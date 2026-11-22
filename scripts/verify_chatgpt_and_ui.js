const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_chatgpt";
const PORT = 9230;
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
  console.log("=== STARTING CHATGPT-STYLE AI BRAIN & UI VERIFICATION ===");

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
      } catch (e) {
        await sleep(300);
      }
    }
    if (!pageTarget) throw new Error("Chrome failed to start on port " + PORT);

    const client = new CDPClient(pageTarget.webSocketDebuggerUrl);
    await client.connect();

    await client.send("Page.enable");
    await client.send("Runtime.enable");

    // Wait for auto-authentication & initial render
    await sleep(2500);

    const shotDir = path.resolve(__dirname, "..", "AUDIT_SCREENSHOTS");

    // 1. Initial Overview Screenshot (Dark)
    await client.captureScreenshot(path.join(shotDir, "v2_01_restored_overview_dark.png"));
    console.log("[PASS] Captured Dark Overview Screenshot");

    // 2. Test Light Theme Toggle
    await client.eval(`setAppTheme("light");`);
    await sleep(500);
    await client.captureScreenshot(path.join(shotDir, "v2_02_restored_overview_light.png"));
    console.log("[PASS] Captured Light Overview Screenshot");

    // Switch back to Dark Theme
    await client.eval(`setAppTheme("dark");`);
    await sleep(300);

    // 3. Navigate to AI Brain Section
    console.log("Navigating to AI Brain section...");
    const navResult = await client.eval(`(() => {
      const aiBtn = document.querySelector('.sidebar .item[data-sec="ai"]');
      if (aiBtn) {
        aiBtn.click();
        return { clicked: true, secVisible: document.querySelector('#sec-ai').style.display };
      }
      return { clicked: false };
    })()`);
    console.log("Nav Result:", navResult);
    await sleep(1000);

    // 4. Capture ChatGPT Welcome Screen
    await client.captureScreenshot(path.join(shotDir, "v2_03_chatgpt_welcome_screen.png"));
    console.log("[PASS] Captured ChatGPT Welcome Screen");

    // 5. Test Quick Prompt Trigger (Click prompt card)
    console.log("Clicking quick prompt card for P&L Status...");
    const promptClickResult = await client.eval(`(() => {
      const card = document.querySelector('.chatgpt-prompt-card');
      if (card) {
        card.click();
        return { clicked: true, text: card.innerText };
      }
      return { clicked: false };
    })()`);
    console.log("Prompt Click Result:", promptClickResult);

    // Wait for AI response to arrive and render
    await sleep(3000);

    // 6. Capture ChatGPT Conversation Response
    await client.captureScreenshot(path.join(shotDir, "v2_04_chatgpt_conversation_response.png"));
    console.log("[PASS] Captured ChatGPT Conversation Response");

    // 7. Verify Message Stream and State
    const chatState = await client.eval(`(() => {
      const msgs = document.querySelectorAll('.chatgpt-msg-row');
      const sessions = document.querySelectorAll('.chatgpt-history-item');
      return {
        messagesCount: msgs.length,
        sessionsCount: sessions.length,
        hasAssistantMessage: !!document.querySelector('.chatgpt-msg-row.assistant'),
        hasTaskButton: !!document.querySelector('.chatgpt-msg-actions button'),
        lastResponseSnippet: document.querySelector('.chatgpt-msg-row.assistant .chatgpt-msg-content') ? document.querySelector('.chatgpt-msg-row.assistant .chatgpt-msg-content').innerText.slice(0, 300) : null
      };
    })()`);
    console.log("Chat State:", chatState);

    // 8. Test Light Theme in ChatGPT Interface
    await client.eval(`setAppTheme("light");`);
    await sleep(500);
    await client.captureScreenshot(path.join(shotDir, "v2_05_chatgpt_light_theme.png"));
    console.log("[PASS] Captured ChatGPT Light Theme Screenshot");

    // Switch back to Dark Theme
    await client.eval(`setAppTheme("dark");`);
    await sleep(300);

    // 9. Check console errors
    console.log("Console Errors Count:", client.consoleErrors.length);
    if (client.consoleErrors.length > 0) {
      console.warn("Console Errors detected:", JSON.stringify(client.consoleErrors, null, 2));
    } else {
      console.log("[PASS] 0 Console Errors encountered throughout execution!");
    }

    client.ws.close();
  } finally {
    chromeProc.kill("SIGTERM");
  }
}

main().catch((err) => {
  console.error("VERIFICATION FAILED:", err);
  process.exit(1);
});
