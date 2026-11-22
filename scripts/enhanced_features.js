// ==============================================================================
// SHAH GROUP AI OS — LIFECYCLE & WORKFLOW AUTOMATION ENHANCEMENTS JAVASCRIPT
// ==============================================================================

// ------------------------------------------------------------------------------
// 1. DYNAMIC QUOTATIONS MODULE
// ------------------------------------------------------------------------------

var qActiveItems = [];
window.qActiveItems = qActiveItems;

function openNewQuotationModal(editData = null){
  const isEdit = !!(editData && editData.id);
  
  if (editData && editData.items && editData.items.length) {
    qActiveItems = JSON.parse(JSON.stringify(editData.items));
  } else {
    qActiveItems = [
      { item_name: "DGPS RTK Topographic Boundary Demarcation", description: "Centimeter geodetic survey with base and rover CORS correction", unit: "Acre", quantity: 50, rate: 450, discount: 0, gst_rate: 18 },
      { item_name: "AutoCAD Civil 3D & GIS Topo Deliverables", description: "Digital elevation model (DEM), contour mapping & L-section plan", unit: "Lump Sum", quantity: 1, rate: 15000, discount: 0, gst_rate: 18 }
    ];
  }

  const defaultClient = editData ? (editData.client_name || "") : "National Highways Authority of India";
  const defaultProj = editData ? (editData.project_name || "") : "NH-44 Highway Alignment & Topo Survey";
  const defaultValidity = editData ? (editData.validity_days || 30) : 30;
  const defaultGst = editData ? (editData.gst_rate || 18) : 18;
  const defaultTerms = editData ? (editData.terms || "") : "50% Advance with official work order, 50% upon CAD & GIS deliverable submission. Taxes extra as applicable.";

  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#128221; ${isEdit ? 'Edit Commercial Quotation #' + esc(editData.quotation_number) : 'Create Commercial Quotation Proposal'}</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form id="form-dynamic-quotation" onsubmit="submitDynamicQuotation(event, ${isEdit ? editData.id : 'null'})">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
        <div>
          <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Project Name / Scope:</label>
          <input id="q-project-name" required value="${esc(defaultProj)}" placeholder="e.g. NH-44 Alignment Survey" style="width:100%">
        </div>
        <div>
          <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Client Name / Enterprise:</label>
          <input id="q-client-name" required value="${esc(defaultClient)}" placeholder="e.g. NHAI / PWD / L&amp;T" style="width:100%">
        </div>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:14px">
        <div>
          <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Proposal Validity (Days):</label>
          <input id="q-validity" type="number" min="1" max="180" value="${defaultValidity}" style="width:100%">
        </div>
        <div>
          <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Default GST Rate (%):</label>
          <select id="q-gst-rate" style="width:100%" onchange="updateDefaultQuotationGst(this.value)">
            <option value="18" ${defaultGst==18?'selected':''}>18% (Standard Engineering/Survey)</option>
            <option value="12" ${defaultGst==12?'selected':''}>12% (Civil Subcontract Works)</option>
            <option value="5" ${defaultGst==5?'selected':''}>5% (Concessional)</option>
            <option value="0" ${defaultGst==0?'selected':''}>0% (Exempt)</option>
          </select>
        </div>
        <div>
          <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Client Contact / Ref:</label>
          <input id="q-client-contact" value="${esc(editData?editData.client_contact||'':'+91 94250 11223')}" placeholder="Contact / Phone" style="width:100%">
        </div>
      </div>

      <!-- Dynamic Items Section -->
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
        <label style="font-size:12px;font-weight:700">Scope Deliverables &amp; Line Items:</label>
        <button type="button" class="btn btn-secondary btn-sm" onclick="addQuotationItemRow()"><strong>+ Add More Item</strong></button>
      </div>

      <div style="border:1px solid var(--line);border-radius:6px;overflow:hidden;margin-bottom:14px;background:var(--panel)">
        <div style="max-height:260px;overflow-y:auto;overflow-x:auto">
          <table style="width:100%;font-size:12px;margin:0">
            <thead>
              <tr>
                <th style="min-width:180px">Item / Service Name</th>
                <th style="min-width:160px">Scope Description</th>
                <th style="width:75px">Qty</th>
                <th style="width:85px">Unit</th>
                <th style="width:90px">Rate (₹)</th>
                <th style="width:80px">Disc (₹)</th>
                <th style="width:75px">GST %</th>
                <th style="width:110px;text-align:right">Amount (₹)</th>
                <th style="width:45px;text-align:center">✕</th>
              </tr>
            </thead>
            <tbody id="q-items-tbody"></tbody>
          </table>
        </div>
      </div>

      <!-- Live Totals Summary Card -->
      <div style="background:var(--panel-2);padding:12px 16px;border-radius:6px;border:1px solid var(--line);margin-bottom:14px;font-size:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div>
            <div style="display:flex;justify-content:space-between;margin-bottom:3px"><span>Item Subtotal:</span><strong id="q-summary-subtotal">INR 0.00</strong></div>
            <div style="display:flex;justify-content:space-between;color:var(--warn)"><span>Total Discount:</span><strong id="q-summary-discount">- INR 0.00</strong></div>
            <div style="display:flex;justify-content:space-between;margin-top:3px;font-weight:600"><span>Taxable Value:</span><strong id="q-summary-taxable">INR 0.00</strong></div>
          </div>
          <div>
            <div style="display:flex;justify-content:space-between;margin-bottom:3px"><span>Total GST Tax:</span><strong id="q-summary-gst">INR 0.00</strong></div>
            <div style="display:flex;justify-content:space-between;font-size:14px;color:var(--accent);margin-top:3px"><span>Grand Total:</span><strong id="q-summary-total">INR 0.00</strong></div>
            <div style="font-size:11px;color:var(--muted);margin-top:3px" id="q-summary-words">Zero Rupees Only</div>
          </div>
        </div>
      </div>

      <div class="form-group" style="margin-bottom:14px">
        <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Payment &amp; Commercial Terms:</label>
        <textarea id="q-terms" rows="2" style="width:100%;font-size:12px">${esc(defaultTerms)}</textarea>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; ${isEdit ? 'Save Changes' : 'Create &amp; Save Quotation'}</button>
      </div>
    </form>
  `;
  showModal(html);
  renderQuotationRows();
}

function renderQuotationRows(){
  window.qActiveItems = qActiveItems;
  const tbody = $("#q-items-tbody");
  if (!tbody) return;
  tbody.innerHTML = qActiveItems.map((it, idx) => `
    <tr class="q-table-row" data-idx="${idx}">
      <td><input class="q-row-name" value="${esc(it.item_name||it.description||'')}" placeholder="Service Title" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateQuotationItemState(${idx}, 'item_name', this.value)" required></td>
      <td><input class="q-row-desc" value="${esc(it.description||'')}" placeholder="Scope Details" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateQuotationItemState(${idx}, 'description', this.value)"></td>
      <td><input class="q-row-qty" type="number" min="0.01" step="any" value="${it.quantity||1}" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateQuotationItemState(${idx}, 'quantity', this.value)"></td>
      <td>
        <select class="q-row-unit" style="width:100%;padding:4px;font-size:11px" onchange="updateQuotationItemState(${idx}, 'unit', this.value)">
          <option value="Acre" ${(it.unit||'Acre')=='Acre'?'selected':''}>Acre</option>
          <option value="Km" ${it.unit=='Km'?'selected':''}>Km</option>
          <option value="Sq Km" ${it.unit=='Sq Km'?'selected':''}>Sq Km</option>
          <option value="Lump Sum" ${it.unit=='Lump Sum'?'selected':''}>Lump Sum</option>
          <option value="Days" ${it.unit=='Days'?'selected':''}>Days</option>
          <option value="Nos" ${it.unit=='Nos'?'selected':''}>Nos</option>
        </select>
      </td>
      <td><input class="q-row-rate" type="number" min="0" step="any" value="${it.rate||0}" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateQuotationItemState(${idx}, 'rate', this.value)"></td>
      <td><input class="q-row-disc" type="number" min="0" step="any" value="${it.discount||0}" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateQuotationItemState(${idx}, 'discount', this.value)"></td>
      <td>
        <select class="q-row-gst" style="width:100%;padding:4px;font-size:11px" onchange="updateQuotationItemState(${idx}, 'gst_rate', this.value)">
          <option value="18" ${(it.gst_rate||18)==18?'selected':''}>18%</option>
          <option value="12" ${it.gst_rate==12?'selected':''}>12%</option>
          <option value="5" ${it.gst_rate==5?'selected':''}>5%</option>
          <option value="0" ${it.gst_rate==0?'selected':''}>0%</option>
        </select>
      </td>
      <td style="text-align:right;font-weight:600;padding-right:8px" class="q-row-line-total">₹ 0.00</td>
      <td style="text-align:center"><button type="button" class="btn btn-secondary btn-sm" style="padding:2px 6px;color:var(--bad)" onclick="removeQuotationItemRow(${idx})">✕</button></td>
    </tr>
  `).join("");
  calculateQuotationLiveTotal();
}

function addQuotationItemRow(){
  const defaultGst = parseFloat($("#q-gst-rate") ? $("#q-gst-rate").value : 18) || 18;
  qActiveItems.push({
    item_name: `Additional Service Item #${qActiveItems.length + 1}`,
    description: "Scope item deliverable",
    unit: "Nos",
    quantity: 1,
    rate: 1000,
    discount: 0,
    gst_rate: defaultGst
  });
  renderQuotationRows();
}

function removeQuotationItemRow(idx){
  if (qActiveItems.length <= 1) {
    toast("Quotation must have at least one line item.", "warn");
    return;
  }
  qActiveItems.splice(idx, 1);
  renderQuotationRows();
}

