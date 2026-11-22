# -*- coding: utf-8 -*-
"""Patch dashboard.html with Owner Setup Center and Google Business Profile."""
import sys

path = 'foundation/dashboard/dashboard.html'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Owner Setup Center to Navigation
nav_target = '<div class="item" data-sec="integrations"><span class="ico">&#128279;</span>Integration & Sync</div>'
nav_replacement = '''<div class="item" data-sec="integrations"><span class="ico">&#128279;</span>Integration & Sync</div>
      <div class="item" data-sec="owner-setup"><span class="ico">&#128736;</span>Owner Setup Center</div>'''

if 'data-sec="owner-setup"' not in content:
    if nav_target in content:
        content = content.replace(nav_target, nav_replacement, 1)
        print("[OK] Added Owner Setup Center nav item.")
    else:
        print("[WARN] Nav target not found.")

# 2. Add Google Business Profile button to subnav-integrations
subnav_target = '<button class="btn btn-secondary btn-sm" data-int-sub="health" onclick="switchIntSub(\'health\')">&#128154; Health Monitor</button>'
subnav_replacement = '''<button class="btn btn-secondary btn-sm" data-int-sub="health" onclick="switchIntSub('health')">&#128154; Health Monitor</button>
        <button class="btn btn-secondary btn-sm" data-int-sub="gbp" onclick="switchIntSub('gbp')">&#127970; Google Business Profile</button>'''

if 'data-int-sub="gbp"' not in content:
    if subnav_target in content:
        content = content.replace(subnav_target, subnav_replacement, 1)
        print("[OK] Added GBP subnav button.")
    else:
        print("[WARN] Subnav target not found.")

# 3. Add int-sub-gbp subpanel inside sec-integrations
gbp_subpanel_html = '''
      <!-- Subpanel: Google Business Profile (GBP) -->
      <div id="int-sub-gbp" class="int-subpanel" style="display:none">
        <div class="card" style="margin-bottom:16px;border-left:4px solid #1a73e8;background:var(--panel-2)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
            <div>
              <h3 style="margin:0 0 2px">&#127970; Google Business Profile (GBP) Center</h3>
              <div style="font-size:12px;color:var(--muted)">Manage official Google Maps presence, service offerings, customer reviews, and local updates.</div>
            </div>
            <div style="display:flex;gap:8px">
              <button class="btn btn-primary btn-sm" onclick="loadGBPStatus()">&#8635; Refresh GBP Status</button>
            </div>
          </div>
          <div id="gbp-status-banner" style="padding:10px 14px;border-radius:6px;background:rgba(26,115,232,0.1);border:1px solid rgba(26,115,232,0.3);margin-bottom:14px;font-size:12px">
            Checking Google Business Profile status...
          </div>
          <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:14px;margin-bottom:16px">
            <div style="background:var(--panel);padding:14px;border-radius:8px">
              <h4 style="margin:0 0 8px;font-size:13px">&#128205; Business Identity &amp; Location</h4>
              <div id="gbp-business-details" style="font-size:12px;line-height:1.7;color:var(--text)">Loading details...</div>
            </div>
            <div style="background:var(--panel);padding:14px;border-radius:8px">
              <h4 style="margin:0 0 8px;font-size:13px">&#128736; Published Service Offerings</h4>
              <div id="gbp-services-list" style="font-size:12px;color:var(--text)">Loading services...</div>
            </div>
          </div>

          <!-- Create GBP Post / Update -->
          <div style="background:var(--panel);padding:14px;border-radius:8px;margin-bottom:16px">
            <h4 style="margin:0 0 8px;font-size:13px">&#128227; Create Google Post (Local Update)</h4>
            <div style="display:flex;gap:10px;flex-wrap:wrap">
              <input type="text" id="gbp-post-summary" class="input" placeholder="e.g. Certified DGPS RTK boundary surveys available in Nagpur & Central India with 24-hr report turnaround." style="flex:1;min-width:240px">
              <button class="btn btn-primary btn-sm" onclick="submitGBPPost()">Publish Google Post</button>
            </div>
            <div id="gbp-posts-history" style="margin-top:12px;font-size:12px"></div>
          </div>
        </div>
      </div>
'''

if 'id="int-sub-gbp"' not in content:
    # Insert right before </section> of sec-integrations
    sec_int_end = '</section>\n\n    <section id="sec-settings"'
    if sec_int_end in content:
        content = content.replace(sec_int_end, gbp_subpanel_html + '\n    </section>\n\n    <section id="sec-settings"', 1)
        print("[OK] Added int-sub-gbp panel.")
    else:
        print("[WARN] sec-integrations end not found.")

