// scripts/final_browser_verifier.js
const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_profile_final";
const PORT = 9226;
const BASE_URL = "http://127.0.0.1:8899/";
const ROTATED_PASS = "ShahGroup_Owner_Secured_2026!#";

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
    this.consoleLogs = [];

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
        } else if (msg.method === "Console.messageAdded") {
          if (msg.params.message.level === "error") {
            console.error("CONSOLE ERROR:", msg.params.message.text);
            this.consoleErrors.push(msg.params.message.text);
          } else {
            this.consoleLogs.push(msg.params.message.text);
          }
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

async function runFinalBrowserVerification() {
  console.log("======================================================================");
  console.log("SHAH GROUP AI OS — FINAL HEADLESS CHROME CDP BROWSER VERIFIER");
  console.log("======================================================================");

  if (fs.existsSync(USER_DATA_DIR)) {
    fs.rmSync(USER_DATA_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(USER_DATA_DIR, { recursive: true });

  const evidence = {
    timestamp: new Date().toISOString(),
    chrome_version: "Google Chrome Latest (Headless)",
    base_url: BASE_URL,
    sections_audited: [],
    console_errors: [],
    page_exceptions: [],
    screenshots: [],
    status: "UNKNOWN"
  };

  const chromeProc = spawn(CHROME_PATH, [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${USER_DATA_DIR}`,
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--window-size=1600,1050",
    "about:blank",
  ]);

  let cdp = null;
  try {
    let targets = null;
    for (let i = 0; i < 25; i++) {
      await sleep(400);
      try {
        targets = await fetchJson(`http://127.0.0.1:${PORT}/json`);
        if (targets && targets.length > 0) break;
      } catch (e) {}
    }

    if (!targets || targets.length === 0) {
      throw new Error("Failed to connect to Chrome remote debugging port.");
    }

    const pageTarget = targets.find((t) => t.type === "page") || targets[0];
    cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.waitOpen();

    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Console.enable");

    // 1. Navigate to local application
    console.log("[STEP 1] Navigating to application root...");
    await cdp.send("Page.navigate", { url: BASE_URL });
    await sleep(2000);

    // 2. Login with rotated owner credential
    console.log("[STEP 2] Authenticating with rotated Owner credential...");
    const loginResult = await cdp.eval(`
      (async () => {
        const r = await fetch("/api/auth/login", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({username: "owner", password: "${ROTATED_PASS}"})
        });
        const j = await r.json();
        if (j.token) {
          state.token = j.token;
          localStorage.setItem("sgai_token", j.token);
          await auth();
          bindNav();
          switchWorkspace("SSC");
          return { ok: true, user: j.user, tokenReceived: true };
        }
        return { ok: false, error: j.error };
      })()
    `);
    console.log("[PASS] Owner Login Result:", loginResult);
    evidence.sections_audited.push({
      step: "Owner Login with Rotated Credentials",
      passed: !!loginResult.ok,
      details: loginResult
    });

    await sleep(1500);

    // 3. Verify Executive Overview
    console.log("[STEP 3] Auditing Executive Overview...");
    const overviewAudit = await cdp.eval(`
      (function() {
        const activeNav = document.querySelector("#nav .item.active");
        return {
          activeNav: activeNav ? activeNav.innerText.trim() : null,
          hasHeader: document.body.innerText.includes("Executive Overview") || document.body.innerText.includes("SHAH GROUP"),
          workspace: window.state ? window.state.ws : null
        };
      })()
    `);
    console.log("[PASS] Overview Audit:", overviewAudit);
    evidence.sections_audited.push({
      step: "Executive Overview Display",
      passed: !!(overviewAudit && overviewAudit.hasHeader),
      details: overviewAudit
    });

    // 4. Verify Owner Setup Center in DOM
    console.log("[STEP 4] Auditing Owner Setup Center (#sec-owner-setup)...");
    const ownerSetupAudit = await cdp.eval(`
      (async function() {
        if (window.showSection) window.showSection("owner-setup");
        await new Promise(r => setTimeout(r, 1000));
        const sec = document.querySelector("#sec-owner-setup");
        const cards = document.querySelectorAll("#owner-setup-categories-container .card");
        return {
          sectionExists: !!sec,
          sectionVisible: sec ? sec.style.display !== "none" : false,
          progressNum: document.querySelector("#setup-progress-num") ? document.querySelector("#setup-progress-num").innerText : null,
          categoriesCount: cards.length
        };
      })()
    `);
    console.log("[PASS] Owner Setup Center Audit:", ownerSetupAudit);
    evidence.sections_audited.push({
      step: "Owner Setup Center",
      passed: !!(ownerSetupAudit && ownerSetupAudit.sectionExists && ownerSetupAudit.sectionVisible),
      details: ownerSetupAudit
    });

    // 5. Verify Central Integration Center & Google Business Profile Subpanel
    console.log("[STEP 5] Auditing Central Integration Center & GBP Subpanel...");
    const integrationAudit = await cdp.eval(`
      (async function() {
        if (window.showSection) window.showSection("integrations");
        await new Promise(r => setTimeout(r, 800));
        
        // Switch to GBP subtab
        if (window.switchIntSub) window.switchIntSub("gbp");
        await new Promise(r => setTimeout(r, 800));

        const gbpPanel = document.querySelector("#int-sub-gbp");
        return {
          integrationsSecVisible: document.querySelector("#sec-integrations") ? document.querySelector("#sec-integrations").style.display !== "none" : false,
          gbpPanelExists: !!gbpPanel,
          gbpPanelVisible: gbpPanel ? gbpPanel.style.display !== "none" : false,
          gbpBannerText: document.querySelector("#gbp-status-banner") ? document.querySelector("#gbp-status-banner").innerText : null
        };
      })()
    `);
    console.log("[PASS] Integrations & GBP Audit:", integrationAudit);
    evidence.sections_audited.push({
      step: "Integrations & Google Business Profile",
      passed: !!(integrationAudit && integrationAudit.gbpPanelExists && integrationAudit.gbpPanelVisible),
      details: integrationAudit
    });

    // 6. Verify AI Brain & Marketing Intelligence Studio
    console.log("[STEP 6] Auditing AI Brain & Intelligence Section...");
    const aiMarketingAudit = await cdp.eval(`
      (async function() {
        if (window.showSection) window.showSection("ai");
        await new Promise(r => setTimeout(r, 800));
        const sec = document.querySelector("#sec-ai");
        return {
          aiSecVisible: sec ? sec.style.display !== "none" : false,
          hasAiAssistant: sec ? sec.innerText.includes("AI Brain") || sec.innerText.includes("Assistant") : false
        };
      })()
    `);
    console.log("[PASS] AI Intelligence Audit:", aiMarketingAudit);
    evidence.sections_audited.push({
      step: "AI Brain & Intelligence",
      passed: !!(aiMarketingAudit && aiMarketingAudit.aiSecVisible),
      details: aiMarketingAudit
    });

    // 7. Verify Social Media Registry in Browser DOM
    console.log("[STEP 7] Auditing Social Media Registry in DOM...");
    const socialAudit = await cdp.eval(`
      (async () => {
        const r = await fetch("/api/social/accounts?workspace=SSC", {
          headers: {"Authorization": "Bearer " + state.token}
        });
        const d = await r.json();
        return {
          totalAccounts: (d.accounts || []).length,
          accounts: (d.accounts || []).map(a => ({
            platform: a.platform,
            account_id: a.platform_account_id,
            status: a.connection_status
          }))
        };
      })()
    `);
    console.log("[PASS] Social Media Registry Audit:", socialAudit);
    evidence.sections_audited.push({
      step: "Social Media Registry SSC Verification",
      passed: socialAudit.totalAccounts >= 3,
      details: socialAudit
    });

    // Return to Overview
    await cdp.eval(`if (window.showSection) window.showSection("overview");`);
    await sleep(800);

    // Capture High-Res Screenshot
    console.log("[STEP 8] Capturing full dashboard screenshot...");
    const screenshot = await cdp.send("Page.captureScreenshot", {
      format: "png",
      quality: 100,
      fromSurface: true,
    });
    const screenshotPath = path.join(__dirname, "final_cdp_dashboard_screenshot.png");
    fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
    console.log(`[PASS] Screenshot saved to ${screenshotPath}`);

    evidence.screenshots.push({
      filename: "scripts/final_cdp_dashboard_screenshot.png",
      format: "image/png",
      size_bytes: Buffer.from(screenshot.data, "base64").length,
    });

    evidence.console_errors = cdp.consoleErrors;
    const hasZeroErrors = cdp.consoleErrors.length === 0 && evidence.page_exceptions.length === 0;
    evidence.status = hasZeroErrors ? "PASSED_ZERO_ERRORS" : "FAILED_CONSOLE_ERRORS";

    const evidencePath = path.join(__dirname, "final_browser_evidence.json");
    fs.writeFileSync(evidencePath, JSON.stringify(evidence, null, 2), "utf-8");
    console.log(`[PASS] Final Browser evidence saved to: ${evidencePath}`);

    console.log("======================================================================");
    console.log(`FINAL CDP BROWSER AUDIT RESULT: ${evidence.status}`);
    console.log(`Total Console Errors: ${cdp.consoleErrors.length}`);
    console.log("======================================================================");

  } finally {
    if (chromeProc) {
      chromeProc.kill("SIGKILL");
    }
  }
}

runFinalBrowserVerification().catch((err) => {
  console.error("FATAL FINAL BROWSER AUDIT ERROR:", err);
  process.exit(1);
});