function updateQuotationItemState(idx, key, val){
  if (!qActiveItems[idx]) return;
  if (key === 'quantity' || key === 'rate' || key === 'discount' || key === 'gst_rate') {
    qActiveItems[idx][key] = Math.max(0, parseFloat(val) || 0);
  } else {
    qActiveItems[idx][key] = val;
  }
  calculateQuotationLiveTotal();
}

function updateDefaultQuotationGst(val){
  const gst = parseFloat(val) || 0;
  qActiveItems.forEach(it => it.gst_rate = gst);
  renderQuotationRows();
}

function calculateQuotationLiveTotal(){
  let subtotal = 0;
  let totalDiscount = 0;
  let totalGst = 0;

  const rows = document.querySelectorAll("#q-items-tbody tr");
  qActiveItems.forEach((it, idx) => {
    const qty = Math.max(0, parseFloat(it.quantity) || 0);
    const rate = Math.max(0, parseFloat(it.rate) || 0);
    const disc = Math.max(0, parseFloat(it.discount) || 0);
    const gstRate = parseFloat(it.gst_rate) || 0;

    const base = qty * rate;
    const taxable = Math.max(0, base - disc);
    const gst = Math.round(taxable * (gstRate / 100) * 100) / 100;
    const lineTotal = taxable + gst;

    subtotal += base;
    totalDiscount += disc;
    totalGst += gst;

    if (rows[idx]) {
      const totalCell = rows[idx].querySelector(".q-row-line-total");
      if (totalCell) totalCell.textContent = `₹ ${lineTotal.toLocaleString('en-IN', {minimumFractionDigits:2, maximumFractionDigits:2})}`;
    }
  });

  const taxableTotal = Math.max(0, subtotal - totalDiscount);
  const grandTotal = taxableTotal + totalGst;

  if ($("#q-summary-subtotal")) $("#q-summary-subtotal").textContent = `INR ${subtotal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if ($("#q-summary-discount")) $("#q-summary-discount").textContent = `- INR ${totalDiscount.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if ($("#q-summary-taxable")) $("#q-summary-taxable").textContent = `INR ${taxableTotal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if ($("#q-summary-gst")) $("#q-summary-gst").textContent = `INR ${totalGst.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if ($("#q-summary-total")) $("#q-summary-total").textContent = `INR ${grandTotal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
}

async function submitDynamicQuotation(e, editId = null){
  e.preventDefault();
  const validItems = qActiveItems.filter(it => it.item_name && it.item_name.trim());
  if (!validItems.length) {
    toast("Please enter at least one valid line item.", "bad");
    return;
  }

  const payload = {
    workspace_id: state.ws,
    project_name: $("#q-project-name").value.trim(),
    client_name: $("#q-client-name").value.trim(),
    client_contact: $("#q-client-contact").value.trim(),
    validity_days: parseInt($("#q-validity").value) || 30,
    gst_rate: parseFloat($("#q-gst-rate").value) || 18,
    terms: $("#q-terms").value.trim(),
    items: validItems
  };

  try{
    if (editId) {
      await api(`/api/quotations/${editId}?workspace=${state.ws}`, { method: "PUT", body: payload });
      toast("Quotation updated successfully!", "ok");
    } else {
      await api(`/api/quotations?workspace=${state.ws}`, { method: "POST", body: payload });
      toast("Quotation created and registered successfully!", "ok");
    }
    closeModal();
    await refreshFinanceData();
  }catch(err){
    toast("Error saving quotation: " + err.message, "bad");
  }
}

async function openEditQuotationModal(qid){
  try{
    const j = await api(`/api/quotations/${qid}?workspace=${state.ws}`);
    if (j.quotation) openNewQuotationModal(j.quotation);
  }catch(e){ toast("Failed to load quotation: " + e.message, "bad"); }
}

async function openViewQuotationModal(qid){
  try{
    const j = await api(`/api/quotations/${qid}?workspace=${state.ws}`);
    const q = j.quotation;
    if (!q) return toast("Quotation not found", "bad");
    const items = q.items || [];

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:10px">
        <h3 style="margin:0">&#128221; Proposal Preview: ${esc(q.quotation_number)}</h3>
        <div style="display:flex;gap:8px">
          <button class="btn btn-secondary btn-sm" onclick="window.print()">&#128424; Print / PDF</button>
          <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
        </div>
      </div>
      <div id="print-quotation-document" style="background:#fff;color:#000;padding:20px;border-radius:6px;font-family:sans-serif;font-size:12px;line-height:1.4">
        <div style="display:flex;justify-content:space-between;border-bottom:2px solid #0047AB;padding-bottom:12px;margin-bottom:12px">
          <div>
            <h2 style="margin:0;color:#0047AB;font-size:20px">SHAH GROUP OF ENTERPRISES</h2>
            <div style="font-size:11px;color:#555">Shah Survey &amp; Consultants | Shah Infrastructure &amp; Construction</div>
            <div style="font-size:11px;color:#555">GSTIN: 27AABCS1234F1Z5 | PAN: AABCS1234F</div>
          </div>
          <div style="text-align:right">
            <h3 style="margin:0;color:#333;font-size:16px">COMMERCIAL QUOTATION</h3>
            <div><strong>Ref:</strong> ${esc(q.quotation_number)}</div>
            <div><strong>Date:</strong> ${(q.created_at||'').split(' ')[0]}</div>
            <div><strong>Validity:</strong> ${q.validity_days||30} Days</div>
          </div>
        </div>

        <div style="margin-bottom:12px;background:#f8f9fa;padding:10px;border-radius:4px">
          <div><strong>Quotation For:</strong> ${esc(q.client_name||'Valued Client')}</div>
          <div><strong>Project Scope:</strong> ${esc(q.project_name||'')}</div>
          <div><strong>Contact:</strong> ${esc(q.client_contact||'—')}</div>
        </div>

        <table style="width:100%;border-collapse:collapse;margin-bottom:14px">
          <thead>
            <tr style="background:#0047AB;color:#fff">
              <th style="padding:6px;text-align:left;border:1px solid #ddd">#</th>
              <th style="padding:6px;text-align:left;border:1px solid #ddd">Item / Deliverable</th>
              <th style="padding:6px;text-align:left;border:1px solid #ddd">Description</th>
              <th style="padding:6px;text-align:center;border:1px solid #ddd">Qty</th>
              <th style="padding:6px;text-align:center;border:1px solid #ddd">Unit</th>
              <th style="padding:6px;text-align:right;border:1px solid #ddd">Rate (₹)</th>
              <th style="padding:6px;text-align:right;border:1px solid #ddd">Total (₹)</th>
            </tr>
          </thead>
          <tbody>
            ${items.map((it, idx)=>`
              <tr>
                <td style="padding:6px;border:1px solid #ddd">${idx+1}</td>
                <td style="padding:6px;border:1px solid #ddd;font-weight:600">${esc(it.item_name||it.description)}</td>
                <td style="padding:6px;border:1px solid #ddd;color:#555">${esc(it.description||'')}</td>
                <td style="padding:6px;border:1px solid #ddd;text-align:center">${it.quantity||1}</td>
                <td style="padding:6px;border:1px solid #ddd;text-align:center">${esc(it.unit||'Nos')}</td>
                <td style="padding:6px;border:1px solid #ddd;text-align:right">${Number(it.rate||0).toLocaleString('en-IN', {minimumFractionDigits:2})}</td>
                <td style="padding:6px;border:1px solid #ddd;text-align:right;font-weight:600">${Number(it.amount||(it.quantity*it.rate)).toLocaleString('en-IN', {minimumFractionDigits:2})}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <div style="display:flex;justify-content:flex-end;margin-bottom:14px">
          <div style="width:280px">
            <div style="display:flex;justify-content:space-between;padding:3px 0"><span>Subtotal:</span><span>₹ ${Number(q.subtotal||0).toLocaleString('en-IN', {minimumFractionDigits:2})}</span></div>
            <div style="display:flex;justify-content:space-between;padding:3px 0"><span>Discount:</span><span>- ₹ ${Number(q.discount_total||0).toLocaleString('en-IN', {minimumFractionDigits:2})}</span></div>
            <div style="display:flex;justify-content:space-between;padding:3px 0"><span>GST (${q.gst_rate||18}%):</span><span>₹ ${Number(q.gst_amount||0).toLocaleString('en-IN', {minimumFractionDigits:2})}</span></div>
            <div style="display:flex;justify-content:space-between;padding:6px 0;border-top:2px solid #0047AB;font-size:14px;font-weight:bold;color:#0047AB"><span>Grand Total:</span><span>₹ ${Number(q.total_amount||0).toLocaleString('en-IN', {minimumFractionDigits:2})}</span></div>
          </div>
        </div>

        <div style="margin-bottom:14px;background:#fdfdfd;padding:8px;border:1px solid #eee;border-radius:4px">
          <strong>Terms &amp; Conditions:</strong>
          <div style="color:#555;margin-top:2px">${esc(q.terms||'Standard 30 days validity. 50% advance with work order.')}</div>
        </div>

        <div style="display:flex;justify-content:space-between;margin-top:20px;padding-top:10px;border-top:1px dashed #ccc">
          <div>Authorized Client Acceptance &amp; Stamp</div>
          <div style="text-align:right">For SHAH GROUP OF ENTERPRISES<br><br><strong>Authorized Signatory</strong></div>
        </div>
      </div>
    `);
  }catch(e){ toast("Error viewing quotation: " + e.message, "bad"); }
}


// ------------------------------------------------------------------------------
// 2. SURVEY SITE LIFECYCLE & FINANCIAL TRACKING
// ------------------------------------------------------------------------------

let activeSiteLifecycleCategory = 'all';

async function renderSites(categoryFilter = null){
  if (categoryFilter !== null) activeSiteLifecycleCategory = categoryFilter;
  const sitesBox = $("#project-sites");
  if (!sitesBox) return;

  try{
    const j = await api(`/api/sites?category=${activeSiteLifecycleCategory}&workspace=${state.ws}`);
    const sites = j.sites || [];

    sitesBox.innerHTML = sites.length ? `
      <table>
        <thead>
          <tr>
            <th>Site Code</th>
            <th>Site Name &amp; Scope</th>
            <th>Client &amp; Location</th>
            <th>Schedule &amp; Dates</th>
            <th>Team &amp; Equipment</th>
            <th>Survey Status</th>
            <th>Financials (Value / Balance)</th>
            <th style="text-align:right">Actions</th>
          </tr>
        </thead>
        <tbody>
          ${sites.map(s => {
            const scat = s.schedule_category || 'Active Site';
            let catPill = 'info';
            if (scat.includes('Today')) catPill = 'ok';
            else if (scat.includes('Tomorrow')) catPill = 'warn';
            else if (scat.includes('Overdue')) catPill = 'bad';
            else if (scat.includes('Completed')) catPill = 'ok';

            const teamList = Array.isArray(s.assigned_team) ? s.assigned_team : [];
            const balDue = parseFloat(s.balance_due || 0);

            return `
              <tr>
                <td><strong>${esc(s.code)}</strong></td>
                <td>
                  <strong>${esc(s.name)}</strong>
                  <div style="font-size:11px;color:var(--muted)">${esc(s.survey_type||'Topographic')} | ${esc((s.scope_of_work||'').substring(0, 35))}</div>
                </td>
                <td>
                  <div>${esc(s.client_name||'Direct Client')}</div>
                  <div style="font-size:11px;color:var(--muted)">${esc(s.project_location||s.address||'—')}</div>
                </td>
                <td>
                  <span class="pill ${catPill}">${esc(scat)}</span>
                  <div style="font-size:11px;color:var(--muted);margin-top:2px">Start: ${esc(s.start_date||'—')}</div>
                </td>
                <td>
                  <div><strong>Lead:</strong> ${esc(s.team_leader||'Unassigned')}</div>
                  <div style="font-size:11px;color:var(--muted)">${teamList.length} staff | ${(s.equipment_assigned||[]).length} tools</div>
                </td>
                <td>
                  <button class="pill ok" style="cursor:pointer;border:0" onclick="openUpdateSiteStatusModal(${s.id})">${esc(s.survey_status||'Site Scheduled')} ▾</button>
                </td>
                <td>
                  <div>₹ ${Number(s.project_value||0).toLocaleString('en-IN')}</div>
                  <div style="font-size:11px;color:${balDue>0?'var(--warn)':'var(--good)'}">
                    <strong>Bal:</strong> ₹ ${Number(balDue).toLocaleString('en-IN')} (${esc(s.payment_status||'Pending')})
                  </div>
                </td>
                <td style="text-align:right">
                  <div style="display:flex;gap:4px;justify-content:flex-end">
                    <button class="btn btn-secondary btn-sm" onclick="openUpdateSiteStatusModal(${s.id})" title="Update Survey Status">&#128221;</button>
                    <button class="btn btn-secondary btn-sm" onclick="openUpdateSitePaymentModal(${s.id})" title="Financial Tracking &amp; Payment">&#128176;</button>
                    <button class="btn btn-secondary btn-sm" onclick="openSiteDetailsModal(${s.id})" title="View Complete Site Log">&#128269;</button>
                  </div>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    ` : `<div class="empty">No survey sites found for filter: "${activeSiteLifecycleCategory}". Click "+ Add Survey Site" above.</div>`;

  }catch(e){
    sitesBox.innerHTML = `<div class="empty">Error loading sites: ${esc(e.message)}</div>`;
  }
}

function filterSitesLifecycle(cat, btn){
  if (btn && btn.parentElement) {
    btn.parentElement.querySelectorAll("button").forEach(b => b.classList.remove("active", "btn-primary"));
    btn.classList.add("active", "btn-primary");
  }
  renderSites(cat);
}

function openNewSiteModal(){
  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#128205; Schedule New Survey Project Site</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form id="form-new-site" onsubmit="submitNewSite(event)">
      <div style="display:flex;gap:6px;margin-bottom:14px;border-bottom:1px solid var(--line);padding-bottom:8px" id="modal-site-tabs">
        <button type="button" class="btn btn-secondary btn-sm active" onclick="switchSiteModalTab('scope', this)">1. Scope &amp; Location</button>
        <button type="button" class="btn btn-secondary btn-sm" onclick="switchSiteModalTab('team', this)">2. Team &amp; Logistics</button>
        <button type="button" class="btn btn-secondary btn-sm" onclick="switchSiteModalTab('finance', this)">3. Financials</button>
      </div>

      <!-- Tab 1: Scope & Location -->
      <div id="site-tab-scope">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Site / Project Name:</label><input id="s-name" required placeholder="e.g. NH-44 Alignment Topo Survey" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Site Code:</label><input id="s-code" placeholder="Auto-generated if blank (e.g. SITE-SSC-001)" style="width:100%"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Client Name / Agency:</label><input id="s-client" required placeholder="e.g. NHAI / PWD" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Project Location / City:</label><input id="s-location" required placeholder="e.g. Nagpur to Seoni Section" style="width:100%"></div>
        </div>
        <div class="form-group" style="margin-bottom:10px">
          <label style="font-size:11px;font-weight:600">Complete Address / Base Camp:</label>
          <input id="s-address" placeholder="Toll Plaza Camp, NH-44 Chainage 240+000" style="width:100%">
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div>
            <label style="font-size:11px;font-weight:600">Survey Type:</label>
            <select id="s-type" style="width:100%">
              <option value="DGPS RTK Geodetic Survey">DGPS RTK Geodetic Survey</option>
              <option value="Drone LiDAR &amp; Photogrammetry">Drone LiDAR &amp; Photogrammetry</option>
              <option value="Highway Final Location Survey (FLS)">Highway Final Location Survey (FLS)</option>
              <option value="Topographic &amp; Contour Survey">Topographic &amp; Contour Survey</option>
              <option value="Bathymetric Hydrographic Survey">Bathymetric Hydrographic Survey</option>
              <option value="Subsurface Utility Mapping (GPR)">Subsurface Utility Mapping (GPR)</option>
              <option value="Cadastral &amp; Boundary Demarcation">Cadastral &amp; Boundary Demarcation</option>
            </select>
          </div>
          <div><label style="font-size:11px;font-weight:600">GPS Coordinates / Map Link:</label><input id="s-coords" placeholder="21.1458 N, 79.0882 E / Google Maps link" style="width:100%"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div><label style="font-size:11px;font-weight:600">Survey Start Date:</label><input id="s-start-date" type="date" value="${new Date().toISOString().split('T')[0]}" required style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Expected Completion Date:</label><input id="s-end-date" type="date" value="${new Date(Date.now()+15*86400000).toISOString().split('T')[0]}" style="width:100%"></div>
        </div>
      </div>

      <!-- Tab 2: Team & Logistics -->
      <div id="site-tab-team" style="display:none">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Designated Team Leader:</label><input id="s-leader" placeholder="Senior Surveyor Name" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Assigned Team Members (comma-sep):</label><input id="s-team" placeholder="Vikram Singh, Rahul Verma, Ankit" style="width:100%"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Assigned Survey Equipment:</label><input id="s-equipment" placeholder="CHCNav i90 DGPS (Base+Rover), DJI Matrice 350 RTK" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Vehicle / Transport Mode:</label><input id="s-transport" placeholder="Bolero Camper (MH-31-CB-4040)" style="width:100%"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Estimated Field Expenses (₹):</label><input id="s-expenses" type="number" placeholder="25000" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Site Contact Person &amp; Phone:</label><input id="s-contact" placeholder="Mr. Deshmukh (+91 98220 55443)" style="width:100%"></div>
        </div>
        <div class="form-group">
          <label style="font-size:11px;font-weight:600">Special Field Instructions / Safety Protocol:</label>
          <textarea id="s-instructions" rows="2" placeholder="Strict compliance with MoRTH Section 100 accuracy tolerances. High-visibility PPE mandatory." style="width:100%"></textarea>
        </div>
      </div>

      <!-- Tab 3: Financials -->
      <div id="site-tab-finance" style="display:none">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Total Project / Work Order Value (₹):</label><input id="s-value" type="number" placeholder="250000" value="250000" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Advance Payment Received (₹):</label><input id="s-advance" type="number" placeholder="50000" value="50000" style="width:100%"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Payment Due Date:</label><input id="s-due-date" type="date" value="${new Date(Date.now()+30*86400000).toISOString().split('T')[0]}" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Initial Survey Status:</label>
            <select id="s-status" style="width:100%">
              <option value="Site Scheduled" selected>Site Scheduled</option>
              <option value="Team Assigned">Team Assigned</option>
              <option value="Travel Planned">Travel Planned</option>
              <option value="Survey Pending">Survey Pending</option>
            </select>
          </div>
        </div>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px;border-top:1px solid var(--line);padding-top:10px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Save &amp; Schedule Site</button>
      </div>
    </form>
  `;
  showModal(html);
}

function switchSiteModalTab(tab, btn){
  ["scope", "team", "finance"].forEach(t => {
    const el = $("#site-tab-" + t);
    if (el) el.style.display = (t === tab) ? "block" : "none";
  });
  if (btn && btn.parentElement) {
    btn.parentElement.querySelectorAll("button").forEach(b => b.classList.remove("active", "btn-primary"));
    btn.classList.add("active", "btn-primary");
  }
}

async function submitNewSite(e){
  e.preventDefault();
  const teamList = $("#s-team").value.split(",").map(x => x.trim()).filter(Boolean);
  const equipList = $("#s-equipment").value.split(",").map(x => x.trim()).filter(Boolean);

  const payload = {
    workspace_id: state.ws,
    name: $("#s-name").value.trim(),
    code: $("#s-code").value.trim() || undefined,
    client_name: $("#s-client").value.trim(),
    project_location: $("#s-location").value.trim(),
    complete_address: $("#s-address").value.trim(),
    survey_type: $("#s-type").value,
    coordinates: $("#s-coords").value.trim(),
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
    payment_due_date: $("#s-due-date").value,
    survey_status: $("#s-status").value
  };

  try{
    await api("/api/sites", { method: "POST", body: payload });
    toast("Survey site scheduled successfully!", "ok");
    closeModal();
    await renderSites();
  }catch(err){
    toast("Error scheduling site: " + err.message, "bad");
  }
}

async function openUpdateSiteStatusModal(siteId){
  try{
    const j = await api(`/api/sites/${siteId}?workspace=${state.ws}`);
    const s = j.site;
    if (!s) return toast("Site not found", "bad");
    const history = s.status_history || [];

    const statuses = [
      "Site Scheduled", "Team Assigned", "Travel Planned", "Survey Pending",
      "Survey In Progress", "Field Survey Completed", "Data Processing",
      "Report Preparation", "Report Under Review", "Report Completed",
      "Report Submitted", "Client Approval Pending", "Payment Pending",
      "Partially Paid", "Payment Received", "Closed"
    ];

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:8px">
        <h3 style="margin:0">&#128221; Update Survey Status: ${esc(s.name)} (${esc(s.code)})</h3>
        <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
      </div>
      <form onsubmit="submitSiteStatusChange(event, ${siteId})">
        <div class="form-group" style="margin-bottom:12px">
          <label style="font-size:11px;font-weight:600">Select New Survey Lifecycle Status:</label>
          <select id="update-site-status-select" style="width:100%;font-size:13px;padding:6px">
            ${statuses.map(st => `<option value="${st}" ${st===s.survey_status?'selected':''}>${st}</option>`).join('')}
          </select>
        </div>
        <div class="form-group" style="margin-bottom:12px">
          <label style="font-size:11px;font-weight:600">Operational Notes / Remarks:</label>
          <input id="update-site-remarks" placeholder="e.g. Field GPS logging completed; RAW RINEX data transferred to CAD server" style="width:100%" required>
        </div>

        <h4 style="margin:14px 0 6px">&#128338; Timestamped Audit History Timeline:</h4>
        <div style="max-height:160px;overflow-y:auto;border:1px solid var(--line);border-radius:4px;padding:8px;background:var(--panel-2);font-size:12px">
          ${history.length ? history.map(h => `
            <div style="border-bottom:1px solid var(--line);padding:4px 0">
              <span class="pill ok" style="font-size:10px">${esc(h.status)}</span>
              <span style="font-weight:600;margin-left:6px">${esc(h.changed_by||'User')}</span>
              <span style="color:var(--muted);font-size:10px;margin-left:6px">${esc(h.timestamp)}</span>
              <div style="color:var(--muted);margin-top:2px">${esc(h.remarks||'')}</div>
            </div>
          `).join('') : '<div class="muted">No prior transitions logged.</div>'}
        </div>

        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">&#10003; Commit Status Change</button>
        </div>
      </form>
    `);
  }catch(e){ toast("Error loading site: " + e.message, "bad"); }
}

async function submitSiteStatusChange(e, siteId){
  e.preventDefault();
  const newStatus = $("#update-site-status-select").value;
  const remarks = $("#update-site-remarks").value.trim();

  try{
    await api(`/api/sites/${siteId}/status?workspace=${state.ws}`, {
      method: "POST",
      body: { survey_status: newStatus, remarks }
    });
    toast(`Site status updated to "${newStatus}"`, "ok");
    closeModal();
    await renderSites();
  }catch(err){
    toast("Error updating status: " + err.message, "bad");
  }
}

async function openUpdateSitePaymentModal(siteId){
  try{
    const j = await api(`/api/sites/${siteId}?workspace=${state.ws}`);
    const s = j.site;
    if (!s) return toast("Site not found", "bad");

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:8px">
        <h3 style="margin:0">&#128176; Financial Tracking &amp; Payment: ${esc(s.name)}</h3>
        <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
      </div>
      <form onsubmit="submitSitePaymentUpdate(event, ${siteId})">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Total Work Order Value (₹):</label><input id="pay-val" type="number" value="${s.project_value||0}" style="width:100%" oninput="calcSitePaymentBalance()"></div>
          <div><label style="font-size:11px;font-weight:600">Total Billed to Client (₹):</label><input id="pay-billed" type="number" value="${s.total_billed||s.project_value||0}" style="width:100%" oninput="calcSitePaymentBalance()"></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Advance Received (₹):</label><input id="pay-adv" type="number" value="${s.advance_received||0}" style="width:100%" oninput="calcSitePaymentBalance()"></div>
          <div><label style="font-size:11px;font-weight:600">Subsequent Payment Received (₹):</label><input id="pay-rec" type="number" value="${s.payment_received||0}" style="width:100%" oninput="calcSitePaymentBalance()"></div>
        </div>
        <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line);margin-bottom:12px;font-size:12px">
          <div style="display:flex;justify-content:space-between"><span>Total Collected:</span><strong id="pay-preview-collected">₹ 0.00</strong></div>
          <div style="display:flex;justify-content:space-between;margin-top:3px;font-size:14px;color:var(--warn)"><span>Outstanding Balance Due:</span><strong id="pay-preview-balance">₹ 0.00</strong></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div><label style="font-size:11px;font-weight:600">Invoice Number Generated:</label><input id="pay-inv-num" value="${esc(s.invoice_generated||'')}" placeholder="e.g. INV-SSC-2026-0001" style="width:100%"></div>
          <div><label style="font-size:11px;font-weight:600">Payment Due Date:</label><input id="pay-due" type="date" value="${s.payment_due_date||''}" style="width:100%"></div>
        </div>
        <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">&#10003; Update Payment Records</button>
        </div>
      </form>
    `);
    calcSitePaymentBalance();
  }catch(e){ toast("Error loading site financials: " + e.message, "bad"); }
}

function calcSitePaymentBalance(){
  const billed = parseFloat($("#pay-billed") ? $("#pay-billed").value : 0) || 0;
  const adv = parseFloat($("#pay-adv") ? $("#pay-adv").value : 0) || 0;
  const rec = parseFloat($("#pay-rec") ? $("#pay-rec").value : 0) || 0;
  const collected = adv + rec;
  const bal = Math.max(0, billed - collected);

  if ($("#pay-preview-collected")) $("#pay-preview-collected").textContent = `₹ ${collected.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if ($("#pay-preview-balance")) $("#pay-preview-balance").textContent = `₹ ${bal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
}

async function submitSitePaymentUpdate(e, siteId){
  e.preventDefault();
  const payload = {
    project_value: parseFloat($("#pay-val").value) || 0,
    total_billed: parseFloat($("#pay-billed").value) || 0,
    advance_received: parseFloat($("#pay-adv").value) || 0,
    payment_received: parseFloat($("#pay-rec").value) || 0,
    invoice_generated: $("#pay-inv-num").value.trim(),
    payment_due_date: $("#pay-due").value
  };

  try{
    await api(`/api/sites/${siteId}/payment?workspace=${state.ws}`, {
      method: "POST",
      body: payload
    });
    toast("Site financial records updated successfully!", "ok");
    closeModal();
    await renderSites();
  }catch(err){
    toast("Error updating payment: " + err.message, "bad");
  }
}

async function openSiteDetailsModal(siteId){
  try{
    const j = await api(`/api/sites/${siteId}?workspace=${state.ws}`);
    const s = j.site;
    if (!s) return toast("Site not found", "bad");

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:8px">
        <h3 style="margin:0">&#128205; Site Lifecycle Log: ${esc(s.name)} (${esc(s.code)})</h3>
        <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;margin-bottom:14px">
        <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line)">
          <div><strong>Client:</strong> ${esc(s.client_name||'Direct Client')}</div>
          <div><strong>Location:</strong> ${esc(s.project_location||s.address||'—')}</div>
          <div><strong>Coordinates:</strong> ${esc(s.coordinates||'—')}</div>
          <div><strong>Survey Type:</strong> <span class="pill info">${esc(s.survey_type||'Topographic')}</span></div>
          <div><strong>Schedule:</strong> <span class="pill ok">${esc(s.schedule_category||'Active')}</span> (${esc(s.start_date||'—')})</div>
        </div>
        <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line)">
          <div><strong>Team Leader:</strong> ${esc(s.team_leader||'Unassigned')}</div>
          <div><strong>Field Staff:</strong> ${(s.assigned_team||[]).join(', ')||'None logged'}</div>
          <div><strong>Equipment:</strong> ${(s.equipment_assigned||[]).join(', ')||'None logged'}</div>
          <div><strong>Transport:</strong> ${esc(s.transport_details||'—')}</div>
          <div><strong>Site Contact:</strong> ${esc(s.site_contact_person||'—')}</div>
        </div>
      </div>
      <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line);font-size:12px;margin-bottom:14px">
        <div style="display:flex;justify-content:space-between">
          <span>Project Value: <strong>₹ ${Number(s.project_value||0).toLocaleString('en-IN')}</strong></span>
          <span>Advance: <strong>₹ ${Number(s.advance_received||0).toLocaleString('en-IN')}</strong></span>
          <span>Balance Due: <strong style="color:var(--warn)">₹ ${Number(s.balance_due||0).toLocaleString('en-IN')}</strong></span>
          <span>Payment Status: <span class="pill ${s.balance_due>0?'warn':'ok'}">${esc(s.payment_status||'Pending')}</span></span>
        </div>
      </div>
      <div style="display:flex;justify-content:flex-end">
        <button class="btn btn-secondary" onclick="closeModal()">Close</button>
      </div>
    `);
  }catch(e){ toast("Error opening site details: " + e.message, "bad"); }
}


// ------------------------------------------------------------------------------
// 3. NON-GST BILLING SYSTEM (COMMERCIAL BILL OF SUPPLY)
// ------------------------------------------------------------------------------

var nonGstActiveItems = [];
window.nonGstActiveItems = nonGstActiveItems;

function openNewNonGSTBillModal(){
  nonGstActiveItems = [
    { item: "Site Topographic Alignment Survey", unit: "Acre", quantity: 20, rate: 1000 }
  ];

  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#129534; Create Non-GST Commercial Bill (Bill of Supply)</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <div style="background:rgba(2, 132, 199, 0.1);border:1px solid var(--accent);padding:8px 12px;border-radius:4px;font-size:11px;margin-bottom:12px;color:var(--accent)">
      &#9432; <strong>Legally Compliant Non-GST Bill:</strong> Strictly zero GST taxes, no CGST/SGST/IGST breakdown, and no tax liability. Operates with independent sequential numbering (BILL-YYYY-XXXX).
    </div>
    <form id="form-nongst-bill" onsubmit="submitNonGSTBill(event)">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div><label style="font-size:11px;font-weight:600">Client / Billed To Name:</label><input id="ng-client-name" required placeholder="e.g. Siddharth Infra Pvt Ltd" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">Client Contact / Mobile:</label><input id="ng-client-contact" placeholder="+91 94250 88990" style="width:100%"></div>
      </div>
      <div class="form-group" style="margin-bottom:10px">
        <label style="font-size:11px;font-weight:600">Client Billing Address:</label>
        <input id="ng-client-address" placeholder="MIDC Industrial Area, Hingna, Nagpur" style="width:100%">
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px">
        <div><label style="font-size:11px;font-weight:600">Bill Date:</label><input id="ng-bill-date" type="date" value="${new Date().toISOString().split('T')[0]}" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">Payment Due Date:</label><input id="ng-due-date" type="date" value="${new Date(Date.now()+15*86400000).toISOString().split('T')[0]}" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">Payment Mode:</label>
          <select id="ng-pay-mode" style="width:100%">
            <option value="NEFT / RTGS">NEFT / RTGS Bank Transfer</option>
            <option value="Cheque">Account Payee Cheque</option>
            <option value="Cash">Cash Receipt</option>
            <option value="UPI">UPI Digital Payment</option>
          </select>
        </div>
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <label style="font-size:12px;font-weight:700">Services &amp; Work Description Items:</label>
        <button type="button" class="btn btn-secondary btn-sm" onclick="addNonGstRow()">+ Add Item</button>
      </div>

      <div style="border:1px solid var(--line);border-radius:4px;overflow:hidden;margin-bottom:12px;background:var(--panel)">
        <table style="width:100%;font-size:12px;margin:0">
          <thead>
            <tr>
              <th style="min-width:200px">Work Item Description</th>
              <th style="width:80px">Qty</th>
              <th style="width:90px">Unit</th>
              <th style="width:100px">Rate (₹)</th>
              <th style="width:110px;text-align:right">Amount (₹)</th>
              <th style="width:40px;text-align:center">✕</th>
            </tr>
          </thead>
          <tbody id="ng-items-tbody"></tbody>
        </table>
      </div>

      <div style="background:var(--panel-2);padding:10px 14px;border-radius:4px;border:1px solid var(--line);margin-bottom:12px;font-size:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div>
            <div style="display:flex;justify-content:space-between"><span>Subtotal:</span><strong id="ng-preview-subtotal">INR 0.00</strong></div>
            <div style="display:flex;justify-content:space-between;color:var(--warn);margin-top:3px">
              <span>Discount (₹):</span>
              <input id="ng-discount" type="number" min="0" value="0" style="width:100px;font-size:11px;padding:2px 4px;text-align:right" oninput="calculateNonGstLiveTotal()">
            </div>
          </div>
          <div>
            <div style="display:flex;justify-content:space-between;font-size:14px;color:var(--good)"><span>Total Bill Value:</span><strong id="ng-preview-total">INR 0.00</strong></div>
            <div style="font-size:11px;color:var(--muted);margin-top:2px" id="ng-preview-words">Zero Rupees Only</div>
          </div>
        </div>
      </div>

      <div class="form-group" style="margin-bottom:12px">
        <label style="font-size:11px;font-weight:600">Notes &amp; Commercial Terms:</label>
        <textarea id="ng-notes" rows="2" style="width:100%;font-size:12px">Non-taxable supply. Payment due upon presentation.</textarea>
      </div>

      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Issue Non-GST Bill</button>
      </div>
    </form>
  `;
  showModal(html);
  renderNonGstRows();
}

function renderNonGstRows(){
  window.nonGstActiveItems = nonGstActiveItems;
  const tbody = $("#ng-items-tbody");
  if (!tbody) return;
  tbody.innerHTML = nonGstActiveItems.map((it, idx) => `
    <tr>
      <td><input class="ng-row-item" value="${esc(it.item||'')}" placeholder="Description of service rendered" style="width:100%;padding:4px 6px;font-size:12px" oninput="nonGstActiveItems[${idx}].item=this.value" required></td>
      <td><input class="ng-row-qty" type="number" min="0.01" step="any" value="${it.quantity||1}" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateNonGstItem(${idx}, 'quantity', this.value)"></td>
      <td>
        <select class="ng-row-unit" style="width:100%;padding:4px;font-size:11px" onchange="nonGstActiveItems[${idx}].unit=this.value">
          <option value="Acre" ${(it.unit||'Acre')=='Acre'?'selected':''}>Acre</option>
          <option value="Km" ${it.unit=='Km'?'selected':''}>Km</option>
          <option value="Lump Sum" ${it.unit=='Lump Sum'?'selected':''}>Lump Sum</option>
          <option value="Days" ${it.unit=='Days'?'selected':''}>Days</option>
          <option value="Nos" ${it.unit=='Nos'?'selected':''}>Nos</option>
        </select>
      </td>
      <td><input class="ng-row-rate" type="number" min="0" step="any" value="${it.rate||0}" style="width:100%;padding:4px 6px;font-size:12px" oninput="updateNonGstItem(${idx}, 'rate', this.value)"></td>
      <td style="text-align:right;font-weight:600;padding-right:8px" class="ng-row-amount">₹ 0.00</td>
      <td style="text-align:center"><button type="button" class="btn btn-secondary btn-sm" style="padding:2px 6px;color:var(--bad)" onclick="removeNonGstRow(${idx})">✕</button></td>
    </tr>
  `).join("");
  calculateNonGstLiveTotal();
}

function addNonGstRow(){
  nonGstActiveItems.push({ item: "Additional Professional Service", unit: "Lump Sum", quantity: 1, rate: 5000 });
  renderNonGstRows();
}

function removeNonGstRow(idx){
  if (nonGstActiveItems.length <= 1) {
    toast("Bill must have at least one item.", "warn");
    return;
  }
  nonGstActiveItems.splice(idx, 1);
  renderNonGstRows();
}

function updateNonGstItem(idx, key, val){
  if (!nonGstActiveItems[idx]) return;
  nonGstActiveItems[idx][key] = Math.max(0, parseFloat(val) || 0);
  calculateNonGstLiveTotal();
}

function calculateNonGstLiveTotal(){
  let subtotal = 0;
  const rows = document.querySelectorAll("#ng-items-tbody tr");
  nonGstActiveItems.forEach((it, idx) => {
    const qty = Math.max(0, parseFloat(it.quantity) || 0);
    const rate = Math.max(0, parseFloat(it.rate) || 0);
    const lineAmt = qty * rate;
    subtotal += lineAmt;
    if (rows[idx]) {
      const amtCell = rows[idx].querySelector(".ng-row-amount");
      if (amtCell) amtCell.textContent = `₹ ${lineAmt.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
    }
  });

  const disc = parseFloat($("#ng-discount") ? $("#ng-discount").value : 0) || 0;
  const grandTotal = Math.max(0, subtotal - disc);

  if ($("#ng-preview-subtotal")) $("#ng-preview-subtotal").textContent = `INR ${subtotal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
  if ($("#ng-preview-total")) $("#ng-preview-total").textContent = `INR ${grandTotal.toLocaleString('en-IN', {minimumFractionDigits:2})}`;
}

async function submitNonGSTBill(e){
  e.preventDefault();
  const validItems = nonGstActiveItems.filter(it => it.item && it.item.trim());
  if (!validItems.length) {
    toast("Please enter at least one valid line item.", "bad");
    return;
  }

  const payload = {
    workspace_id: state.ws,
    bill_type: "NON_GST",
    client_name: $("#ng-client-name").value.trim(),
    client_address: $("#ng-client-address").value.trim(),
    client_contact: $("#ng-client-contact").value.trim(),
    invoice_date: $("#ng-bill-date").value,
    due_date: $("#ng-due-date").value,
    payment_mode: $("#ng-pay-mode").value,
    discount_amount: parseFloat($("#ng-discount").value) || 0,
    notes: $("#ng-notes").value.trim(),
    items: validItems
  };

  try{
    await api(`/api/bills?workspace=${state.ws}`, { method: "POST", body: payload });
    toast("Non-GST Commercial Bill issued successfully!", "ok");
    closeModal();
    await refreshFinanceData();
  }catch(err){
    toast("Error creating bill: " + err.message, "bad");
  }
}


// ------------------------------------------------------------------------------
// 4. REGISTERED VENDOR MANAGEMENT
// ------------------------------------------------------------------------------

let activeVendorStatusFilter = 'all';

async function renderRegisteredVendors(statusFilter = null){
  if (statusFilter !== null) activeVendorStatusFilter = statusFilter;
  const box = $("#finance-vendors");
  if (!box) return;

  try{
    const j = await api(`/api/vendors?status=${activeVendorStatusFilter}&workspace=${state.ws}`);
    const vendors = j.vendors || [];

    box.innerHTML = vendors.length ? `
      <table>
        <thead>
          <tr>
            <th>Company / Vendor Name</th>
            <th>Category</th>
            <th>Contact Person &amp; Phone</th>
            <th>Location (City, State)</th>
            <th>GSTIN / PAN / MSME</th>
            <th>Status</th>
            <th style="text-align:right">Actions</th>
          </tr>
        </thead>
        <tbody>
          ${vendors.map(v => {
            let sPill = 'info';
            if (v.status === 'Approved' || v.status === 'Active') sPill = 'ok';
            else if (v.status === 'Rejected') sPill = 'bad';
            else sPill = 'warn';

            return `
              <tr>
                <td>
                  <strong>${esc(v.company_name||v.name)}</strong>
                  <div style="font-size:11px;color:var(--muted)">${esc(v.services_supplied||'Services Supplier')}</div>
                </td>
                <td><span class="pill info">${esc(v.category||'Supplies')}</span></td>
                <td>
                  <div>${esc(v.contact_person||'—')}</div>
                  <div style="font-size:11px;color:var(--muted)">${esc(v.mobile||v.contact||'—')}</div>
                </td>
                <td>${esc(v.city||'')}${v.state?', '+esc(v.state):''}</td>
                <td>
                  <div style="font-size:11px">${v.gstin?'GSTIN: '+esc(v.gstin):'PAN: '+esc(v.pan||'Unregistered')}</div>
                </td>
                <td><span class="pill ${sPill}">${esc(v.status||'Approved')}</span></td>
                <td style="text-align:right">
                  <div style="display:flex;gap:4px;justify-content:flex-end">
                    <button class="btn btn-secondary btn-sm" onclick="openVendorProfileModal(${v.id})" title="View Profile">&#128269;</button>
                    <button class="btn btn-secondary btn-sm" onclick="openUpdateVendorStatusModal(${v.id})" title="Approve / Change Status">&#10003;</button>
                  </div>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    ` : `<div class="empty">No vendors found for status: "${activeVendorStatusFilter}". Click "+ Register New Vendor" above.</div>`;
  }catch(e){
    box.innerHTML = `<div class="empty">Error loading vendors: ${esc(e.message)}</div>`;
  }
}

function openRegisterVendorModal(){
  const html = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:10px">
      <h3 style="margin:0">&#127970; Register New Vendor / Supplier</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form id="form-register-vendor" onsubmit="submitRegisterVendor(event)">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div><label style="font-size:11px;font-weight:600">Company / Vendor Name:</label><input id="v-name" required placeholder="e.g. Leica Geosystems India" style="width:100%"></div>
        <div>
          <label style="font-size:11px;font-weight:600">Vendor Category:</label>
          <select id="v-cat" style="width:100%">
            <option value="Survey Equipment">Survey Equipment (GNSS, Total Station, Drones)</option>
            <option value="Vehicle Rental">Vehicle &amp; Field Transportation</option>
            <option value="Civil Construction Materials">Civil Construction Materials</option>
            <option value="IT &amp; Software">IT &amp; Geospatial Software</option>
            <option value="Printing &amp; CAD Reprographics">Printing &amp; CAD Reprographics</option>
            <option value="Subcontractor">Field Engineering Subcontractor</option>
            <option value="General Supplies">General Office &amp; Site Supplies</option>
          </select>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px">
        <div><label style="font-size:11px;font-weight:600">Contact Person:</label><input id="v-contact-person" required placeholder="Mr. Rajesh Kumar" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">Mobile Phone:</label><input id="v-mobile" required placeholder="+91 98230 44556" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">Email Address:</label><input id="v-email" placeholder="sales@vendor.com" style="width:100%"></div>
      </div>
      <div class="form-group" style="margin-bottom:10px">
        <label style="font-size:11px;font-weight:600">Office / Registered Address:</label>
        <input id="v-address" placeholder="Plot 12, Industrial Area" style="width:100%">
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px">
        <div><label style="font-size:11px;font-weight:600">City:</label><input id="v-city" placeholder="Nagpur" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">State:</label><input id="v-state" placeholder="Maharashtra" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">PIN Code:</label><input id="v-pincode" placeholder="440028" style="width:100%"></div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:10px">
        <div><label style="font-size:11px;font-weight:600">GSTIN Number (Optional):</label><input id="v-gstin" placeholder="27AAACT0000A1Z5" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">PAN Number:</label><input id="v-pan" placeholder="AAACT0000A" style="width:100%"></div>
        <div><label style="font-size:11px;font-weight:600">MSME / Udyam Reg:</label><input id="v-msme" placeholder="UDYAM-MH-0000" style="width:100%"></div>
      </div>
      <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line);margin-bottom:10px">
        <div style="font-size:11px;font-weight:700;margin-bottom:6px">Bank Settlement Account (Restricted Access):</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
          <div><input id="v-bank-name" placeholder="Bank Name" style="width:100%;font-size:11px"></div>
          <div><input id="v-bank-account" placeholder="Account Number" style="width:100%;font-size:11px"></div>
          <div><input id="v-bank-ifsc" placeholder="IFSC Code" style="width:100%;font-size:11px"></div>
        </div>
      </div>
      <div class="form-group" style="margin-bottom:12px">
        <label style="font-size:11px;font-weight:600">Products &amp; Services Supplied:</label>
        <input id="v-services" placeholder="RTK GNSS Base &amp; Rover units, Survey tripods, prism poles" style="width:100%">
      </div>
      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Register Vendor</button>
      </div>
    </form>
  `;
  showModal(html);
}

async function submitRegisterVendor(e){
  e.preventDefault();
  const payload = {
    workspace_id: state.ws,
    company_name: $("#v-name").value.trim(),
    category: $("#v-cat").value,
    contact_person: $("#v-contact-person").value.trim(),
    mobile: $("#v-mobile").value.trim(),
    email: $("#v-email").value.trim(),
    address: $("#v-address").value.trim(),
    city: $("#v-city").value.trim(),
    state: $("#v-state").value.trim(),
    pincode: $("#v-pincode").value.trim(),
    gstin: $("#v-gstin").value.trim(),
    pan: $("#v-pan").value.trim(),
    msme_udyam: $("#v-msme").value.trim(),
    bank_name: $("#v-bank-name").value.trim(),
    bank_account: $("#v-bank-account").value.trim(),
    bank_ifsc: $("#v-bank-ifsc").value.trim(),
    services_supplied: $("#v-services").value.trim(),
    status: "Approved"
  };

  try{
    await api(`/api/vendors?workspace=${state.ws}`, { method: "POST", body: payload });
    toast("Vendor registered successfully!", "ok");
    closeModal();
    await renderRegisteredVendors();
  }catch(err){
    toast("Error registering vendor: " + err.message, "bad");
  }
}

async function openVendorProfileModal(vid){
  try{
    const j = await api(`/api/vendors/${vid}?workspace=${state.ws}`);
    const v = j.vendor;
    if (!v) return toast("Vendor not found", "bad");

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:8px">
        <h3 style="margin:0">&#127970; Vendor Profile: ${esc(v.company_name||v.name)}</h3>
        <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:12px;margin-bottom:14px">
        <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line)">
          <div><strong>Category:</strong> <span class="pill info">${esc(v.category||'Supplies')}</span></div>
          <div><strong>Contact Person:</strong> ${esc(v.contact_person||'—')}</div>
          <div><strong>Mobile:</strong> ${esc(v.mobile||v.contact||'—')}</div>
          <div><strong>Email:</strong> ${esc(v.email||'—')}</div>
          <div><strong>Location:</strong> ${esc(v.address||'')}, ${esc(v.city||'')}, ${esc(v.state||'')}</div>
        </div>
        <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line)">
          <div><strong>GSTIN:</strong> ${esc(v.gstin||'Unregistered')}</div>
          <div><strong>PAN:</strong> ${esc(v.pan||'—')}</div>
          <div><strong>MSME:</strong> ${esc(v.msme_udyam||'—')}</div>
          <div><strong>Status:</strong> <span class="pill ok">${esc(v.status||'Approved')}</span></div>
          <div><strong>Registration Date:</strong> ${esc(v.registration_date||'—')}</div>
        </div>
      </div>
      <div style="background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line);font-size:12px;margin-bottom:14px">
        <strong>Bank Details (Restricted View):</strong>
        <div style="margin-top:4px">Bank: ${esc(v.bank_name||'—')} | A/C: ${esc(v.bank_account?('XXXX' + String(v.bank_account).slice(-4)):'—')} | IFSC: ${esc(v.bank_ifsc||'—')}</div>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button class="btn btn-secondary" onclick="openUpdateVendorStatusModal(${v.id})">Change Status / Verify</button>
        <button class="btn btn-primary" onclick="closeModal()">Close</button>
      </div>
    `);
  }catch(e){ toast("Error loading vendor: " + e.message, "bad"); }
}

