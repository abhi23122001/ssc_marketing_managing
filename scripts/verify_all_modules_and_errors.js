const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_all_modules";
const PORT = 9232;
const BASE_URL = "http://127.0.0.1:8899/";

function sleep(ms) { return new Promise((r) => setTimeout(r, ms)); }
function fetchJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => resolve(JSON.parse(data)));
    }).on("error", reject);
  });
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.ws = null;
    this.id = 1;
    this.callbacks = new Map();
    this.consoleErrors = [];
    this.exceptions = [];
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
        if (parsed.params.type === "error") {
          this.consoleErrors.push({
            args: parsed.params.args.map((a) => a.value || a.description),
          });
        }
      } else if (parsed.method === "Runtime.exceptionThrown") {
        this.exceptions.push(parsed.params.exceptionDetails);
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
}

async function main() {
  console.log("=== COMPREHENSIVE ALL-MODULES AND ERROR AUDIT ===");

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
    "--window-size=1600,980",
    BASE_URL,
  ]);

  try {
    let pageTarget = null;
    for (let i = 0; i < 20; i++) {
      try {
        const targets = await fetchJson(`http://127.0.0.1:${PORT}/json/list`);
        pageTarget = targets.find((t) => t.type === "page") || targets[0];
        if (pageTarget && pageTarget.webSocketDebuggerUrl) break;
      } catch (e) { await sleep(300); }
    }
    if (!pageTarget) throw new Error("Chrome failed to start on port " + PORT);

    const client = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await client.connect();

    await client.send("Page.enable");
    await client.send("Runtime.enable");

    // Wait for auto-authentication & initial render
    await sleep(2500);

    const modules = [
      "overview",
      "workspaces",
      "projects",
      "finance",
      "employees",
      "marketing",
      "crm",
      "ai",
      "approvals",
      "integrations",
      "settings"
    ];

    const results = [];

    for (const mod of modules) {
      const res = await client.eval(`(() => {
        const btn = document.querySelector('.sidebar .item[data-sec="${mod}"]');
        if (!btn) return { exists: false, module: '${mod}' };
        btn.click();
        const sec = document.querySelector('#sec-${mod}');
        return {
          exists: true,
          module: '${mod}',
          display: sec ? sec.style.display : null,
          computedDisplay: sec ? getComputedStyle(sec).display : null,
          hasContent: sec ? sec.children.length > 0 : false,
          offsetHeight: sec ? sec.offsetHeight : 0
        };
      })()`);
      console.log(`Module [${mod}]:`, res);
      results.push(res);
      await sleep(400);
    }

    // Now test Finance subtabs
    await client.eval(`showSection("finance")`);
    await sleep(400);
    const finSubtabs = ["quotations", "invoices", "salary", "claims", "vendors", "pl", "documents"];
    for (const sub of finSubtabs) {
      const subRes = await client.eval(`(() => {
        const btn = document.querySelector('#subnav-finance button[data-sub="${sub}"]');
        if (!btn) return { exists: false, sub: '${sub}' };
        btn.click();
        const pane = document.querySelector('#sub-fin-${sub}');
        return {
          exists: true,
          sub: '${sub}',
          display: pane ? pane.style.display : null,
          computedDisplay: pane ? getComputedStyle(pane).display : null,
          offsetHeight: pane ? pane.offsetHeight : 0
        };
      })()`);
      console.log(`  Finance subtab [${sub}]:`, subRes);
      await sleep(200);
    }

    // Now test AI Brain subtabs
    await client.eval(`showSection("ai")`);
    await sleep(400);
    const aiSubtabs = ["assistant", "hermes", "research", "briefs", "alerts", "reports", "scheduler", "knowledge", "agents"];
    for (const sub of aiSubtabs) {
      const subRes = await client.eval(`(() => {
        const btn = document.querySelector('#subnav-ai-brain button[data-sub="${sub}"]');
        if (!btn) return { exists: false, sub: '${sub}' };
        btn.click();
        const pane = document.querySelector('#sub-ai-${sub}');
        return {
          exists: true,
          sub: '${sub}',
          display: pane ? pane.style.display : null,
          computedDisplay: pane ? getComputedStyle(pane).display : null,
          offsetHeight: pane ? pane.offsetHeight : 0
        };
      })()`);
      console.log(`  AI subtab [${sub}]:`, subRes);
      await sleep(200);
    }

    // Check errors
    console.log("\n--- ERROR CHECK RESULTS ---");
    console.log(`Console Errors: ${client.consoleErrors.length}`);
    if (client.consoleErrors.length > 0) {
      console.log(JSON.stringify(client.consoleErrors, null, 2));
    }
    console.log(`Uncaught Exceptions: ${client.exceptions.length}`);
    if (client.exceptions.length > 0) {
      console.log(JSON.stringify(client.exceptions, null, 2));
    }

    const allPassed = results.every(r => r.exists && r.computedDisplay === "block" && r.offsetHeight > 0);
    console.log(`\nOverall Module Navigation Verdict: ${allPassed ? "100% PASS" : "FAIL"}`);

    client.ws.close();
  } finally {
    chromeProc.kill("SIGTERM");
  }
}

main().catch(err => {
  console.error("AUDIT FAILED:", err);
  process.exit(1);
});
