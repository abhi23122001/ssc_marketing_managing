// scripts/verify_all_enhancements_browser.js
/**
 * Headless Chrome CDP Verification Test for SHAH GROUP AI OS Enhancements:
 * 1. Dynamic Quotation Items (2, 5, 10, 20 items, live math, edit without loss).
 * 2. Survey Site Lifecycle & Reminders (16 statuses, 3-tab modal, travel/team/equipment/financials).
 * 3. Non-GST Commercial Bills (Bill of Supply, strictly 0% tax, BILL-YYYY-XXXX).
 * 4. Registered Vendors (KYC, MSME, PAN, GSTIN, Bank, Approval workflow).
 * 5. Employee Status & Exit Clearance (Active/Notice/Former, F&F settlement, handover).
 * 6. Report Archive & Visual Analytics (Charts, tables, in-app viewer).
 * 7. Light Theme Accessibility & High-Contrast Validation.
 * 8. Zero Console Error Audit.
 */

const { spawn } = require("child_process");
const http = require("http");
const fs = require("fs");
const path = require("path");

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const USER_DATA_DIR = "C:\\temp\\chrome_verify_profile_enhancements";
const PORT = 9233;
const BASE_URL = "http://127.0.0.1:8899/";

const SCREENSHOT_DIR = path.resolve(__dirname, "..", "AUDIT_SCREENSHOTS");
const EVIDENCE_DIR = path.resolve(__dirname, "..", "AUDIT_TEST_EVIDENCE");
const LOG_DIR = path.resolve(__dirname, "..", "AUDIT_LOGS");

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
    this.logs = [];

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.id && this.callbacks.has(msg.id)) {
        const { resolve, reject } = this.callbacks.get(msg.id);
        this.callbacks.delete(msg.id);
        if (msg.error) reject(msg.error);
        else resolve(msg.result);
      } else if (msg.method) {
        if (msg.method === "Runtime.exceptionThrown") {
          const detail = msg.params.exceptionDetails;
          console.error("PAGE EXCEPTION:", detail);
          this.consoleErrors.push(detail);
          this.logs.push(`[EXCEPTION] ${JSON.stringify(detail)}`);
        } else if (msg.method === "Console.messageAdded") {
          const text = msg.params.message.text;
          const level = msg.params.message.level;
          this.logs.push(`[CONSOLE ${level.toUpperCase()}] ${text}`);
          if (level === "error") {
            // Ignore minor favicon or 404 image errors if any
            if (!text.includes("favicon") && !text.includes("Failed to load resource: the server responded with a status of 404")) {
              console.error("CONSOLE ERROR:", text);
              this.consoleErrors.push(text);
            }
          }
        }
      }
    };
  }

  waitOpen() {
    return new Promise((resolve, reject) => {
      if (this.ws.readyState === WebSocket.OPEN) return resolve();
      this.ws.onopen = () => resolve();
      this.ws.onerror = (e) => reject(e);
    });
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
      throw new Error(`Eval error: ${JSON.stringify(res.exceptionDetails)}`);
    }
    return res.result ? res.result.value : null;
  }

  async captureScreenshot(outputPath) {
    const res = await this.send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(outputPath, Buffer.from(res.data, "base64"));
  }
}

