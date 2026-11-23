// scripts/verify_google_integrations_browser.js
const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_google_integrations";
const PORT = 9225;
const BASE_URL = "http://127.0.0.1:8899/";
const SCREENSHOT_DIR = path.resolve(__dirname, "..", "AUDIT_SCREENSHOTS");

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
          this.consoleErrors.push(msg.params.exceptionDetails.text || JSON.stringify(msg.params.exceptionDetails));
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

async function runBrowserVerification() {
  console.log("======================================================================");
  console.log("SHAH GROUP AI OS — GOOGLE INTEGRATIONS BROWSER UX VERIFICATION");
  console.log("======================================================================");

  if (fs.existsSync(USER_DATA_DIR)) {
    fs.rmSync(USER_DATA_DIR, { recursive: true, force: true });
  }
  fs.mkdirSync(USER_DATA_DIR, { recursive: true });
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

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

    if (!targets || targets.length === 0) {
      throw new Error("Could not connect to Chrome debugging target on port " + PORT);
    }

    const pageTarget = targets.find((t) => t.type === "page") || targets[0];
    cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await cdp.waitOpen();

    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Console.enable");

    // Set desktop viewport
    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1,
      mobile: false,
    });

    console.log("[NAV] Navigating to " + BASE_URL);
    await cdp.send("Page.navigate", { url: BASE_URL });
    await sleep(2000);

    // Authenticate as owner
    console.log("[AUTH] Logging in as Owner...");
    const loginRes = await cdp.eval(`
      (async () => {
        const r = await fetch("/api/auth/login", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({username: "owner", password: "ShahGroup_Owner_Secured_2026!#"})
        });
        const j = await r.json();
        if(!j.token) return { ok: false, error: j.error };
        state.token = j.token;
        localStorage.setItem("sgai_token", j.token);
        await auth();
        bindNav();
        switchWorkspace("SSC");
        return { ok: true, username: j.user ? j.user.username : 'owner' };
      })()
    `);

    if (!loginRes.ok) {
      throw new Error("Login failed: " + JSON.stringify(loginRes));
    }
    console.log("[AUTH] Successfully logged in as:", loginRes.username);

    // Navigate to Integrations Section
    console.log("[TAB] Activating Integrations Section (#sec-integrations)...");
    await cdp.eval(`
      (async () => {
        showSection("integrations");
        switchIntSub("hub");
        if(typeof loadGoogleAccountStatus === 'function') await loadGoogleAccountStatus();
      })()
    `);
    await sleep(1500);

    // Check Hub Panel
    console.log("[DOM] Checking Connection Hub Subpanel (#int-sub-hub)...");
    const hubCheck = await cdp.eval(`
      (() => {
        const btnDrive = document.getElementById("btn-google-drive-connect");
        const btnSheets = document.getElementById("btn-google-sheets-connect");
        const badgeDrive = document.getElementById("badge-drive-status");
        const badgeSheets = document.getElementById("badge-sheets-status");
        return {
          has_btn_drive: !!btnDrive,
          has_btn_sheets: !!btnSheets,
          badge_drive_text: badgeDrive ? badgeDrive.textContent : "",
          badge_sheets_text: badgeSheets ? badgeSheets.textContent : ""
        };
      })()
    `);
    console.log("[HUB DOM]:", JSON.stringify(hubCheck, null, 2));

    // Capture Desktop Screenshot 1: Connection Hub Overview
    console.log("[SCREENSHOT] Capturing Connection Hub Overview...");
    const shot1 = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const shot1Path = path.join(SCREENSHOT_DIR, "google_integrations_hub.png");
    fs.writeFileSync(shot1Path, Buffer.from(shot1.data, "base64"));
    console.log("[SCREENSHOT] Saved:", shot1Path);

    // Switch to Google Sheets Subpanel
    console.log("[TAB] Switching to Google Sheets Subpanel (switchIntSub('sheets'))...");
    await cdp.eval(`
      (async () => {
        switchIntSub("sheets");
        if(typeof loadSheetsMappings === 'function') await loadSheetsMappings();
        if(typeof loadSheetsHistory === 'function') await loadSheetsHistory();
      })()
    `);
    await sleep(2000);

    const sheetsCheck = await cdp.eval(`
      (() => {
        const inputSp = document.getElementById("input-target-spreadsheet");
        const linkOpen = document.getElementById("link-open-google-sheet");
        const rowsMappings = document.querySelectorAll("#sheets-mapping-tbody tr");
        const rowsHistory = document.querySelectorAll("#sheets-history-tbody tr");
        return {
          has_spreadsheet_input: !!inputSp,
          spreadsheet_input_val: inputSp ? inputSp.value : null,
          has_open_link: !!linkOpen,
          mappings_rows_count: rowsMappings.length,
          history_rows_count: rowsHistory.length
        };
      })()
    `);
    console.log("[SHEETS DOM]:", JSON.stringify(sheetsCheck, null, 2));

    // Capture Desktop Screenshot 2: Google Sheets 12-Module Mapping & Sync History
    console.log("[SCREENSHOT] Capturing Google Sheets Mapping & Sync History...");
    const shot2 = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const shot2Path = path.join(SCREENSHOT_DIR, "google_sheets_sync_history.png");
    fs.writeFileSync(shot2Path, Buffer.from(shot2.data, "base64"));
    console.log("[SCREENSHOT] Saved:", shot2Path);

    // Switch to Google Drive Subpanel
    console.log("[TAB] Switching to Google Drive Subpanel (switchIntSub('drive'))...");
    await cdp.eval(`
      (async () => {
        switchIntSub("drive");
        if(typeof loadDriveFolders === 'function') await loadDriveFolders();
      })()
    `);
    await sleep(2000);

    const driveCheck = await cdp.eval(`
      (() => {
        const driveFolders = document.querySelectorAll("#drive-folders-grid > div");
        const emailLabel = document.getElementById("drive-connected-email");
        return {
          folders_count: driveFolders.length,
          connected_email_label: emailLabel ? emailLabel.textContent : ""
        };
      })()
    `);
    console.log("[DRIVE DOM]:", JSON.stringify(driveCheck, null, 2));

    // Mobile Viewport Check (375x812, deviceScaleFactor 2)
    console.log("[MOBILE] Setting Viewport to Mobile (375x812)...");
    await cdp.send("Emulation.setDeviceMetricsOverride", {
      width: 375,
      height: 812,
      deviceScaleFactor: 2,
      mobile: true,
    });
    await sleep(1000);

    const shot3 = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const shot3Path = path.join(SCREENSHOT_DIR, "google_integrations_mobile.png");
    fs.writeFileSync(shot3Path, Buffer.from(shot3.data, "base64"));
    console.log("[SCREENSHOT] Saved:", shot3Path);

    console.log("======================================================================");
    console.log("CONSOLE ERRORS LOGGED: " + cdp.consoleErrors.length);
    if (cdp.consoleErrors.length > 0) {
      console.warn("Console Errors:", cdp.consoleErrors);
    }
    console.log("======================================================================");

    const allPassed =
      hubCheck.has_btn_drive &&
      hubCheck.has_btn_sheets &&
      sheetsCheck.has_spreadsheet_input &&
      sheetsCheck.mappings_rows_count === 12 &&
      sheetsCheck.has_open_link &&
      driveCheck.folders_count >= 10 &&
      cdp.consoleErrors.length === 0;

    console.log("BROWSER UX VERIFICATION STATUS: " + (allPassed ? "PASSED (100%)" : "FAILED"));
    return allPassed;
  } finally {
    if (chromeProc) {
      chromeProc.kill("SIGKILL");
    }
  }
}

runBrowserVerification()
  .then((ok) => process.exit(ok ? 0 : 1))
  .catch((err) => {
    console.error("FATAL ERROR:", err);
    process.exit(1);
  });
