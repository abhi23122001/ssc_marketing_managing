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
    '--remote-debugging-port=9231',
    '--user-data-dir=C:\\temp\\chrome_inspect_dom',
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--window-size=1600,980',
    'http://127.0.0.1:8899/'
  ]);

  try {
    let targets = null;
    for (let i = 0; i < 20; i++) {
      try {
        targets = await fetchJson('http://127.0.0.1:9231/json/list');
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
    await sleep(2500);

    // Call showSection('ai')
    await send('Runtime.evaluate', { expression: 'showSection("ai")' });
    await sleep(500);

    const info = await send('Runtime.evaluate', {
      expression: `(() => {
        const main = document.querySelector("#main");
        const sec = document.querySelector("#sec-ai");
        return {
          mainRect: main ? main.getBoundingClientRect() : null,
          mainScrollHeight: main ? main.scrollHeight : 0,
          mainScrollTop: main ? main.scrollTop : 0,
          mainChildren: Array.from(main ? main.children : []).map(c => ({
            id: c.id,
            display: c.style.display,
            rect: c.getBoundingClientRect()
          })),
          secRect: sec ? sec.getBoundingClientRect() : null,
          secComputedDisplay: sec ? getComputedStyle(sec).display : null,
          secComputedVisibility: sec ? getComputedStyle(sec).visibility : null,
          secComputedOpacity: sec ? getComputedStyle(sec).opacity : null,
          secParent: sec && sec.parentElement ? sec.parentElement.tagName + "#" + sec.parentElement.id : null,
          bodyScrollHeight: document.body.scrollHeight,
          windowInnerHeight: window.innerHeight,
          windowInnerWidth: window.innerWidth
        };
      })()`,
      returnByValue: true
    });

    console.log('DOM Info:', JSON.stringify(info.result.value, null, 2));

    ws.close();
  } finally {
    p.kill('SIGTERM');
  }
})();