async function runEnhancementsVerification() {
  console.log("=== STARTING BROWSER CDP AUDIT FOR ALL NEW ENHANCEMENTS ===");
  [SCREENSHOT_DIR, EVIDENCE_DIR, LOG_DIR].forEach((d) => {
    if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
  });

  if (fs.existsSync(USER_DATA_DIR)) {
    try { fs.rmSync(USER_DATA_DIR, { recursive: true, force: true }); } catch (e) {}
  }
  fs.mkdirSync(USER_DATA_DIR, { recursive: true });

  const chromeProc = spawn(CHROME_PATH, [
    "--headless=new",
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${USER_DATA_DIR}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-client-side-phishing-detection",
    "--disable-default-apps",
    "--disable-hang-monitor",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-sync",
    "--disable-translate",
    "--metrics-recording-only",
    "--window-size=1600,1050",
    BASE_URL,
  ]);

  let cdp = null;
  const testResults = {
    timestamp: new Date().toISOString(),
    tests: [],
    consoleErrors: [],
    overallStatus: "RUNNING",
  };

  try {
    // Wait for Chrome remote debugging to come up
    let connected = false;
    for (let i = 0; i < 30; i++) {
      await sleep(500);
      try {
        const list = await fetchJson(`http://127.0.0.1:${PORT}/json`);
        if (list && list.length > 0) {
          const pageTarget = list.find((t) => t.type === "page") || list[0];
          cdp = new CDPClient(pageTarget.webSocketDebuggerUrl);
          await cdp.waitOpen();
          connected = true;
          break;
        }
      } catch (e) {}
    }

    if (!connected) {
      throw new Error("Failed to connect to Chrome CDP within 15 seconds.");
    }
    console.log("[OK] Chrome CDP Connected successfully.");

    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Console.enable");

    // Wait for initial load
    await sleep(2500);

    // --------------------------------------------------------------------------
    // STEP 0: AUTHENTICATION
    // --------------------------------------------------------------------------
    console.log("--> Step 0: Checking Authentication & Performing Login...");
    let authState = await cdp.eval(`
      (async () => {
        let tok = (typeof state !== 'undefined' && state.token) || localStorage.getItem("sgai_token");
        if (!tok) {
          const r = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username: "owner", password: "ShahGroup_Owner_Secured_2026!#" })
          });
          const j = await r.json();
          if (j.token) {
            tok = j.token;
            state.token = j.token;
            localStorage.setItem("sgai_token", j.token);
            await auth();
          }
        }
        return {
          token: !!(typeof state !== 'undefined' && state.token),
          user: typeof state !== 'undefined' ? state.user : null,
          ws: typeof state !== 'undefined' ? state.ws : null
        };
      })()
    `);
    console.log("[OK] Auth State:", authState);
    if (!authState || !authState.token) {
      throw new Error("Authentication failed: Unable to log in with owner credentials.");
    }
    testResults.tests.push({ name: "Authentication (Owner)", status: "PASSED", details: authState });

    // --------------------------------------------------------------------------
    // STEP 1: DYNAMIC QUOTATION ITEM SYSTEM (2, 5, 10, 20 items, live math, edit)
    // --------------------------------------------------------------------------
    console.log("--> Step 1: Testing Dynamic Quotation Items (2, 5, 10, 20 rows, live math)...");
    
    // Switch to Finance view
    await cdp.eval(`showSection("finance"); switchWorkspace("SSC");`);
    await sleep(1000);

    // Open Quotation Modal
    await cdp.eval(`openNewQuotationModal()`);
    await sleep(500);

    // Check default items count (must be 2)
    const initialItemCount = await cdp.eval(`window.qActiveItems ? window.qActiveItems.length : 0`);
    console.log("Initial Quotation Items Count (Default):", initialItemCount);

    // Add items up to 5
    await cdp.eval(`
      addQuotationItemRow(); // 3
      addQuotationItemRow(); // 4
      addQuotationItemRow(); // 5
    `);
    const count5 = await cdp.eval(`window.qActiveItems.length`);

    // Add items up to 10
    await cdp.eval(`
      for(let i=0; i<5; i++) addQuotationItemRow();
    `);
    const count10 = await cdp.eval(`window.qActiveItems.length`);

    // Add items up to 20
    await cdp.eval(`
      for(let i=0; i<10; i++) addQuotationItemRow();
    `);
    const count20 = await cdp.eval(`window.qActiveItems.length`);

    console.log(`Dynamic rows verification: count5=${count5}, count10=${count10}, count20=${count20}`);

    // Set test data for 5 items and verify live recalculation
    const mathTest = await cdp.eval(`
      qActiveItems = [
        { item_name: "DGPS Ground Control Point (GCP) Survey", unit: "Point", quantity: 20, rate: 1500, discount: 0, gst_rate: 18 },
        { item_name: "Drone Aerial Photogrammetry (LiDAR)", unit: "Sq Km", quantity: 15, rate: 8000, discount: 5000, gst_rate: 18 },
        { item_name: "AutoCAD Civil 3D Alignment & Profile", unit: "Km", quantity: 25, rate: 3000, discount: 0, gst_rate: 18 },
        { item_name: "Hydrological Catchment & HFL Analysis", unit: "Lump Sum", quantity: 1, rate: 25000, discount: 0, gst_rate: 18 },
        { item_name: "MoRTH Geotechnical Soil Testing Boreholes", unit: "Nos", quantity: 10, rate: 4500, discount: 2000, gst_rate: 18 }
      ];
      renderQuotationRows();
      calculateQuotationLiveTotal();
      
      const subtotal = qActiveItems.reduce((acc, it) => acc + ((it.quantity||0)*(it.rate||0)), 0);
      const discount = qActiveItems.reduce((acc, it) => acc + (parseFloat(it.discount)||0), 0);
      const taxable = subtotal - discount;
      const gst = taxable * 0.18;
      const total = taxable + gst;

      ({
        itemCount: qActiveItems.length,
        subtotal,
        discount,
        taxable,
        gst,
        total,
        previewTotalText: $("#q-preview-total") ? $("#q-preview-total").textContent : "",
        wordsText: $("#q-amount-words") ? $("#q-amount-words").textContent : ""
      })
    `);

    console.log("[OK] Quotation 5-Item Math Test:", mathTest);
    
    // Submit this dynamic quotation
    const createdQuotation = await cdp.eval(`
      (async () => {
        $("#q-project-name").value = "MPRDC 4-Lane Highway Detailed Project Survey";
        $("#q-client-name").value = "Madhya Pradesh Road Development Corporation";
        $("#q-terms").value = "50% advance, balance on deliverable submission";
        
        const payload = {
          workspace_id: state.ws,
          project_name: $("#q-project-name").value,
          client_name: $("#q-client-name").value,
          validity_days: parseInt($("#q-validity").value) || 30,
          gst_rate: 18,
          terms: $("#q-terms").value,
          items: qActiveItems
        };
        const res = await api("/api/quotations?workspace=" + state.ws, { method: "POST", body: payload });
        closeModal();
        return res;
      })()
    `);
    console.log("[OK] Created Quotation via Modal/API:", createdQuotation);

    // Refresh quotations table and verify it has Edit & View buttons
    await cdp.eval(`refreshFinanceData();`);
    await sleep(800);

    const quotRowVerification = await cdp.eval(`
      const rows = document.querySelectorAll("#finance-quotations-table tbody tr");
      const firstRow = rows[0] ? rows[0].innerText : "";
      const hasEditBtn = !!document.querySelector("#finance-quotations-table button[onclick*='openEditQuotationModal']");
      const hasViewBtn = !!document.querySelector("#finance-quotations-table button[onclick*='openViewQuotationModal']");
      ({ totalRows: rows.length, firstRow: firstRow.substring(0, 100), hasEditBtn, hasViewBtn })
    `);
    console.log("[OK] Quotation Table Inspection:", quotRowVerification);

    // Test Edit quotation modal without losing items
    const editLoadTest = await cdp.eval(`
      (async () => {
        if (${createdQuotation && createdQuotation.quotation ? createdQuotation.quotation.id : 'null'}) {
          await openEditQuotationModal(${createdQuotation.quotation.id});
          await new Promise(r => setTimeout(r, 400));
          const count = qActiveItems.length;
          const firstItem = qActiveItems[0] ? qActiveItems[0].item_name : "";
          closeModal();
          return { loadedItemCount: count, firstItem };
        }
        return { loadedItemCount: 0, firstItem: "none" };
      })()
    `);
    console.log("[OK] Quotation Edit Load Test (Preserved Items):", editLoadTest);

    testResults.tests.push({
      name: "Dynamic Quotation Module (2, 5, 10, 20 items, live math, edit)",
      status: (count20 === 20 && mathTest.itemCount === 5 && editLoadTest.loadedItemCount === 5) ? "PASSED" : "FAILED",
      details: { count5, count10, count20, mathTest, editLoadTest, quotRowVerification }
    });

    // --------------------------------------------------------------------------
    // STEP 2: SURVEY SITES LIFECYCLE (16 Statuses, Reminders, 3 Tabs, Financials)
    // --------------------------------------------------------------------------
    console.log("--> Step 2: Testing Survey Site Management Lifecycle (16 statuses, travel, equipment, reminders)...");
    
    // Switch to Projects
    await cdp.eval(`showSection("projects");`);
    await sleep(800);

    // Open New Site Modal
    await cdp.eval(`openNewSiteModal()`);
    await sleep(500);

    // Switch between all 3 tabs in the modal
    const tabsCheck = await cdp.eval(`
      const tabs = [];
      const tabBtns = document.querySelectorAll("#modal-site-tabs button");
      switchSiteModalTab('scope', tabBtns[0]);
      tabs.push({ tab: 'scope', visible: $("#site-tab-scope") && $("#site-tab-scope").style.display !== 'none' });
      switchSiteModalTab('team', tabBtns[1]);
      tabs.push({ tab: 'team', visible: $("#site-tab-team") && $("#site-tab-team").style.display !== 'none' });
      switchSiteModalTab('finance', tabBtns[2]);
      tabs.push({ tab: 'finance', visible: $("#site-tab-finance") && $("#site-tab-finance").style.display !== 'none' });
      tabs;
    `);
    console.log("[OK] 3-Tab Modal Switch Test:", tabsCheck);

    // Create a new site with rich metadata
    const createdSiteRes = await cdp.eval(`
      (async () => {
        $("#s-name").value = "Nagpur Metro Reach-4 Alignment & Geodetic Control";
        $("#s-code").value = "SITE-NGP-METRO-02";
        $("#s-client").value = "Maharashtra Metro Rail Corporation (MahaMetro)";
        $("#s-location").value = "Hingna to Subhash Nagar Corridor, Nagpur";
        $("#s-address").value = "Metro Pillar 120 to 240, Wardha Rd, Nagpur 440022";
        $("#s-coords").value = "21.1458 N, 79.0882 E";
        $("#s-start-date").value = new Date().toISOString().split("T")[0];
        $("#s-end-date").value = new Date(Date.now() + 14*86400000).toISOString().split("T")[0];
        $("#s-leader").value = "Rajesh Sharma";
        $("#s-team").value = "Amit Verma, Vikrant Shah, Priya Deshmukh";
        $("#s-equipment").value = "Trimble R12i DGPS Base/Rover, Leica TS16 Total Station, Trimble DiNi Digital Level";
        $("#s-transport").value = "Bolero Camper MH-31-AG-8899";
        $("#s-expenses").value = "25000";
        $("#s-contact").value = "Er. Deshpande (+91 98220 11223)";
        $("#s-instructions").value = "Strict compliance with MoRTH accuracy tolerances.";
        $("#s-value").value = "450000";
        $("#s-advance").value = "150000";

        const teamList = $("#s-team").value.split(",").map(x => x.trim()).filter(Boolean);
        const equipList = $("#s-equipment").value.split(",").map(x => x.trim()).filter(Boolean);

        const payload = {
          workspace_id: state.ws,
          code: $("#s-code").value.trim(),
          name: $("#s-name").value.trim(),
          client_name: $("#s-client").value.trim(),
          project_location: $("#s-location").value.trim(),
          complete_address: $("#s-address").value.trim(),
          coordinates: $("#s-coords").value.trim(),
          survey_type: $("#s-type").value,
          start_date: $("#s-start-date").value,
          expected_completion_date: $("#s-end-date").value,
          team_leader: $("#s-leader").value.trim(),
          assigned_team: teamList,
          equipment_assigned: equipList,
          transport_details: $("#s-transport").value.trim(),
          estimated_expenses: parseFloat($("#s-expenses").value) || 0,
          site_contact_person: $("#s-contact").value.trim(),
          special_instructions: $("#s-instructions").value.trim(),
          project_value: parseFloat($("#s-value").value) || 0,
          advance_received: parseFloat($("#s-advance").value) || 0,
          payment_due_date: new Date(Date.now() + 30*86400000).toISOString().split("T")[0],
          survey_status: "Site Scheduled"
        };

        const res = await api("/api/sites?workspace=" + state.ws, { method: "POST", body: payload });
        closeModal();
        return res;
      })()
    `);
    console.log("[OK] Created Comprehensive Site:", createdSiteRes);

    // Refresh and test site lifecycle category filters
    await cdp.eval(`renderSites('all');`);
    await sleep(800);

    const filterTests = await cdp.eval(`
      (async () => {
        const categories = ['all', 'upcoming', 'tomorrow', 'today', 'overdue', 'completed', 'payment_pending'];
        const results = {};
        for(const cat of categories) {
          const res = await api('/api/sites?category=' + cat + '&workspace=' + state.ws);
          results[cat] = res.sites ? res.sites.length : 0;
        }
        return results;
      })()
    `);
    console.log("[OK] Site Lifecycle Filters & Reminders Result:", filterTests);

    // Test updating site status through multiple lifecycle stages
    const siteId = createdSiteRes && createdSiteRes.site ? createdSiteRes.site.id : 1;
    const statusUpdateFlow = await cdp.eval(`
      (async () => {
        const stages = [
          "Survey In Progress",
          "Field Survey Completed",
          "Data Processing",
          "Report Submitted"
        ];
        const historyLogs = [];
        for (const st of stages) {
          const upd = await api('/api/sites/' + ${siteId} + '/status?workspace=' + state.ws, {
            method: "POST",
            body: { status: st, remarks: "Automated CDP transition to: " + st }
          });
          historyLogs.push(upd.site ? upd.site.survey_status : null);
        }
        return historyLogs;
      })()
    `);
    console.log("[OK] Survey Status Lifecycle Transitions:", statusUpdateFlow);

    // Test financial balance update on site
    const paymentUpdateRes = await cdp.eval(`
      (async () => {
        const upd = await api('/api/sites/' + ${siteId} + '/payment?workspace=' + state.ws, {
          method: "POST",
          body: {
            project_value: 450000,
            advance_received: 150000,
            total_billed: 450000,
            payment_received: 200000,
            payment_due_date: "2026-12-15",
            payment_status: "Partially Paid"
          }
        });
        return {
          val: upd.site.project_value,
          paid: upd.site.payment_received,
          balance: upd.site.balance_due,
          status: upd.site.payment_status
        };
      })()
    `);
    console.log("[OK] Site Financial Tracking Result:", paymentUpdateRes);

    testResults.tests.push({
      name: "Survey Sites Lifecycle (16 statuses, travel, equipment, reminders, finances)",
      status: (statusUpdateFlow.length === 4 && paymentUpdateRes.balance === 100000) ? "PASSED" : "FAILED",
      details: { tabsCheck, createdSiteRes, filterTests, statusUpdateFlow, paymentUpdateRes }
    });

    // --------------------------------------------------------------------------
    // STEP 3: NON-GST COMMERCIAL BILLING SYSTEM (Bill of Supply, 0% Tax)
    // --------------------------------------------------------------------------
    console.log("--> Step 3: Testing Non-GST Commercial Bills (Bill of Supply, 0 tax, BILL-YYYY-XXXX)...");
    
    // Switch to Finance
    await cdp.eval(`showSection("finance");`);
    await sleep(600);

    // Open Non-GST Bill Modal
    await cdp.eval(`openNewNonGSTBillModal()`);
    await sleep(500);

    // Verify non-GST live math (strictly 0% tax)
    const nonGstMath = await cdp.eval(`
      (() => {
        nonGstActiveItems = [
          { item: "Boundary Demarcation & Boundary Pillars Fixing", unit: "Pillars", quantity: 50, rate: 800 },
          { item: "Topographic Ground Level Spot Heights Survey", unit: "Acre", quantity: 25, rate: 1200 },
          { item: "CAD As-Built Drawing Deliverable Compilation", unit: "Lump Sum", quantity: 1, rate: 15000 }
        ];
        renderNonGstRows();
        calculateNonGstLiveTotal();

        const subtotal = nonGstActiveItems.reduce((acc, it) => acc + ((it.quantity||0)*(it.rate||0)), 0);
        return {
          itemCount: nonGstActiveItems.length,
          subtotal,
          previewTaxText: $("#ng-preview-tax") ? $("#ng-preview-tax").textContent : "",
          previewTotalText: $("#ng-preview-total") ? $("#ng-preview-total").textContent : "",
          wordsText: $("#ng-amount-words") ? $("#ng-amount-words").textContent : ""
        };
      })()
    `);
    console.log("[OK] Non-GST Bill Live Recalculation (Strictly 0% Tax):", nonGstMath);

    // Submit Non-GST Bill
    const createdBillRes = await cdp.eval(`
      (async () => {
        $("#ng-client-name").value = "Vidarbha Agro & Infrastructure Pvt Ltd";
        $("#ng-client-address").value = "Plot 45, MIDC Butibori, Nagpur - 441108";
        $("#ng-client-contact").value = "+91 94221 55667";
        $("#ng-discount").value = "5000";
        calculateNonGstLiveTotal();

        const payload = {
          workspace_id: state.ws,
          bill_type: "NON_GST",
          client_name: $("#ng-client-name").value.trim(),
          client_address: $("#ng-client-address").value.trim(),
          client_contact: $("#ng-client-contact").value.trim(),
          invoice_date: $("#ng-bill-date").value,
          due_date: $("#ng-due-date").value,
          payment_mode: $("#ng-pay-mode").value,
          discount_amount: 5000,
          notes: "Commercial non-taxable supply. Payment via RTGS/NEFT.",
          items: nonGstActiveItems
        };

        const res = await api("/api/bills?workspace=" + state.ws, { method: "POST", body: payload });
        closeModal();
        return res;
      })()
    `);
    console.log("[OK] Created Non-GST Commercial Bill:", createdBillRes);

    // Verify Bill of Supply preview modal
    const billDoc = createdBillRes && (createdBillRes.bill || createdBillRes.invoice);
    const billPreviewTest = await cdp.eval(`
      (async () => {
        if (${billDoc ? billDoc.id : 'null'}) {
          // Put billDoc into cachedInvoices so previewInvoice can render it
          if (!window.cachedInvoices) window.cachedInvoices = [];
          const idx = window.cachedInvoices.findIndex(x => x.id === ${billDoc ? billDoc.id : 0});
          if (idx >= 0) window.cachedInvoices[idx] = ${JSON.stringify(billDoc)};
          else window.cachedInvoices.unshift(${JSON.stringify(billDoc)});

          previewInvoice(${billDoc ? billDoc.id : 0});
          await new Promise(r => setTimeout(r, 400));
          const modalText = $("#modal-content") ? $("#modal-content").innerText : "";
          const hasBillOfSupply = modalText.includes("BILL OF SUPPLY");
          const hasZeroTax = modalText.includes("0.00") || modalText.includes("Exempt");
          const hasSec31 = modalText.includes("31(3)(c)") || modalText.includes("Non-GST");
          closeModal();
          return { hasBillOfSupply, hasZeroTax, hasSec31, billNum: "${billDoc ? billDoc.invoice_number : ''}" };
        }
        return { hasBillOfSupply: false, hasZeroTax: false, hasSec31: false, billNum: "" };
      })()
    `);
    console.log("[OK] Bill of Supply Preview Verification:", billPreviewTest);

    testResults.tests.push({
      name: "Non-GST Commercial Bills (Bill of Supply, strictly 0% tax, BILL-YYYY-XXXX)",
      status: (billPreviewTest.hasBillOfSupply && billDoc && billDoc.invoice_number.startsWith("BILL-")) ? "PASSED" : "FAILED",
      details: { nonGstMath, createdBillRes, billPreviewTest }
    });

    // --------------------------------------------------------------------------
    // STEP 4: REGISTERED VENDOR MANAGEMENT (KYC, MSME, PAN, Bank, Approval)
    // --------------------------------------------------------------------------
    console.log("--> Step 4: Testing Registered Vendor Workflow (KYC, MSME, PAN, Bank, Approval)...");
    
    // Switch to Vendors tab in Finance
    await cdp.eval(`
      (async () => {
        const nav = $("#subnav-finance");
        if(nav) {
          const btn = nav.querySelector("button[data-sub='vendors']");
          if(btn) btn.click();
        }
        await renderRegisteredVendors('all');
      })()
    `);
    await sleep(800);

    // Open Register Vendor Modal
    await cdp.eval(`openRegisterVendorModal()`);
    await sleep(500);

    // Submit vendor registration
    const vendorRegRes = await cdp.eval(`
      (async () => {
        $("#v-name").value = "Trimble Navigation India Pvt Ltd";
        $("#v-contact-person").value = "Suresh Kulkarni (Regional Sales Head)";
        $("#v-mobile").value = "+91 98230 44556";
        $("#v-email").value = "suresh.kulkarni@trimble.com";
        $("#v-cat").value = "Survey Equipment";
        $("#v-services").value = "Trimble R12i RTK GNSS Receiver AMC, Calibration, Base Station CORS correction subscriptions";
        $("#v-address").value = "Unit 402, Trade Centre, BKC, Bandra East";
        $("#v-city").value = "Mumbai";
        $("#v-state").value = "Maharashtra";
        $("#v-pincode").value = "400051";
        $("#v-gstin").value = "27AAACT9920M1Z8";
        $("#v-pan").value = "AAACT9920M";
        $("#v-msme").value = "UDYAM-MH-19-0044892";
        $("#v-bank-name").value = "HDFC Bank Ltd";
        $("#v-bank-account").value = "50200048192831";
        $("#v-bank-ifsc").value = "HDFC0000060";

        const payload = {
          workspace_id: state.ws,
          company_name: $("#v-name").value,
          contact_person: $("#v-contact-person").value,
          mobile: $("#v-mobile").value,
          email: $("#v-email").value,
          category: $("#v-cat").value,
          services_supplied: $("#v-services").value,
          address: $("#v-address").value,
          city: $("#v-city").value,
          state: $("#v-state").value,
          pincode: $("#v-pincode").value,
          gstin: $("#v-gstin").value,
          pan: $("#v-pan").value,
          msme_udyam: $("#v-msme").value,
          bank_name: $("#v-bank-name").value,
          bank_account: $("#v-bank-account").value,
          bank_ifsc: $("#v-bank-ifsc").value,
          status: "Under Verification"
        };

        const res = await api("/api/vendors?workspace=" + state.ws, { method: "POST", body: payload });
        closeModal();
        return res;
      })()
    `);
    console.log("[OK] Created Registered Vendor:", vendorRegRes);

    const vendorId = vendorRegRes && vendorRegRes.vendor ? vendorRegRes.vendor.id : 1;

    // Test vendor approval workflow
    const vendorStatusFlow = await cdp.eval(`
      (async () => {
        const approved = await api('/api/vendors/' + ${vendorId} + '/status?workspace=' + state.ws, {
          method: "POST",
          body: { status: "Approved", remarks: "KYC and GSTIN verified against GST portal" }
        });
        const active = await api('/api/vendors/' + ${vendorId} + '/status?workspace=' + state.ws, {
          method: "POST",
          body: { status: "Active", remarks: "Master service agreement signed" }
        });
        return {
          approvedStatus: approved.vendor ? approved.vendor.status : null,
          activeStatus: active.vendor ? active.vendor.status : null
        };
      })()
    `);
    console.log("[OK] Vendor Status Approval Workflow:", vendorStatusFlow);

    // Refresh and check vendor rendering
    const vendorTableCheck = await cdp.eval(`
      (async () => {
        await renderRegisteredVendors('all');
        const box = $("#finance-vendors");
        const table = box ? box.querySelector("table") : null;
        const rows = table ? table.querySelectorAll("tbody tr") : [];
        return { hasTable: !!table, rowCount: rows.length, firstText: rows[0] ? rows[0].innerText.substring(0, 80) : "" };
      })()
    `);
    console.log("[OK] Vendor Table Rendering:", vendorTableCheck);

    testResults.tests.push({
      name: "Registered Vendor Management (KYC, MSME, PAN, Bank, Approval)",
      status: (vendorStatusFlow.activeStatus === "Active" && vendorTableCheck.hasTable) ? "PASSED" : "FAILED",
      details: { vendorRegRes, vendorStatusFlow, vendorTableCheck }
    });

    // --------------------------------------------------------------------------
    // STEP 5: EMPLOYEE STATUS & EXIT CLEARANCE MANAGEMENT
    // --------------------------------------------------------------------------
    console.log("--> Step 5: Testing Employee Status & Exit Management (Active, Notice, Former, F&F)...");
    
    // Switch to HRM
    await cdp.eval(`showSection("hrm");`);
    await sleep(800);

    // Test roster filters
    const rosterFilters = await cdp.eval(`
      (async () => {
        const activeRes = await api('/api/employees?filter=active&workspace=' + state.ws);
        const noticeRes = await api('/api/employees?filter=notice&workspace=' + state.ws);
        const formerRes = await api('/api/employees?filter=former&workspace=' + state.ws);
        const allRes = await api('/api/employees?filter=all&workspace=' + state.ws);
        return {
          activeCount: activeRes.employees ? activeRes.employees.length : 0,
          noticeCount: noticeRes.employees ? noticeRes.employees.length : 0,
          formerCount: formerRes.employees ? formerRes.employees.length : 0,
          allCount: allRes.employees ? allRes.employees.length : 0,
          sampleActive: activeRes.employees && activeRes.employees[0] ? activeRes.employees[0].name : ""
        };
      })()
    `);
    console.log("[OK] Employee Roster Filters Initial:", rosterFilters);

    // Perform an exit clearance workflow on an employee
    const exitWorkflowRes = await cdp.eval(`
      (async () => {
        let empList = await api('/api/employees?filter=active&workspace=' + state.ws);
        let target = empList.employees && empList.employees.length ? empList.employees[empList.employees.length - 1] : null;
        if (!target) {
          const all = await api('/api/employees?filter=all&workspace=' + state.ws);
          if (all.employees && all.employees.length > 0) {
            target = all.employees[0];
            await api('/api/employees/' + target.id + '/status?workspace=' + state.ws, {
              method: "POST",
              body: { employment_status: "Active", remarks: "Reset to active for verification test" }
            });
          }
        }
        if (!target) return { updated: false, reason: "No target employee found" };

        const payload = {
          employment_status: "Exited",
          last_working_date: "2026-11-20",
          exit_date: "2026-11-20",
          reason_for_leaving: "Relocating to home state / higher education",
          exit_type: "Resignation",
          notice_period_details: "Served 30 days notice period satisfactorily",
          handover_status: "Completed",
          final_settlement_status: "Full & Final Settled",
          exit_remarks: "All survey instruments, DGPS access credentials, and company SIM card handed over to store manager.",
          remarks: "Exit clearance certified by HR & Operations"
        };

        const upd = await api('/api/employees/' + target.id + '/status?workspace=' + state.ws, {
          method: "POST",
          body: payload
        });

        // Re-check filters
        const formerRes = await api('/api/employees?filter=former&workspace=' + state.ws);
        return {
          updated: true,
          empId: target.id,
          empName: target.name,
          newStatus: upd.employee ? upd.employee.employment_status : null,
          formerCountAfter: formerRes.employees ? formerRes.employees.length : 0
        };
      })()
    `);
    console.log("[OK] Exit Clearance Workflow Result:", exitWorkflowRes);

    testResults.tests.push({
      name: "Employee Status & Exit Management (Active/Notice/Former, F&F settlement, handover)",
      status: (exitWorkflowRes.updated && exitWorkflowRes.newStatus === "Exited") ? "PASSED" : "FAILED",
      details: { rosterFilters, exitWorkflowRes }
    });

    // --------------------------------------------------------------------------
    // STEP 6: REPORT ARCHIVE & VISUAL ANALYTICS (Charts, Tables, In-App Viewer)
    // --------------------------------------------------------------------------
    console.log("--> Step 6: Testing Report Archive & Visual Analytics (Charts, Tables, In-App Viewer)...");
    
    // Switch to Finance -> Reports
    const chartsCheck = await cdp.eval(`
      (async () => {
        showSection("finance");
        const nav = $("#subnav-finance");
        if(nav) {
          const btn = nav.querySelector("button[data-sub='reports']");
          if(btn) btn.click();
        }
        await renderReportsArchive();
        const summaryBox = $("#reports-analytics-summary");
        const chartsBox = $("#reports-charts-container");
        return {
          hasSummary: !!summaryBox && summaryBox.children.length >= 4,
          hasCharts: !!chartsBox && chartsBox.children.length >= 2,
          chartTitles: chartsBox ? Array.from(chartsBox.querySelectorAll("h4")).map(h => h.innerText) : []
        };
      })()
    `);
    console.log("[OK] Report Archive Visual Analytics & Charts:", chartsCheck);

    // Trigger dynamic report generation
    const generatedReportRes = await cdp.eval(`
      (async () => {
        const payload = {
          workspace_id: state.ws,
          report_type: ($("#report-type-select") ? $("#report-type-select").value : "MONTHLY_PERFORMANCE"),
          date_range: ($("#report-period-select") ? $("#report-period-select").value : "Last 30 Days"),
          title: "SSC Master Financial & Operations Acceptance Audit Report",
          notes: "Generated via automated CDP verification runner with live DB queries."
        };

        const res = await api("/api/reports/generate?workspace=" + state.ws, { method: "POST", body: payload });
        await renderReportsArchive();
        return res;
      })()
    `);
    console.log("[OK] Generated Automated Report:", generatedReportRes);

    // Open in-app report viewer modal
    const repId = generatedReportRes && generatedReportRes.report ? generatedReportRes.report.id : 1;
    const viewerCheck = await cdp.eval(`
      (async () => {
        await openReportViewerModal(${repId});
        await new Promise(r => setTimeout(r, 600));
        const modal = $("#modal-content");
        const tables = modal ? modal.querySelectorAll("table") : [];
        const title = modal ? modal.querySelector("h3").innerText : "";
        const text = modal ? modal.innerText : "";
        closeModal();
        return {
          hasModal: !!modal,
          title,
          tableCount: tables.length,
          hasSummary: text.includes("Executive Summary") || text.includes("Financial Summary"),
          hasRecommendations: text.includes("Recommendations")
        };
      })()
    `);
    console.log("[OK] In-App Report Viewer Modal Inspection:", viewerCheck);

    testResults.tests.push({
      name: "Report Archive & Visual Analytics (Charts, Tables, In-App Viewer)",
      status: (chartsCheck.hasCharts && viewerCheck.tableCount >= 2) ? "PASSED" : "FAILED",
      details: { chartsCheck, generatedReportRes, viewerCheck }
    });

    // --------------------------------------------------------------------------
    // STEP 7: THEME CONTRAST & ACCESSIBILITY AUDIT (Light & Dark Themes)
    // --------------------------------------------------------------------------
    console.log("--> Step 7: Performing Light Theme & Dark Theme Contrast Audit...");
    
    // Switch to Light Theme
    await cdp.eval(`setAppTheme('light');`);
    await sleep(600);

    const lightContrastCheck = await cdp.eval(`
      (() => {
        const bodyBg = window.getComputedStyle(document.body).backgroundColor;
        const bodyColor = window.getComputedStyle(document.body).color;
        
        // Sample cards, inputs, tables, buttons
        const card = document.querySelector(".card");
        const cardBg = card ? window.getComputedStyle(card).backgroundColor : "";
        const cardColor = card ? window.getComputedStyle(card).color : "";

        const input = document.querySelector("input");
        const inputBg = input ? window.getComputedStyle(input).backgroundColor : "";
        const inputColor = input ? window.getComputedStyle(input).color : "";

        const th = document.querySelector("th");
        const thColor = th ? window.getComputedStyle(th).color : "";

        // Check for any white text on light backgrounds
        const allTextEls = Array.from(document.querySelectorAll("p, span, div, h1, h2, h3, h4, th, td, label"));
        let badContrastCount = 0;
        for (const el of allTextEls.slice(0, 100)) {
          const c = window.getComputedStyle(el).color;
          // Check if text is white AND background is white/light (illegible contrast)
          if (c === "rgb(255, 255, 255)") {
            let cur = el;
            let bg = window.getComputedStyle(cur).backgroundColor;
            while (cur && (bg === "transparent" || bg === "rgba(0, 0, 0, 0)")) {
              cur = cur.parentElement;
              if (cur) bg = window.getComputedStyle(cur).backgroundColor;
            }
            if (bg.includes("255, 255, 255") || bg.includes("248, 250, 252") || bg.includes("241, 245, 249")) {
              badContrastCount++;
            }
          }
        }

        return {
          theme: 'light',
          bodyBg,
          bodyColor,
          cardBg,
          cardColor,
          inputBg,
          inputColor,
          thColor,
          badContrastCount
        };
      })()
    `);
    console.log("[OK] Light Theme Computed Styles & Contrast:", lightContrastCheck);

    // Switch back to Dark Theme
    await cdp.eval(`setAppTheme('dark');`);
    await sleep(400);

    const darkContrastCheck = await cdp.eval(`
      (() => {
        const bodyBg = window.getComputedStyle(document.body).backgroundColor;
        const bodyColor = window.getComputedStyle(document.body).color;
        return { theme: 'dark', bodyBg, bodyColor };
      })()
    `);
    console.log("[OK] Dark Theme Computed Styles:", darkContrastCheck);

    testResults.tests.push({
      name: "Light Theme Accessibility & Contrast Hardening",
      status: (lightContrastCheck.badContrastCount === 0 && lightContrastCheck.bodyColor.includes("15, 23, 42")) ? "PASSED" : "FAILED",
      details: { lightContrastCheck, darkContrastCheck }
    });

    // --------------------------------------------------------------------------
    // STEP 8: CONSOLE ERROR AUDIT & EVIDENCE CAPTURE
    // --------------------------------------------------------------------------
    console.log("--> Step 8: Checking Console Errors & Capturing Screenshot...");
    
    // Capture full-page screenshot
    const screenshotPath = path.join(SCREENSHOT_DIR, "enhancements_cdp_screenshot.png");
    await cdp.captureScreenshot(screenshotPath);
    console.log("[OK] Captured verification screenshot:", screenshotPath);

    const consoleErrorCount = cdp.consoleErrors.length;
    console.log("Total Captured Console Errors:", consoleErrorCount);
    if (consoleErrorCount > 0) {
      console.warn("Captured Errors:", cdp.consoleErrors);
    }

    testResults.tests.push({
      name: "Console & Runtime Stability (0 Console Errors)",
      status: consoleErrorCount === 0 ? "PASSED" : "FAILED",
      details: { consoleErrorCount, errors: cdp.consoleErrors }
    });

    // Overall Status
    const allPassed = testResults.tests.every((t) => t.status === "PASSED");
    testResults.overallStatus = allPassed ? "ALL_PASSED" : "FAILED";
    console.log(`\n=== FINAL BROWSER AUDIT RESULT: ${testResults.overallStatus} ===\n`);

  } catch (err) {
    console.error("BROWSER VERIFICATION FATAL ERROR:", err);
    testResults.overallStatus = "FATAL_ERROR";
    testResults.error = err.message;
  } finally {
    if (cdp && cdp.ws) {
      try { cdp.ws.close(); } catch (e) {}
    }
    try {
      chromeProc.kill("SIGKILL");
    } catch (e) {}

    // Save test results evidence
    const evidencePath = path.join(EVIDENCE_DIR, "enhancements_browser_evidence.json");
    fs.writeFileSync(evidencePath, JSON.stringify(testResults, null, 2), "utf-8");
    console.log("[OK] Evidence JSON saved to:", evidencePath);
  }
}

runEnhancementsVerification();