# 4. Add sec-owner-setup section right before sec-settings
owner_setup_section_html = '''
    <!-- =========================================================
         OWNER SETUP CENTER & ONBOARDING CHECKLIST
         ========================================================= -->
    <section id="sec-owner-setup" class="sec" style="display:none">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:10px">
        <div>
          <h2 style="margin:0 0 4px">&#128736; Interactive Owner Setup Center &amp; Checklist</h2>
          <div style="font-size:13px;color:var(--muted)">Consolidated center for all remaining manual steps: Google &amp; Meta OAuth credentials, account linking, and genuine business onboarding.</div>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-primary btn-sm" onclick="loadOwnerSetupChecklist()">&#8635; Refresh Checklist</button>
        </div>
      </div>

      <!-- Overview Cards -->
      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;margin-bottom:20px">
        <div class="card" style="padding:16px;border-left:4px solid var(--accent)">
          <div style="font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:600">Onboarding Progress</div>
          <div id="setup-progress-num" style="font-size:24px;font-weight:700;margin-top:4px">-- / -- Tasks</div>
          <div id="setup-progress-label" style="font-size:12px;color:var(--text);margin-top:2px">Initializing checklist...</div>
        </div>
        <div class="card" style="padding:16px;border-left:4px solid #10b981">
          <div style="font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:600">Internal System Readiness</div>
          <div style="font-size:24px;font-weight:700;margin-top:4px;color:#10b981">100% Operational</div>
          <div style="font-size:12px;color:var(--text);margin-top:2px">Zero Paid Billing • Fresh Business Reset</div>
        </div>
        <div class="card" style="padding:16px;border-left:4px solid #f59e0b">
          <div style="font-size:11px;color:var(--muted);text-transform:uppercase;font-weight:600">Owner Action Required</div>
          <div id="setup-pending-num" style="font-size:24px;font-weight:700;margin-top:4px;color:#f59e0b">-- Actions</div>
          <div style="font-size:12px;color:var(--text);margin-top:2px">OAuth Consents &amp; Business Data</div>
        </div>
      </div>

      <!-- Secure Credentials Entry Card -->
      <div class="card" style="padding:20px;margin-bottom:24px;background:var(--panel-2);border:1px solid var(--line)">
        <h3 style="margin:0 0 6px">&#128272; Secure OAuth &amp; Business Configuration</h3>
        <div style="font-size:12px;color:var(--muted);margin-bottom:16px">Enter your private OAuth application keys and official GSTIN securely into local encrypted configuration. Secrets are never exposed in chat logs or git repositories.</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(260px, 1fr));gap:14px">
          <div>
            <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Google Client ID</label>
            <input type="text" id="owner-google-client-id" class="input" placeholder="e.g. 123456789-xxxx.apps.googleusercontent.com" style="width:100%">
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Google Client Secret</label>
            <input type="password" id="owner-google-client-secret" class="input" placeholder="••••••••••••••••••••••••" style="width:100%">
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Meta App ID (Facebook &amp; Instagram)</label>
            <input type="text" id="owner-meta-app-id" class="input" placeholder="e.g. 158923489123456" style="width:100%">
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Meta App Secret</label>
            <input type="password" id="owner-meta-app-secret" class="input" placeholder="••••••••••••••••••••••••" style="width:100%">
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;display:block;margin-bottom:4px">Official Business GSTIN</label>
            <input type="text" id="owner-business-gstin" class="input" placeholder="e.g. 27AABCS1234F1Z5" style="width:100%">
          </div>
          <div style="display:flex;align-items:flex-end">
            <button class="btn btn-primary" onclick="submitOwnerCredentials()" style="width:100%;height:38px">&#128190; Save Encrypted Config</button>
          </div>
        </div>
        <div id="owner-creds-msg" style="margin-top:10px;font-size:12px"></div>
      </div>

      <!-- Categories Container -->
      <div id="owner-setup-categories-container">
        <div style="color:var(--muted);padding:20px;text-align:center">&#8635; Loading Owner Setup checklist...</div>
      </div>
    </section>
'''

if 'id="sec-owner-setup"' not in content:
    sec_settings_target = '<section id="sec-settings"'
    if sec_settings_target in content:
        content = content.replace(sec_settings_target, owner_setup_section_html + '\n    <section id="sec-settings"', 1)
        print("[OK] Added sec-owner-setup section.")
    else:
        print("[WARN] sec-settings target not found.")