async function openUpdateVendorStatusModal(vid){
  const statuses = ["Approved", "Active", "Under Verification", "Registration Pending", "Inactive", "Rejected"];
  showModal(`
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:8px">
      <h3 style="margin:0">&#128221; Update Vendor Approval Status</h3>
      <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
    </div>
    <form onsubmit="submitVendorStatus(event, ${vid})">
      <div class="form-group" style="margin-bottom:12px">
        <label style="font-size:11px;font-weight:600">Select Vendor Status:</label>
        <select id="update-vendor-status-select" style="width:100%;font-size:13px;padding:6px">
          ${statuses.map(st => `<option value="${st}">${st}</option>`).join('')}
        </select>
      </div>
      <div class="form-group" style="margin-bottom:12px">
        <label style="font-size:11px;font-weight:600">Verification Remarks / Notes:</label>
        <input id="update-vendor-remarks" placeholder="KYC, GSTIN and bank details verified" style="width:100%" required>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:8px">
        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
        <button type="submit" class="btn btn-primary">&#10003; Commit Vendor Status</button>
      </div>
    </form>
  `);
}

async function submitVendorStatus(e, vid){
  e.preventDefault();
  const st = $("#update-vendor-status-select").value;
  const rem = $("#update-vendor-remarks").value.trim();

  try{
    await api(`/api/vendors/${vid}/status?workspace=${state.ws}`, {
      method: "POST",
      body: { status: st, remarks: rem }
    });
    toast(`Vendor status updated to "${st}"`, "ok");
    closeModal();
    await renderRegisteredVendors();
  }catch(err){
    toast("Error updating vendor status: " + err.message, "bad");
  }
}


