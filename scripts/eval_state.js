const { spawn } = require('child_process');
const http = require('http');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve(JSON.parse(d)));
    }).on('error', reject);
  });
}

(async () => {
  const p = spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', [
    '--remote-debugging-port=9229',
    '--user-data-dir=C:\\temp\\chrome_diag_eval',
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    'http://127.0.0.1:8899/'
  ]);

  try {
    let targets = null;
    for (let i = 0; i < 20; i++) {
      try {
        targets = await fetchJson('http://127.0.0.1:9229/json/list');
        if (targets && targets.length) break;
      } catch (e) { await sleep(300); }
    }
    const pt = targets.find(t => t.type === 'page') || targets[0];
    const ws = new WebSocket(pt.webSocketDebuggerUrl);
    await new Promise(r => ws.onopen = r);

    let id = 1;
    function send(method, params = {}) {
      return new Promise((res, rej) => {
        const curId = id++;
        const onMsg = (e) => {
          const d = JSON.parse(e.data);
          if (d.id === curId) {
            ws.removeEventListener('message', onMsg);
            if (d.error) rej(d.error); else res(d.result);
          }
        };
        ws.addEventListener('message', onMsg);
        ws.send(JSON.stringify({ id: curId, method, params }));
      });
    }

    await send('Runtime.enable');
    await sleep(2000);

    const evalRes = await send('Runtime.evaluate', {
      expression: 'JSON.stringify({ token: state.token, role: state.role, visibleAi: visible("ai"), secAiDisplay: getComputedStyle(document.querySelector("#sec-ai")).display })',
      returnByValue: true
    });
    console.log('Initial eval:', evalRes.result.value);

    // Call showSection("ai")
    await send('Runtime.evaluate', {
      expression: 'showSection("ai")'
    });
    const afterClick = await send('Runtime.evaluate', {
      expression: 'JSON.stringify({ secAiDisplay: getComputedStyle(document.querySelector("#sec-ai")).display, offsetHeight: document.querySelector("#sec-ai").offsetHeight, innerText: document.querySelector("#sec-ai").innerText.slice(0, 300) })',
      returnByValue: true
    });
    console.log('After showSection("ai"):', afterClick.result.value);

    ws.close();
  } finally {
    p.kill('SIGTERM');
  }
})();
