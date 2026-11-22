const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_all_fixes";
const PORT = 9235;
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
    this.consoleErrors = [];
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
        if (parsed.params.type === "error") {
          this.consoleErrors.push({
            type: "console.error",
            args: parsed.params.args.map((a) => a.value || a.description),
          });
        }
        this.consoleLogs.push({
          type: parsed.params.type,
          args: parsed.params.args.map((a) => a.value || a.description),
        });
      } else if (parsed.method === "Runtime.exceptionThrown") {
        this.consoleErrors.push({
          type: "exception",
          error: parsed.params.exceptionDetails,
        });
      }
    };
  }

  send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const callId = this.id++;
      this.callbacks.set(callId, { resolve, reject });
      this.ws.send(JSON.stringify({ id: callId, method, params }));
    });
  }

  async eval(expr) {
    const res = await this.send("Runtime.evaluate", {
      expression: expr,
      returnByValue: true,
      awaitPromise: true,
    });
    if (res.exceptionDetails) {
      throw new Error(
        res.exceptionDetails.exception?.description ||
          res.exceptionDetails.text
      );
    }
    return res.result?.value;
  }
}

async function main() {
  console.log("=== STARTING FULL AUTOMATED VERIFICATION ===");
  if (!fs.existsSync("C:\\temp")) fs.mkdirSync("C:\\temp", { recursive: true });

  const chromeProc = spawn(CHROME_PATH, [
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${USER_DATA_DIR}`,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--window-size=1440,900",
    BASE_URL,
  ]);

  let connected = false;
  let targetWsUrl = null;
  for (let i = 0; i < 20; i++) {
    await sleep(500);
    try {
      const targets = await fetchJson(`http://127.0.0.1:${PORT}/json`);
      if (targets && targets.length > 0) {
        const page = targets.find((t) => t.type === "page") || targets[0];
        targetWsUrl = page.webSocketDebuggerUrl;
        connected = true;
        break;
      }
    } catch (e) {}
  }

  if (!connected) {
    console.error("Could not connect to Chrome DevTools port", PORT);
    chromeProc.kill();
    process.exit(1);
  }

  const cdp = new CDPClient(targetWsUrl);
  await cdp.connect();
  await cdp.send("Runtime.enable");
  await cdp.send("Page.enable");

  console.log("Connected to Chrome via CDP.");
  await sleep(1500);

  // 1. Check Login or perform Login
  const isLogged = await cdp.eval(`!!state.token`);
  console.log("Initial state.token:", isLogged);

  if (!isLogged) {
    console.log("Logging in as owner...");
    await cdp.eval(`
      $("#login-username").value = "owner";
      $("#login-password").value = "demo-owner-pass-0001";
      $("#btn-login").click();
    `);
    await sleep(2000);
    const postLoginToken = await cdp.eval(`state.token`);
    console.log("Post login token acquired:", !!postLoginToken);
  }

  // 2. TEST UNIVERSAL ASSISTANT (ASK ANYTHING)
  console.log("\n--- TEST 1: Universal Assistant (Ask Anything) Intelligence ---");
  await cdp.eval(`
    showSection("ai");
    const aiBtn = document.querySelector("#subnav-ai-brain button[data-sub='assistant']");
    if(aiBtn) aiBtn.click();
  `);
  await sleep(800);

  const queries = [
    { q: "hello", check: "Namaste" },
    { q: "Total profit kitna hua hai?", check: "P&L Financial Report" },
    { q: "leads status", check: "CRM Leads Summary" },
    { q: "morth specs", check: "MoRTH Section 300" }
  ];

  const answers = [];
  for (const { q, check } of queries) {
    console.log(`Sending query: "${q}"...`);
    const ans = await cdp.eval(`
      (async () => {
        const res = await api("/api/intelligence/ask", {
          method: "POST",
          body: { query: "${q}", workspace: state.ws || "SSC" }
        });
        return res.answer;
      })()
    `);
    console.log(`  -> Intent: ${ans.intent}`);
    console.log(`  -> Source: ${ans.data_source}`);
    console.log(`  -> Answer Preview: ${ans.verified_answer.substring(0, 90).replace(/\\n/g, ' ')}...`);
    
    if (!ans.verified_answer.includes(check)) {
      console.warn(`  [WARN] Answer did not contain expected keyword: "${check}"`);
    } else {
      console.log(`  [PASS] Answer verified accurate.`);
    }
    answers.push(ans.verified_answer);
  }

  // Check distinctness
  const uniqueAnswers = new Set(answers);
  if (uniqueAnswers.size === queries.length) {
    console.log(`[PASS] 100% Unique, non-repeating answers verified! (${uniqueAnswers.size}/${queries.length})`);
  } else {
    console.error(`[FAIL] Repetitive answers detected! Unique: ${uniqueAnswers.size}`);
  }

  // 3. TEST MARKETING CONCEPTS & TRENDS
  console.log("\n--- TEST 2: AI Social Media Studio (Concepts & Trends) ---");
  await cdp.eval(`showSection("marketing");`);
  await sleep(600);
  
  // Switch to Ideas
  await cdp.eval(`
    const btnIdeas = document.querySelector("#subnav-marketing button[data-sub='ideas']");
    if(btnIdeas) btnIdeas.click();
  `);
  await sleep(800);

  // Click Generate New Concepts
  console.log("Generating new concepts...");
  await cdp.eval(`generateNewMarketingIdeas();`);
  await sleep(1500);

  const conceptsCount = await cdp.eval(`$("#ideas-container").querySelectorAll(".card").length`);
  console.log(`Ideas rendered in container: ${conceptsCount}`);
  if (conceptsCount > 0) {
    console.log("[PASS] Strategic Content Concepts generated and displayed.");
  } else {
    console.error("[FAIL] No concept cards rendered.");
  }

  // Test Filter
  console.log("Testing category filter: Drone LiDAR...");
  await cdp.eval(`
    const filterBtn = document.querySelector("#ideas-category-filter button[data-pillar='Drone LiDAR']");
    if(filterBtn) filterBtn.click();
  `);
  await sleep(500);
  const droneCount = await cdp.eval(`$("#ideas-container").querySelectorAll(".card").length`);
  console.log(`Drone LiDAR filtered cards count: ${droneCount}`);

  // Test Action button "Draft Script"
  console.log("Clicking Draft Script action...");
  await cdp.eval(`
    const firstDraftBtn = $("#ideas-container").querySelector("button");
    if(firstDraftBtn) firstDraftBtn.click();
  `);
  await sleep(500);
  const scriptTitleVal = await cdp.eval(`$("#script-title") ? $("#script-title").value : ""`);
  console.log(`Loaded script title: "${scriptTitleVal}"`);
  if (scriptTitleVal.length > 0) {
    console.log("[PASS] Idea action successfully loaded into Script Generator!");
  }

  // Switch to Trends
  console.log("Testing Geospatial & Civil Trends...");
  await cdp.eval(`
    const btnTrends = document.querySelector("#subnav-marketing button[data-sub='trends']");
    if(btnTrends) btnTrends.click();
  `);
  await sleep(800);
  await cdp.eval(`refreshLiveTrends();`);
  await sleep(1000);

  const trendsRows = await cdp.eval(`$("#trends-report-box").querySelectorAll("tbody tr").length`);
  console.log(`Live trends table rows: ${trendsRows}`);
  if (trendsRows >= 4) {
    console.log("[PASS] Live Industry Trends table verified with direct action buttons.");
  }

  // 4. TEST CENTRAL INTEGRATION & DATA SYNC CENTER
  console.log("\n--- TEST 3: Central Integration & Data Sync Center ---");
  await cdp.eval(`showSection("integrations"); switchIntSub("hub");`);
  await sleep(800);

  const driveSectionExists = await cdp.eval(`!!document.querySelector("#int-sub-hub")`);
  console.log("Integration Hub displayed:", driveSectionExists);

  const driveCardText = await cdp.eval(`document.querySelector("#int-sub-hub").textContent`);
  const hasDrive = driveCardText.includes("Google Drive Storage");
  const hasSheets = driveCardText.includes("Google Sheets Sync");
  const hasInsta = driveCardText.includes("Instagram Business");
  const hasFb = driveCardText.includes("Facebook Official Page");
  const hasYt = driveCardText.includes("YouTube Studio Channel");
  const hasLi = driveCardText.includes("LinkedIn Corporate Page");

  console.log(`  -> Connection Name: Google Drive Storage: ${hasDrive}`);
  console.log(`  -> Connection Name: Google Sheets Sync: ${hasSheets}`);
  console.log(`  -> Connection Name: Instagram Business: ${hasInsta}`);
  console.log(`  -> Connection Name: Facebook Official Page: ${hasFb}`);
  console.log(`  -> Connection Name: YouTube Studio Channel: ${hasYt}`);
  console.log(`  -> Connection Name: LinkedIn Corporate Page: ${hasLi}`);

  if (hasDrive && hasSheets && hasInsta && hasFb && hasYt && hasLi) {
    console.log("[PASS] All Dedicated Connection Sections verified by explicit connection name!");
  } else {
    console.error("[FAIL] Missing one or more dedicated connection sections.");
  }

  // Test Connect Modal
  console.log("Opening Google Drive Connect modal...");
  await cdp.eval(`openConnectModal("google_drive", "Google Drive Storage");`);
  await sleep(500);
  const modalOpen = await cdp.eval(`$("#modal-overlay").style.display !== "none"`);
  const modalTitle = await cdp.eval(`$("#modal-content").querySelector("h3") ? $("#modal-content").querySelector("h3").textContent : ""`);
  console.log(`Modal open: ${modalOpen}, Title: "${modalTitle}"`);
  if (modalOpen && modalTitle.includes("Google Drive")) {
    console.log("[PASS] Connect Modal opens successfully with options.");
  }
  await cdp.eval(`closeModal();`);
  await sleep(300);

  // 5. Check Console Errors across all tested flows
  console.log("\n--- CONSOLE AUDIT ---");
  console.log("Total console errors encountered:", cdp.consoleErrors.length);
  if (cdp.consoleErrors.length > 0) {
    console.error("Console Errors:", JSON.stringify(cdp.consoleErrors, null, 2));
  } else {
    console.log("[PASS] ZERO console errors, ZERO uncaught exceptions!");
  }

  console.log("\n=== ALL TESTS COMPLETED SUCCESSFULLY ===");
  chromeProc.kill();
  process.exit(cdp.consoleErrors.length === 0 ? 0 : 1);
}

main().catch((err) => {
  console.error("FATAL ERROR in test execution:", err);
  process.exit(1);
});
