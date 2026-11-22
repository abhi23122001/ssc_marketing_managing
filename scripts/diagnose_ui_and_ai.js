const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_diag_ui";
const PORT = 9228;
const BASE_URL = "http://127.0.0.1:8899/";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on("error", reject);
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 1;
    this.callbacks = new Map();
    this.events = [];
    this.consoleLogs = [];
  }

  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.onopen = resolve;
      this.ws.onerror = reject;
    });

    this.ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      if (parsed.id && this.callbacks.has(parsed.id)) {
        const { resolve, reject } = this.callbacks.get(parsed.id);
        this.callbacks.delete(parsed.id);
        if (parsed.error) reject(parsed.error);
        else resolve(parsed.result);
      } else if (parsed.method === "Runtime.consoleAPICalled") {
        this.consoleLogs.push({
          type: parsed.params.type,
          args: parsed.params.args.map((a) => a.value || a.description),
        });
      } else if (parsed.method === "Runtime.exceptionThrown") {
        this.consoleLogs.push({
          type: "exception",
          error: parsed.params.exceptionDetails,
        });
      }
    };
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expr) {
    const res = await this.send("Runtime.evaluate", {
      expression: expr,
      returnByValue: true,
      awaitPromise: true,
    });
    if (res.exceptionDetails) {
      throw new Error(JSON.stringify(res.exceptionDetails));
    }
    return res.result ? res.result.value : undefined;
  }

  async captureScreenshot(filepath) {
    const res = await this.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(filepath, Buffer.from(res.data, "base64"));
    console.log(`Saved screenshot: ${filepath}`);
  }
}

async function main() {
  console.log("=== STARTING UI & AI BRAIN DIAGNOSTIC AUDIT ===");

  if (!fs.existsSync(USER_DATA_DIR)) {
    fs.mkdirSync(USER_DATA_DIR, { recursive: true });
  }

  const chromeProc = spawn(CHROME_PATH, [
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${USER_DATA_DIR}`,
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=1440,900",
    BASE_URL,
  ]);

  try {
    let pageTarget = null;
    for (let i = 0; i < 20; i++) {
      try {
        const targets = await fetchJson(`http://127.0.0.1:${PORT}/json/list`);
        pageTarget = targets.find((t) => t.type === "page") || targets[0];
        if (pageTarget && pageTarget.webSocketDebuggerUrl) break;
      } catch (e) {
        await sleep(300);
      }
    }
    if (!pageTarget) throw new Error("Chrome failed to start on port " + PORT);

    const client = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await client.connect();

    await client.send("Page.enable");
    await client.send("Runtime.enable");

    await sleep(2500);

    const shotDir = path.resolve(__dirname, "..", "AUDIT_SCREENSHOTS");

    // 1. Initial overview screenshot
    await client.captureScreenshot(path.join(shotDir, "diag_01_initial_overview.png"));

    // Check console logs
    console.log("Console logs so far:", JSON.stringify(client.consoleLogs, null, 2));

    // Inspect user, theme, and DOM state
    const pageState = await client.eval(`({
      theme: document.body.className,
      token: window.state ? window.state.token : null,
      user: window.state ? window.state.user : null,
      visibleSection: Array.from(document.querySelectorAll('.main > section')).filter(s => s.style.display !== 'none').map(s => s.id),
      headerH: document.querySelector('header.top') ? document.querySelector('header.top').offsetHeight : 0,
      sidebarW: document.querySelector('.sidebar') ? document.querySelector('.sidebar').offsetWidth : 0,
      mainH: document.querySelector('.main') ? document.querySelector('.main').offsetHeight : 0,
      bodyBg: getComputedStyle(document.body).backgroundColor,
      bodyColor: getComputedStyle(document.body).color
    })`);
    console.log("Page State:", pageState);

    // 2. Click on AI Brain section in sidebar
    console.log("Navigating to AI Brain section...");
    const navResult = await client.eval(`(() => {
      const aiBtn = document.querySelector('.sidebar .item[data-sec="ai"]');
      if (aiBtn) {
        aiBtn.click();
        return { clicked: true, secId: 'ai' };
      }
      return { clicked: false };
    })()`);
    console.log("Nav Result:", navResult);
    await sleep(1500);

    // Capture AI section screenshot
    await client.captureScreenshot(path.join(shotDir, "diag_02_ai_brain_section.png"));

    // Inspect AI section HTML & subtabs
    const aiState = await client.eval(`(() => {
      const sec = document.querySelector('#sec-ai');
      if (!sec) return { exists: false };
      const subtabs = Array.from(sec.querySelectorAll('.chips .c, [data-sub]')).map(b => ({
        text: b.innerText.trim(),
        sub: b.getAttribute('data-sub'),
        active: b.classList.contains('active')
      }));
      const subSections = Array.from(sec.querySelectorAll('[id^="sub-ai"]')).map(s => ({
        id: s.id,
        display: s.style.display
      }));
      return {
        exists: true,
        display: sec.style.display,
        subtabs,
        subSections,
        innerHTMLSnippet: sec.innerHTML.slice(0, 1500)
      };
    })()`);
    console.log("AI State:", JSON.stringify(aiState, null, 2));

    client.ws.close();
  } finally {
    chromeProc.kill("SIGTERM");
  }
}

main().catch(err => {
  console.error("DIAGNOSTIC ERROR:", err);
  process.exit(1);
});