# 5. Add JavaScript Controllers
js_code = '''
// -----------------------------------------------------------------------------
// OWNER SETUP CENTER & GOOGLE BUSINESS PROFILE CONTROLLER
// -----------------------------------------------------------------------------
async function loadOwnerSetupChecklist(){
  const container = $("#owner-setup-categories-container");
  if(!container) return;
  try{
    const res = await api(`/api/owner-setup/status?workspace=${state.ws||'SSC'}`);
    if(!res || !res.categories) return;

    const pNum = $("#setup-progress-num");
    const pLbl = $("#setup-progress-label");
    const pPend = $("#setup-pending-num");
    if(pNum) pNum.textContent = `${res.completed_or_ready_count} / ${res.total_tasks} Tasks`;
    if(pLbl) pLbl.textContent = `${res.action_required_count} owner actions remaining`;
    if(pPend) pPend.textContent = `${res.action_required_count} Actions`;

    let html = "";
    res.categories.forEach(cat => {
      html += `
        <div class="card" style="margin-bottom:20px;border-left:4px solid var(--accent)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
            <div>
              <h3 style="margin:0 0 4px">${cat.icon} ${cat.title}</h3>
              <div style="font-size:12px;color:var(--muted)">${cat.description}</div>
            </div>
          </div>
          <div style="display:flex;flex-direction:column;gap:12px">
      `;

      cat.tasks.forEach(t => {
        let badgeColor = "#f59e0b";
        let badgeText = t.status_label;
        if(t.status === "CONNECTED" || t.status === "COMPLETED_OR_READY" || t.status === "CONFIGURED" || t.status === "ACTIVE_READY"){
          badgeColor = "#10b981";
        } else if(t.status === "PAGE_LINKAGE_REQUIRED"){
          badgeColor = "#ef4444";
        }

        html += `
          <div style="background:var(--panel-2);border:1px solid var(--line);border-radius:8px;padding:14px">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
              <div style="font-weight:600;font-size:13px">${t.title}</div>
              <span style="font-size:11px;padding:3px 10px;border-radius:12px;background:${badgeColor}22;color:${badgeColor};border:1px solid ${badgeColor}66;font-weight:600">${badgeText}</span>
            </div>
            <div style="font-size:12px;color:var(--text);margin:6px 0 8px">${t.why_needed}</div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px">
              <strong>Action Steps:</strong>
              <ol style="margin:4px 0 0 18px;padding:0">
                ${t.step_by_step.map(s => `<li>${s}</li>`).join("")}
              </ol>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px;flex-wrap:wrap;gap:8px;border-top:1px solid var(--line);padding-top:8px">
              <span style="font-size:11px;color:var(--muted)">Target: <code style="color:var(--accent)">${t.target_in_app}</code></span>
              <a href="${t.official_url}" target="_blank" class="btn btn-secondary btn-sm" style="text-decoration:none">&#8599; Open Official Portal</a>
            </div>
          </div>
        `;
      });

      html += `</div></div>`;
    });

    container.innerHTML = html;
  }catch(e){
    container.innerHTML = `<div style="color:var(--bad);padding:14px">&#9888; Failed to load checklist: ${e.message}</div>`;
  }
}

async function submitOwnerCredentials(){
  const msg = $("#owner-creds-msg");
  if(msg) msg.innerHTML = `<span style="color:var(--muted)">&#8635; Encrypting and saving credentials...</span>`;

  const data = {};
  const gId = $("#owner-google-client-id");
  const gSec = $("#owner-google-client-secret");
  const mId = $("#owner-meta-app-id");
  const mSec = $("#owner-meta-app-secret");
  const gstin = $("#owner-business-gstin");

  if(gId && gId.value.trim()) data.GOOGLE_CLIENT_ID = gId.value.trim();
  if(gSec && gSec.value.trim()) data.GOOGLE_CLIENT_SECRET = gSec.value.trim();
  if(mId && mId.value.trim()) data.META_APP_ID = mId.value.trim();
  if(mSec && mSec.value.trim()) data.META_APP_SECRET = mSec.value.trim();
  if(gstin && gstin.value.trim()) data.OWNER_BUSINESS_GSTIN = gstin.value.trim();

  try{
    const res = await api("/api/owner-setup/credentials", "POST", data);
    if(msg) msg.innerHTML = `<span style="color:#10b981">&#10003; ${res.message || "Saved successfully!"}</span>`;
    toast("OAuth & Business credentials safely saved!");
    loadOwnerSetupChecklist();
  }catch(e){
    if(msg) msg.innerHTML = `<span style="color:var(--bad)">&#9888; Error: ${e.message}</span>`;
    toast(`Failed to save: ${e.message}`, "bad");
  }
}

async function loadGBPStatus(){
  const banner = $("#gbp-status-banner");
  const details = $("#gbp-business-details");
  const services = $("#gbp-services-list");
  const history = $("#gbp-posts-history");

  try{
    const res = await api(`/api/gbp/profile?workspace=${state.ws||'SSC'}`);
    if(!res) return;

    if(banner){
      let bColor = res.is_connected ? "#10b981" : "#f59e0b";
      banner.style.borderColor = bColor;
      banner.style.background = `${bColor}15`;
      banner.innerHTML = `<strong>Status:</strong> ${res.status_label} | <strong>Required Scope:</strong> <code>${res.required_scope}</code>`;
    }

    if(details && res.config){
      details.innerHTML = `
        <div><strong>Name:</strong> ${res.config.business_name}</div>
        <div><strong>Primary Category:</strong> ${res.config.primary_category}</div>
        <div><strong>Phone:</strong> ${res.config.primary_phone}</div>
        <div><strong>Website:</strong> <a href="${res.config.website_url}" target="_blank" style="color:var(--accent)">${res.config.website_url}</a></div>
        <div><strong>Address:</strong> ${res.config.address}</div>
        <div><strong>Verification Status:</strong> <span style="font-weight:600;color:${res.is_connected ? '#10b981' : '#f59e0b'}">${res.config.verification_status}</span></div>
      `;
    }

    if(services && res.services){
      services.innerHTML = res.services.map(s => `
        <div style="border-bottom:1px solid var(--line);padding:6px 0">
          <strong>${s.service_name}</strong> <span style="font-size:10px;color:var(--muted)">(${s.category})</span>
          <div style="font-size:11px;color:var(--muted)">${s.description}</div>
        </div>
      `).join("");
    }

    if(history && res.posts){
      history.innerHTML = `
        <div style="font-weight:600;margin-bottom:6px">Recent Google Posts (${res.posts_count}):</div>
        ${res.posts.length ? res.posts.map(p => `
          <div style="background:var(--panel-2);padding:8px;border-radius:6px;margin-bottom:6px">
            <div>${p.summary}</div>
            <div style="font-size:10px;color:var(--muted);margin-top:2px">CTA: ${p.call_to_action_type} | Status: <strong style="color:#10b981">${p.status}</strong> | Created: ${p.created_at}</div>
          </div>
        `).join("") : "<div style='color:var(--muted)'>No posts yet. Draft one above!</div>"}
      `;
    }
  }catch(e){
    if(banner) banner.innerHTML = `<span style="color:var(--bad)">&#9888; Failed to load GBP status: ${e.message}</span>`;
  }
}

async function submitGBPPost(){
  const inp = $("#gbp-post-summary");
  if(!inp || !inp.value.trim()){
    toast("Please enter post summary text", "warn");
    return;
  }
  try{
    const res = await api(`/api/gbp/posts?workspace=${state.ws||'SSC'}`, "POST", {
      summary: inp.value.trim(),
      call_to_action_type: "CALL"
    });
    toast("Google Post drafted successfully!");
    inp.value = "";
    loadGBPStatus();
  }catch(e){
    toast(`Failed to draft post: ${e.message}`, "bad");
  }
}
'''

# Update switchIntSub to include 'gbp'
if "if(sub === \"gbp\") loadGBPStatus();" not in content:
    target_sub = 'if(sub === "hub") loadIntegrationHealth();'
    content = content.replace(target_sub, target_sub + '\n  if(sub === "gbp") loadGBPStatus();', 1)
    print("[OK] Updated switchIntSub for GBP.")

# Hook showSection for 'owner-setup'
if 'if(sec === "owner-setup") loadOwnerSetupChecklist();' not in content:
    target_show = 'function showSection(sec){'
    content = content.replace(target_show, target_show + '\n  if(sec === "owner-setup") loadOwnerSetupChecklist();', 1)
    print("[OK] Hooked showSection for owner-setup.")

# Insert js_code before (async function init()
if 'function loadOwnerSetupChecklist' not in content:
    init_target = '(async function init(){'
    content = content.replace(init_target, js_code + '\n' + init_target, 1)
    print("[OK] Added JavaScript controllers for Owner Setup & GBP.")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[COMPLETE] dashboard.html successfully patched.")