// ------------------------------------------------------------------------------
// 5. EMPLOYEE STATUS & EXIT CLEARANCE MANAGEMENT
// ------------------------------------------------------------------------------

let activeEmployeeFilter = 'active';

async function renderStaffDirectory(filterMode = null){
  if (filterMode !== null) activeEmployeeFilter = filterMode;
  const box = $("#employee-list");
  if (!box) return;

  try{
    const j = await api(`/api/employees?filter=${activeEmployeeFilter}&workspace=${state.ws}`);
    const emps = j.employees || [];

    box.innerHTML = emps.length ? `
      <table>
        <thead>
          <tr>
            <th>Emp ID</th>
            <th>Full Name</th>
            <th>Role / Designation</th>
            <th>Department</th>
            <th>Base Salary</th>
            <th>Contact</th>
            <th>Employment Status</th>
            <th style="text-align:right">Actions</th>
          </tr>
        </thead>
        <tbody>
          ${emps.map(e => {
            const st = e.employment_status || 'Active';
            let sPill = 'ok';
            if (st === 'On Leave') sPill = 'info';
            else if (st === 'Notice Period') sPill = 'warn';
            else if (['Resigned', 'Terminated', 'Exited', 'Inactive'].includes(st)) sPill = 'bad';

            return `
              <tr>
                <td><strong>${esc(e.employee_id||e.id)}</strong></td>
                <td><strong>${esc(e.name)}</strong></td>
                <td>${esc(e.designation||e.role)}</td>
                <td>${esc(e.department||'Operations')}</td>
                <td>₹ ${Number(e.salary||0).toLocaleString('en-IN', {minimumFractionDigits:2})}</td>
                <td class="muted">${esc(e.phone||e.email||'—')}</td>
                <td><span class="pill ${sPill}">${esc(st)}</span></td>
                <td style="text-align:right">
                  <button class="btn btn-secondary btn-sm" onclick="openEmployeeStatusModal(${e.id})">Update Status / Exit</button>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    ` : `<div class="empty">No personnel found for filter: "${activeEmployeeFilter}".</div>`;
  }catch(e){
    box.innerHTML = `<div class="empty">Error loading staff directory: ${esc(e.message)}</div>`;
  }
}

function filterEmployeeRoster(mode, btn){
  if (btn && btn.parentElement) {
    btn.parentElement.querySelectorAll("button").forEach(b => b.classList.remove("active", "btn-primary"));
    btn.classList.add("active", "btn-primary");
  }
  renderStaffDirectory(mode);
}

async function openEmployeeStatusModal(empId){
  try{
    const j = await api(`/api/employees/${empId}?workspace=${state.ws}`);
    const e = j.employee;
    if (!e) return toast("Employee not found", "bad");
    const currentStatus = e.employment_status || 'Active';
    const history = e.status_history || [];

    const statuses = ["Active", "On Leave", "Notice Period", "Resigned", "Terminated", "Exited", "Inactive"];

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:8px">
        <h3 style="margin:0">&#128100; Employment Status &amp; Exit Clearance: ${esc(e.name)}</h3>
        <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
      </div>
      <form onsubmit="submitEmployeeStatus(event, ${empId})">
        <div class="form-group" style="margin-bottom:12px">
          <label style="font-size:11px;font-weight:600">Select Employment Status:</label>
          <select id="emp-status-select" style="width:100%;font-size:13px;padding:6px" onchange="toggleExitClearanceFields(this.value)">
            ${statuses.map(st => `<option value="${st}" ${st===currentStatus?'selected':''}>${st}</option>`).join('')}
          </select>
        </div>

        <!-- Exit Clearance Section (Visible on Notice/Resigned/Terminated/Exited/Inactive) -->
        <div id="emp-exit-clearance-box" style="display:${['Notice Period', 'Resigned', 'Terminated', 'Exited', 'Inactive'].includes(currentStatus)?'block':'none'};background:var(--panel-2);padding:10px;border-radius:4px;border:1px solid var(--line);margin-bottom:12px">
          <div style="font-size:11px;font-weight:700;margin-bottom:8px;color:var(--warn)">Exit Clearance &amp; Handover Protocol:</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px">
            <div><label style="font-size:10px;font-weight:600">Last Working Date:</label><input id="emp-lwd" type="date" value="${e.last_working_date||''}" style="width:100%;font-size:11px"></div>
            <div><label style="font-size:10px;font-weight:600">Official Exit Date:</label><input id="emp-exit-date" type="date" value="${e.exit_date||''}" style="width:100%;font-size:11px"></div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:8px">
            <div>
              <label style="font-size:10px;font-weight:600">Reason for Leaving:</label>
              <select id="emp-reason" style="width:100%;font-size:11px">
                <option value="Career Growth / Better Opportunity">Career Growth / Better Opportunity</option>
                <option value="Relocation / Family">Relocation / Family</option>
                <option value="Health Reasons">Health Reasons</option>
                <option value="Contract Completion">Contract Completion</option>
                <option value="Mutual Separation">Mutual Separation</option>
                <option value="Involuntary Termination">Involuntary Termination</option>
              </select>
            </div>
            <div>
              <label style="font-size:10px;font-weight:600">Exit Type:</label>
              <select id="emp-exit-type" style="width:100%;font-size:11px">
                <option value="Voluntary Resignation">Voluntary Resignation</option>
                <option value="Mutual Separation">Mutual Separation</option>
                <option value="End of Term Contract">End of Term Contract</option>
                <option value="Termination">Termination</option>
              </select>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
            <div>
              <label style="font-size:10px;font-weight:600">Equipment &amp; Data Handover:</label>
              <select id="emp-handover" style="width:100%;font-size:11px">
                <option value="Completed" ${e.handover_status==='Completed'?'selected':''}>Completed &amp; Signed Off</option>
                <option value="Pending" ${e.handover_status!=='Completed'?'selected':''}>Pending Equipment Return</option>
              </select>
            </div>
            <div>
              <label style="font-size:10px;font-weight:600">Final Settlement (Full &amp; Final):</label>
              <select id="emp-settlement" style="width:100%;font-size:11px">
                <option value="Settled" ${e.final_settlement_status==='Settled'?'selected':''}>Settled &amp; Paid</option>
                <option value="Pending" ${e.final_settlement_status!=='Settled'?'selected':''}>Pending Clearance</option>
              </select>
            </div>
          </div>
        </div>

        <div class="form-group" style="margin-bottom:12px">
          <label style="font-size:11px;font-weight:600">Remarks / Transition Notes:</label>
          <input id="emp-status-remarks" placeholder="Status change documentation note" style="width:100%" required>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:8px">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary">&#10003; Commit Status Change</button>
        </div>
      </form>
    `);
  }catch(e){ toast("Error loading employee: " + e.message, "bad"); }
}

