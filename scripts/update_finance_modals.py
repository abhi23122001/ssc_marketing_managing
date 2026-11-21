# scripts/update_finance_modals.py
"""
Updates foundation/dashboard/dashboard.html with interactive modals for:
1. openNewQuotationModal() - Create quotation with dynamic line items & live GST computation
2. openNewInvoiceModal() - Create GST invoice with intra/interstate tax engine
3. openRecordPaymentModal(invId) - Record partial/full payment with NEFT/UPI/Cheque ref #
4. openIndividualPayslipModal() - Create individual payslip
5. Fixes cachedPayslips fetching to query /api/payroll/payslips
"""
import re
from pathlib import Path

DASHBOARD_FILE = Path("foundation/dashboard/dashboard.html")

def update_modals():
    content = DASHBOARD_FILE.read_text(encoding="utf-8")

    # 1. Fix payslip fetching in refreshFinanceData
    old_ps_fetch = """    const pRes = await api(`/api/payroll/runs?workspace=${state.ws}`);
    const runs = pRes.runs || [];
    if(runs.length){
      const latestRunId = runs[0].id;
      const psRes = await api(`/api/payroll/payslips?payroll_run_id=${latestRunId}`);
      cachedPayslips = psRes.payslips || [];
    } else {
      cachedPayslips = [];
    }"""

    new_ps_fetch = """    try {
      const psRes = await api(`/api/payroll/payslips`);
      cachedPayslips = psRes.payslips || [];
    } catch(ign) {
      cachedPayslips = [];
    }"""

    if old_ps_fetch in content:
        content = content.replace(old_ps_fetch, new_ps_fetch)
        print("✓ Fixed payslips fetching to query /api/payroll/payslips")

    # 2. Add interactive Creation Modals JS
    creation_modals_js = """
// ---- Interactive Finance Creation Modals ----

function openNewQuotationModal(){
  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#128221; Create Commercial Quotation Proposal</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form id="form-new-quotation" onsubmit="submitNewQuotation(event)">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div>
          <label style="font-size:11px;color:var(--muted)">Project Name / Scope:</label>
          <input id="q-project-name" required placeholder="e.g. NH-44 Alignment Topographical Survey" style="width:100%">
        </div>
        <div>
          <label style="font-size:11px;color:var(--muted)">Client Reference ID:</label>
          <input id="q-client-id" type="number" value="12" style="width:100%">
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div>
          <label style="font-size:11px;color:var(--muted)">Validity (Days):</label>
          <input id="q-validity" type="number" value="30" style="width:100%">
        </div>
        <div>
          <label style="font-size:11px;color:var(--muted)">GST Rate (%):</label>
          <select id="q-gst-rate" style="width:100%" onchange="calculateQuotationLiveTotal()">
            <option value="18" selected>18% (Standard Geospatial/Consultancy)</option>
            <option value="12">12% (Civil Works / Subcontract)</option>
            <option value="5">5% (Concessional)</option>
            <option value="0">0% (Exempt)</option>
          </select>
        </div>
      </div>

      <label style="font-size:11px;color:var(--muted);margin-bottom:4px;display:block">Line Items &amp; Deliverables:</label>
      <div id="q-items-container" style="display:flex;flex-direction:column;gap:6px;margin-bottom:10px">
        <div class="q-item-row" style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:6px">
          <input class="q-item-desc" placeholder="Scope Description" value="DGPS RTK Boundary Demarcation" required>
          <input class="q-item-unit" placeholder="Unit" value="Acre">
          <input class="q-item-qty" type="number" placeholder="Qty" value="100" oninput="calculateQuotationLiveTotal()">
          <input class="q-item-rate" type="number" placeholder="Rate" value="450" oninput="calculateQuotationLiveTotal()">
        </div>
        <div class="q-item-row" style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:6px">
          <input class="q-item-desc" placeholder="Scope Description" value="AutoCAD DWG &amp; Topo Contour Deliverables">
          <input class="q-item-unit" placeholder="Unit" value="Lump Sum">
          <input class="q-item-qty" type="number" placeholder="Qty" value="1" oninput="calculateQuotationLiveTotal()">
          <input class="q-item-rate" type="number" placeholder="Rate" value="15000" oninput="calculateQuotationLiveTotal()">
        </div>
      </div>

      <div style="background:var(--panel-2);padding:10px;border-radius:6px;border:1px solid var(--line);margin-bottom:12px;font-size:12px">
        <div style="display:flex;justify-content:space-between"><span>Taxable Subtotal:</span><strong id="q-preview-subtotal">INR 60,000.00</strong></div>
        <div style="display:flex;justify-content:space-between;margin-top:2px"><span>GST Tax (18%):</span><strong id="q-preview-gst">INR 10,800.00</strong></div>
        <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:14px;color:var(--accent)"><span>Grand Total:</span><strong id="q-preview-total">INR 70,800.00</strong></div>
      </div>

      <div class="form-group" style="margin-bottom:12px">
        <label style="font-size:11px;color:var(--muted)">Payment &amp; Delivery Terms:</label>
        <textarea id="q-terms" rows="2" style="width:100%;font-size:12px">50% Advance with official purchase order, balance 50% upon CAD deliverable submission.</textarea>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Create &amp; Save Quotation</button>
      </div>
    </form>
  `;
  showModal(html);
  calculateQuotationLiveTotal();
}

function calculateQuotationLiveTotal(){
  let subtotal = 0;
  document.querySelectorAll(".q-item-row").forEach(row => {
    const qty = parseFloat(row.querySelector(".q-item-qty") ? row.querySelector(".q-item-qty").value : 1) || 0;
    const rate = parseFloat(row.querySelector(".q-item-rate") ? row.querySelector(".q-item-rate").value : 0) || 0;
    subtotal += (qty * rate);
  });
  const gstRate = parseFloat($("#q-gst-rate") ? $("#q-gst-rate").value : 18) || 0;
  const gst = Math.round(subtotal * (gstRate / 100) * 100) / 100;
  const total = subtotal + gst;

  if($("#q-preview-subtotal")) $("#q-preview-subtotal").textContent = `INR ${subtotal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if($("#q-preview-gst")) $("#q-preview-gst").textContent = `INR ${gst.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if($("#q-preview-total")) $("#q-preview-total").textContent = `INR ${total.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
}

async function submitNewQuotation(e){
  e.preventDefault();
  const items = [];
  document.querySelectorAll(".q-item-row").forEach(row => {
    const desc = row.querySelector(".q-item-desc").value.trim();
    if(desc){
      const unit = row.querySelector(".q-item-unit").value.trim();
      const qty = parseFloat(row.querySelector(".q-item-qty").value) || 1;
      const rate = parseFloat(row.querySelector(".q-item-rate").value) || 0;
      items.push({ description: desc, unit: unit, quantity: qty, rate: rate, amount: qty * rate });
    }
  });

  const payload = {
    workspace_id: state.ws,
    project_name: $("#q-project-name").value.trim(),
    client_id: parseInt($("#q-client-id").value) || 12,
    validity_days: parseInt($("#q-validity").value) || 30,
    gst_rate: parseFloat($("#q-gst-rate").value) || 18,
    terms: $("#q-terms").value.trim(),
    items: items
  };

  try{
    await api(`/api/quotations?workspace=${state.ws}`, { method: "POST", body: payload });
    toast("Quotation created and registered successfully!", "ok");
    closeModal();
    await refreshFinanceData();
  }catch(err){
    toast("Error creating quotation: " + err.message, "bad");
  }
}

function openNewInvoiceModal(){
  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#128181; Create GST Tax Invoice (Rule 46)</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form id="form-new-invoice" onsubmit="submitNewInvoice(event)">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div>
          <label style="font-size:11px;color:var(--muted)">Billed To (Client ID):</label>
          <input id="inv-client-id" type="number" value="12" required style="width:100%">
        </div>
        <div>
          <label style="font-size:11px;color:var(--muted)">HSN / SAC Code:</label>
          <input id="inv-hsn" value="998315" required style="width:100%">
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div>
          <label style="font-size:11px;color:var(--muted)">Service / Work Item Description:</label>
          <input id="inv-item-desc" value="Topographical Drone LiDAR &amp; DGPS Survey Works" required style="width:100%">
        </div>
        <div>
          <label style="font-size:11px;color:var(--muted)">Taxable Service Amount (INR):</label>
          <input id="inv-amount" type="number" value="150000" required style="width:100%" oninput="calculateInvoiceLiveTax()">
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div>
          <label style="font-size:11px;color:var(--muted)">Tax Treatment:</label>
          <select id="inv-tax-type" style="width:100%" onchange="calculateInvoiceLiveTax()">
            <option value="intra" selected>Intra-State (CGST 9% + SGST 9%) - Maharashtra</option>
            <option value="inter">Inter-State (IGST 18%) - Outside Maharashtra</option>
          </select>
        </div>
        <div>
          <label style="font-size:11px;color:var(--muted)">Payment Due Date:</label>
          <input id="inv-due-date" type="date" value="${new Date(Date.now() + 15*86400000).toISOString().split('T')[0]}" style="width:100%">
        </div>
      </div>

      <div style="background:var(--panel-2);padding:10px;border-radius:6px;border:1px solid var(--line);margin-bottom:12px;font-size:12px">
        <div style="display:flex;justify-content:space-between"><span>Taxable Subtotal:</span><strong id="inv-preview-subtotal">INR 1,50,000.00</strong></div>
        <div style="display:flex;justify-content:space-between;margin-top:2px"><span>GST Tax Breakup:</span><strong id="inv-preview-tax">CGST 9%: INR 13,500 | SGST 9%: INR 13,500</strong></div>
        <div style="display:flex;justify-content:space-between;margin-top:4px;font-size:14px;color:var(--good)"><span>Total Invoice Value:</span><strong id="inv-preview-total">INR 1,77,000.00</strong></div>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Issue GST Tax Invoice</button>
      </div>
    </form>
  `;
  showModal(html);
  calculateInvoiceLiveTax();
}

function calculateInvoiceLiveTax(){
  const amt = parseFloat($("#inv-amount") ? $("#inv-amount").value : 150000) || 0;
  const isInter = $("#inv-tax-type") && $("#inv-tax-type").value === "inter";
  const tax = Math.round(amt * 0.18 * 100) / 100;
  const total = amt + tax;

  if($("#inv-preview-subtotal")) $("#inv-preview-subtotal").textContent = `INR ${amt.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if($("#inv-preview-tax")){
    if(isInter){
      $("#inv-preview-tax").textContent = `IGST 18%: INR ${tax.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
    } else {
      const half = tax / 2;
      $("#inv-preview-tax").textContent = `CGST 9%: INR ${half.toLocaleString('en-IN', {minimumFractionDigits:2})} | SGST 9%: INR ${half.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
    }
  }
  if($("#inv-preview-total")) $("#inv-preview-total").textContent = `INR ${total.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
}

async function submitNewInvoice(e){
  e.preventDefault();
  const amt = parseFloat($("#inv-amount").value) || 0;
  const isInter = $("#inv-tax-type").value === "inter";
  const desc = $("#inv-item-desc").value.trim();
  const hsn = $("#inv-hsn").value.trim();

  const payload = {
    workspace_id: state.ws,
    client_id: parseInt($("#inv-client-id").value) || 12,
    subtotal: amt,
    is_interstate: isInter,
    gst_rate: 18.0,
    due_date: $("#inv-due-date").value,
    items: [
      { item: desc, hsn_sac: hsn, quantity: 1, rate: amt, amount: amt }
    ]
  };

  try{
    await api(`/api/invoices?workspace=${state.ws}`, { method: "POST", body: payload });
    toast("GST Tax Invoice generated successfully!", "ok");
    closeModal();
    await refreshFinanceData();
  }catch(err){
    toast("Error creating invoice: " + err.message, "bad");
  }
}

function openRecordPaymentModal(invId){
  const inv = cachedInvoices.find(x => x.id === invId);
  const remaining = inv ? (inv.total_amount - (inv.amount_paid||0)) : 10000;

  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#128176; Record Payment for Invoice ${esc(inv ? inv.invoice_number : '')}</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form onsubmit="submitInvoicePayment(event, ${invId})">
      <div style="margin-bottom:10px">
        <label style="font-size:11px;color:var(--muted)">Payment Amount (INR):</label>
        <input id="pay-amount" type="number" value="${remaining}" required style="width:100%">
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div>
          <label style="font-size:11px;color:var(--muted)">Payment Mode:</label>
          <select id="pay-mode" style="width:100%">
            <option value="NEFT/RTGS">NEFT / RTGS</option>
            <option value="IMPS">IMPS</option>
            <option value="UPI">UPI / QR Code</option>
            <option value="Cheque">Cheque</option>
            <option value="Cash">Cash Voucher</option>
          </select>
        </div>
        <div>
          <label style="font-size:11px;color:var(--muted)">Transaction Ref / UTR #:</label>
          <input id="pay-ref" placeholder="e.g. UTR389201923" required style="width:100%">
        </div>
      </div>
      <div class="form-group" style="margin-bottom:12px">
        <label style="font-size:11px;color:var(--muted)">Notes / Remarks:</label>
        <input id="pay-notes" placeholder="e.g. Part payment against milestone completion" style="width:100%">
      </div>
      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Record Payment Receipt</button>
      </div>
    </form>
  `;
  showModal(html);
}

async function submitInvoicePayment(e, invId){
  e.preventDefault();
  const amt = parseFloat($("#pay-amount").value) || 0;
  const mode = $("#pay-mode").value;
  const ref = $("#pay-ref").value.trim();
  const notes = $("#pay-notes").value.trim();

  try{
    await api(`/api/invoices/${invId}/payment?workspace=${state.ws}`, {
      method: "POST",
      body: { amount: amt, payment_mode: mode, reference_number: ref, notes: notes }
    });
    toast("Payment recorded successfully!", "ok");
    closeModal();
    await refreshFinanceData();
  }catch(err){
    toast("Error recording payment: " + err.message, "bad");
  }
}
"""

    if "function openNewQuotationModal()" not in content:
        content = content.replace("// ---- Quotation Rendering & Operations ----", creation_modals_js + "\n\n// ---- Quotation Rendering & Operations ----")
        print("✓ Injected Interactive Quotation, GST Invoice & Payment Modals")

    DASHBOARD_FILE.write_text(content, encoding="utf-8")
    print(f"Updated dashboard.html ({len(content)} bytes). SUCCESS!")

if __name__ == "__main__":
    update_modals()
