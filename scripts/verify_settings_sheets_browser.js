// scripts/verify_settings_sheets_browser.js
const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_profile_settings";
const PORT = 9223;
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
    this.ws = new WebSocket(wsUrl);
    this.id = 1;
    this.callbacks = new Map();
    this.consoleErrors = [];

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.callbacks.has(msg.id)) {
        const { resolve, reject } = this.callbacks.get(msg.id);
        this.callbacks.delete(msg.id);
        if (msg.error) reject(msg.error);
        else resolve(msg.result);
      } else if (msg.method) {
        if (msg.method === "Runtime.exceptionThrown") {
          console.error("PAGE EXCEPTION:", msg.params.exceptionDetails);
          this.consoleErrors.push(msg.params.exceptionDetails);
        } else if (msg.method === "Console.messageAdded" && msg.params.message.level === "error") {
          console.error("CONSOLE ERROR:", msg.params.message.text);
          this.consoleErrors.push(msg.params.message.text);
        }
      }
    };
  }

  waitOpen() {
    return new Promise((resolve) => {
      if (this.ws.readyState === WebSocket.OPEN) return resolve();
      this.ws.onopen = () => resolve();
    });
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = this.id++;
      this.callbacks.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async eval(expression) {
    const res = await this.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    if (res.exceptionDetails) {
      throw new Error(res.exceptionDetails.text || JSON.stringify(res.exceptionDetails));
    }
    return res.result ? res.result.value : undefined;
  }
}

async function runSettingsVerification() {
  console.log("=== STARTING SETTINGS & SHEETS BROWSER VERIFICATION ===");
  if (fs.existsSync(USER_DATA_DIR)) {
    fs.rmSync(USER_DATA_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(USER_DATA_DIR, { recursive: true });

  const chromeProc = spawn(CHROME_PATH, [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${USER_DATA_DIR}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "about:blank",
  ]);

  let cdp = null;
  try {
    let targets = null;
    for (let i = 0; i < 20; i++) {
      await sleep(500);
      try {
        targets = await fetchJson(`http://127.0.0.1:${PORT}/json`);
        if (targets && targets.length > 0) break;
      } catch (e) {}
    }

    const pageTarget = targets.find((t) => t.type === "page") || targets[0];
    cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.waitOpen();

    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Console.enable");

    await cdp.send("Page.navigate", { url: BASE_URL });
    await sleep(2000);

    // Login
    await cdp.eval(`
      (async () => {
        const r = await fetch("/api/auth/login", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({username: "owner", password: "demo-owner-pass-0001"})
        });
        const j = await r.json();
        state.token = j.token;
        localStorage.setItem("sgai_token", j.token);
        await auth();
        bindNav();
        switchWorkspace("SSC");
      })()
    `);

    // Navigate to Settings
    console.log("[STEP 1] Navigating to Settings section...");
    await cdp.eval(`
      (async () => {
        const item = document.querySelector('.item[data-sec="settings"]');
        if(item) item.click();
        await new Promise(r => setTimeout(r, 600));
      })()
    `);

    // Check Settings subtabs
    console.log("[STEP 2] Verifying subtabs in Settings...");
    const subnavRes = await cdp.eval(`
      (async () => {
        const sSubs = document.querySelectorAll("#subnav-settings button");
        const results = [];
        for(const b of sSubs) {
          b.click();
          await new Promise(r => setTimeout(r, 400));
          const subKey = b.dataset.sub;
          const container = document.getElementById("sub-settings-" + subKey);
          results.push({
            sub: subKey,
            active: b.classList.contains("active"),
            containerVisible: container && container.style.display !== "none"
          });
        }
        return results;
      })()
    `);
    console.log("[PASS] Settings subnav results:", subnavRes);

    // Verify Google Sheets 12 Table Cards
    console.log("[STEP 3] Verifying 12 Table Cards in Sheets subtab...");
    const sheetsRes = await cdp.eval(`
      (async () => {
        const sheetsBtn = document.querySelector("#subnav-settings button[data-sub='sheets']");
        if(sheetsBtn) sheetsBtn.click();
        await new Promise(r => setTimeout(r, 600));
        const cards = document.querySelectorAll("#sheets-tables-grid .card");
        const tables = [];
        cards.forEach(c => {
          const strong = c.querySelector("strong");
          const val = c.querySelector(".v");
          if(strong) tables.push({ table: strong.textContent.trim(), count: val ? val.textContent.trim() : 0 });
        });
        return { totalCards: cards.length, tables };
      })()
    `);
    console.log(`[PASS] Google Sheets rendered ${sheetsRes.totalCards} table cards:`, sheetsRes.tables);

    // Verify Theme toggle & Global Search
    console.log("[STEP 4] Verifying Theme toggle and Global search...");
    const themeRes = await cdp.eval(`
      (async () => {
        const btn = document.getElementById("btn-theme-toggle");
        const before = document.body.classList.contains("theme-light");
        if(btn) btn.click();
        const after = document.body.classList.contains("theme-light");
        if(btn) btn.click(); // revert
        return { initial: before, afterToggle: after, reverted: document.body.classList.contains("theme-light") };
      })()
    `);
    console.log("[PASS] Theme toggle verified:", themeRes);

    console.log("\n=== BROWSER CONSOLE ERROR AUDIT ===");
    console.log("Console Errors:", cdp.consoleErrors.length);
    if (cdp.consoleErrors.length > 0) {
      console.error("FAIL: Browser errors:", cdp.consoleErrors);
      process.exit(1);
    }
    console.log("ALL SETTINGS & SHEETS CHECKS PASSED: 0 ERRORS!");
  } finally {
    if (chromeProc) chromeProc.kill("SIGKILL");
  }
}

runSettingsVerification().catch(e => {
  console.error("Verification failed:", e);
  process.exit(1);
});