function toggleExitClearanceFields(status){
  const box = $("#emp-exit-clearance-box");
  if (!box) return;
  const isExit = ['Notice Period', 'Resigned', 'Terminated', 'Exited', 'Inactive'].includes(status);
  box.style.display = isExit ? 'block' : 'none';
}

async function submitEmployeeStatus(e, empId){
  e.preventDefault();
  const st = $("#emp-status-select").value;
  const isExit = ['Notice Period', 'Resigned', 'Terminated', 'Exited', 'Inactive'].includes(st);

  const payload = {
    employment_status: st,
    remarks: $("#emp-status-remarks").value.trim(),
    exit_date: isExit ? $("#emp-exit-date").value : undefined,
    last_working_date: isExit ? $("#emp-lwd").value : undefined,
    reason_for_leaving: isExit ? $("#emp-reason").value : undefined,
    exit_type: isExit ? $("#emp-exit-type").value : undefined,
    handover_status: isExit ? $("#emp-handover").value : undefined,
    final_settlement_status: isExit ? $("#emp-settlement").value : undefined
  };

  try{
    await api(`/api/employees/${empId}/status?workspace=${state.ws}`, {
      method: "POST",
      body: payload
    });
    toast(`Employee status updated to "${st}"`, "ok");
    closeModal();
    await renderStaffDirectory();
  }catch(err){
    toast("Error updating status: " + err.message, "bad");
  }
}


// ------------------------------------------------------------------------------
// 6. AUTOMATED REPORT ARCHIVE & VISUAL ANALYTICS
// ------------------------------------------------------------------------------

async function renderReportsArchive(){
  const summaryBox = $("#reports-analytics-summary");
  const chartsBox = $("#reports-charts-container");
  const tableBox = $("#reports-archive-table");

  try{
    const [dashRes, archRes] = await Promise.all([
      api(`/api/reports/dashboard?workspace=${state.ws}`),
      api(`/api/reports?workspace=${state.ws}`)
    ]);

    const stats = dashRes.analytics || {};
    const reports = archRes.reports || [];

    if ($("#reports-count-pill")) $("#reports-count-pill").textContent = `${reports.length} Reports`;

    // 1. Metric cards
    if (summaryBox) {
      summaryBox.innerHTML = `
        <div class="c ok"><div class="l">Total Revenue Billed</div><div class="v">₹ ${Number(stats.total_revenue||0).toLocaleString('en-IN')}</div></div>
        <div class="c warn"><div class="l">Outstanding Receivables</div><div class="v">₹ ${Number(stats.outstanding_receivables||0).toLocaleString('en-IN')}</div></div>
        <div class="c accent"><div class="l">Survey Sites Portfolio</div><div class="v">${stats.total_sites||0} (${stats.completed_sites||0} completed)</div></div>
        <div class="c info"><div class="l">Archived Reports</div><div class="v">${dashRes.total_reports||reports.length}</div></div>
      `;
    }

    // 2. Visual Analytics Charts
    if (chartsBox) {
      const gstRev = stats.gst_revenue || 0;
      const nongstRev = stats.nongst_revenue || 0;
      const uncol = stats.outstanding_receivables || 0;
      const totalRev = gstRev + nongstRev;

      chartsBox.innerHTML = `
        <div class="card" style="margin:0;padding:12px">
          <h4 style="margin:0 0 8px">&#128200; Revenue Distribution (GST vs Non-GST)</h4>
          <div style="font-size:11px;margin-bottom:8px;color:var(--muted)">Proportion of GST Tax Invoices vs Non-GST Commercial Bills</div>
          <div style="display:flex;height:24px;border-radius:4px;overflow:hidden;margin-bottom:8px">
            <div style="background:#0284c7;width:${totalRev?(gstRev/totalRev*100):50}%;color:#fff;font-size:10px;display:flex;align-items:center;justify-content:center" title="GST Invoices: ₹ ${gstRev}">GST ${totalRev?(gstRev/totalRev*100).toFixed(0):0}%</div>
            <div style="background:#10b981;width:${totalRev?(nongstRev/totalRev*100):50}%;color:#fff;font-size:10px;display:flex;align-items:center;justify-content:center" title="Non-GST Bills: ₹ ${nongstRev}">Non-GST ${totalRev?(nongstRev/totalRev*100).toFixed(0):0}%</div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:11px">
            <span><span style="color:#0284c7">■</span> GST Invoices: <strong>₹ ${gstRev.toLocaleString('en-IN')}</strong></span>
            <span><span style="color:#10b981">■</span> Non-GST Bills: <strong>₹ ${nongstRev.toLocaleString('en-IN')}</strong></span>
          </div>
        </div>

        <div class="card" style="margin:0;padding:12px">
          <h4 style="margin:0 0 8px">&#128202; Operational Realization &amp; Collections</h4>
          <div style="font-size:11px;margin-bottom:8px;color:var(--muted)">Cash Realized vs Outstanding Client Balance</div>
          <div style="display:flex;height:24px;border-radius:4px;overflow:hidden;margin-bottom:8px">
            <div style="background:#16a34a;width:${(totalRev+uncol)?(totalRev/(totalRev+uncol)*100):100}%;color:#fff;font-size:10px;display:flex;align-items:center;justify-content:center" title="Realized: ₹ ${totalRev}">Billed ${(totalRev+uncol)?(totalRev/(totalRev+uncol)*100).toFixed(0):100}%</div>
            <div style="background:#f59e0b;width:${(totalRev+uncol)?(uncol/(totalRev+uncol)*100):0}%;color:#fff;font-size:10px;display:flex;align-items:center;justify-content:center" title="Pending: ₹ ${uncol}">Pending ${(totalRev+uncol)?(uncol/(totalRev+uncol)*100).toFixed(0):0}%</div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:11px">
            <span><span style="color:#16a34a">■</span> Total Billed: <strong>₹ ${totalRev.toLocaleString('en-IN')}</strong></span>
            <span><span style="color:#f59e0b">■</span> Uncollected: <strong>₹ ${uncol.toLocaleString('en-IN')}</strong></span>
          </div>
        </div>
      `;
    }

    // 3. Table of archived reports
    if (tableBox) {
      tableBox.innerHTML = reports.length ? `
        <table>
          <thead>
            <tr>
              <th>Report Title</th>
              <th>Period Label</th>
              <th>Date Range</th>
              <th>Generated At</th>
              <th>Status</th>
              <th style="text-align:right">Actions</th>
            </tr>
          </thead>
          <tbody>
            ${reports.map(r => `
              <tr>
                <td><strong>${esc(r.title)}</strong></td>
                <td><span class="pill info">${esc(r.period_label||'Monthly')}</span></td>
                <td>${esc(r.date_range||'Last 30 Days')}</td>
                <td class="muted">${esc(r.generated_at)}</td>
                <td><span class="pill ok">${esc(r.status||'Completed')}</span></td>
                <td style="text-align:right">
                  <div style="display:flex;gap:4px;justify-content:flex-end">
                    <button class="btn btn-primary btn-sm" onclick="openReportViewerModal(${r.id})">&#128269; View Report</button>
                    <a href="/api/reports/${r.id}/export?format=csv&workspace=${state.ws}" class="btn btn-secondary btn-sm" target="_blank">&#128229; CSV</a>
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      ` : `<div class="empty">No archived reports yet. Click "⚡ Generate New Report" above.</div>`;
    }

  }catch(e){
    if (tableBox) tableBox.innerHTML = `<div class="empty">Error loading report archive: ${esc(e.message)}</div>`;
  }
}

async function triggerReportGeneration(){
  const repType = $("#report-type-select") ? $("#report-type-select").value : "MONTHLY_PERFORMANCE";
  const period = $("#report-period-select") ? $("#report-period-select").value : "Last 30 Days";

  try{
    toast("Compiling live database metrics and generating report...", "info");
    const j = await api(`/api/reports/generate?workspace=${state.ws}`, {
      method: "POST",
      body: { report_type: repType, date_range: period }
    });
    toast("Business report compiled and archived successfully!", "ok");
    await renderReportsArchive();
    if (j.report && j.report.id) openReportViewerModal(j.report.id);
  }catch(e){
    toast("Report generation failed: " + e.message, "bad");
  }
}

async function openReportViewerModal(reportId){
  try{
    const j = await api(`/api/reports/${reportId}?workspace=${state.ws}`);
    const r = j.report;
    if (!r) return toast("Report not found", "bad");
    const tables = r.detailed_tables_json || [];
    const pendingActions = r.pending_actions_json || [];

    showModal(`
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;border-bottom:1px solid var(--line);padding-bottom:10px">
        <div>
          <h3 style="margin:0">&#128202; ${esc(r.title)}</h3>
          <div style="font-size:11px;color:var(--muted)">Period: ${esc(r.period_label)} | Generated: ${esc(r.generated_at)} | Workspace: ${esc(r.workspace_id)}</div>
        </div>
        <div style="display:flex;gap:6px">
          <a href="/api/reports/${r.id}/export?format=csv&workspace=${state.ws}" class="btn btn-secondary btn-sm" target="_blank">&#128229; Export CSV</a>
          <button class="btn btn-secondary btn-sm" onclick="window.print()">&#128424; Print</button>
          <button class="btn btn-secondary btn-sm" onclick="closeModal()">✕</button>
        </div>
      </div>

      <div style="max-height:500px;overflow-y:auto;padding-right:4px">
        <!-- Executive Summary -->
        <div style="background:var(--panel-2);padding:12px;border-radius:4px;border:1px solid var(--line);margin-bottom:14px">
          <h4 style="margin:0 0 6px">&#128221; Executive Narrative Summary:</h4>
          <div style="font-size:12px;line-height:1.5;color:var(--text)">${esc(r.executive_summary||r.summary)}</div>
        </div>

        <!-- Detailed Tables -->
        ${tables.map(tbl => `
          <div style="margin-bottom:16px">
            <h4 style="margin:0 0 8px">&#128196; ${esc(tbl.section_name)}</h4>
            <table style="width:100%;font-size:12px">
              <thead>
                <tr>
                  ${(tbl.headers||[]).map(h => `<th>${esc(h)}</th>`).join('')}
                </tr>
              </thead>
              <tbody>
                ${(tbl.rows||[]).map(row => `
                  <tr>
                    ${row.map((cell, cIdx) => `<td style="${cIdx===0?'font-weight:600':''}">${esc(cell)}</td>`).join('')}
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `).join('')}

        <!-- Pending Operational Actions -->
        <div style="background:rgba(245, 158, 11, 0.08);border:1px solid var(--warn);padding:12px;border-radius:4px;margin-bottom:14px">
          <h4 style="margin:0 0 6px;color:var(--warn)">&#9888; Actionable Operational Recommendations:</h4>
          <ul style="margin:0;padding-left:18px;font-size:12px">
            ${pendingActions.map(act => `<li>${esc(act)}</li>`).join('')}
          </ul>
        </div>
      </div>

      <div style="display:flex;justify-content:flex-end;margin-top:14px">
        <button class="btn btn-secondary" onclick="closeModal()">Close Viewer</button>
      </div>
    `);
  }catch(e){ toast("Error loading report viewer: " + e.message, "bad"); }
}

// Wire up subnav and listeners when document is ready
window.addEventListener("DOMContentLoaded", () => {
  if (window.setupFinanceSubnav) {
    const origSetup = window.setupFinanceSubnav;
    window.setupFinanceSubnav = function(){
      origSetup();
      const nav = $("#subnav-finance");
      if (nav) {
        nav.querySelectorAll("button[data-sub]").forEach(b => {
          b.addEventListener("click", () => {
            if (b.dataset.sub === "vendors") renderRegisteredVendors();
            if (b.dataset.sub === "reports") renderReportsArchive();
          });
        });
      }
    };
  }
});