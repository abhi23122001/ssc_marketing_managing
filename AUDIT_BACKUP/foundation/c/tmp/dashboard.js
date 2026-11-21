
const state = { token: localStorage.getItem("sgai_token")||"", ws:"SSC", role:null, perms:new Set(), user:null };

const $ = id => document.getElementById(id);
const esc = s => String(s??"").replace(/[&<>"]/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;" }[c]));

async function api(path, opts={}){
  const r = await fetch(path, { headers:{"Authorization":"Bearer "+state.token,...((opts.headers)||{})}, ...opts });
  const j = await r.json().catch(()=>({}));
  if(!r.ok){
    throw new Error(j.error || "request failed ("+r.status+")");
  }
  return j;
}

async function auth(){
  try{
    const j = await api("/api/auth/me");
    state.role = j.user.role;
    state.workspace = j.user.workspace_id || "SSC";
    const per = await api("/api/permissions");
    state.perms = new Set(per.perms);
    $("#role-badge").textContent = state.role;
    $("#user-meta").textContent = j.user.username + " (" + j.user.role + ")";
    const authArea = $("#auth-area");
    authArea.innerHTML = `<div class="sub" id="user-label">Logged in as <strong>${esc(j.user.username)}</strong> (<strong>${esc(j.user.role)}</strong>)</div><button id="logout-btn" class="muted" style="padding:6px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel)">Logout</button>`;
    $("#logout-btn").onclick = () => location.reload();
  }catch(e){
    state.role=null; state.perms=new Set();
    const authArea = $("#auth-area");
    authArea.innerHTML = `<div class="sub">Not authenticated</div><input id="token" placeholder="Session token" autocomplete="off"><button id="login-btn">Login</button>`;
    $("#login-btn").onclick = async () => {
      const r = await fetch("/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:"owner",password:"demo-owner-pass-0001"})});
      const j = await r.json();
      if(r.ok){ state.token=j.token; localStorage.setItem("sgai_token",j.token); $("#token").value=""; await auth(); }
      else alert("Login failed: "+j.error);
    };
  }
}

const SEC_PERM = {
  overview:["report:list","workspace:list"],
  workspaces:["workspace:list"],
  projects:["resource:read","workspace:list","workspace:read"],
  finance:["approval:list"],
  employees:["report:list"],
  marketing:["report:list"],
  crm:["resource:list"],
  ai:["ai:brain:query"],
  approvals:["approval:list"],
  settings:["workspace:manage"],
};

function visible(sec){
  if(state.role === "Owner") return true;
  const perms = state.perms;
  const req = (SEC_PERM[sec]||[]).map(x=>x.replace(/^[+-]/,""));
  return req.some(p => perms.has(p));
}

function bindNav(){
  document.querySelectorAll(".sidebar .item").forEach(el=>{
    el.addEventListener("click", function(e){
      e.stopPropagation();
      document.querySelectorAll(".sidebar .item").forEach(ch=>ch.classList.remove("active"));
      el.classList.add("active");
      showSection(el.dataset.sec);
    });
  });
}

function showSection(sec){
  document.querySelectorAll(".main .card").forEach(c=>c.style.display="none");
  const el = $("#sec-"+sec);
  const show = !!(el && visible(sec));
  if(el) el.style.display = show ? "block" : "none";
  document.querySelectorAll("#nav .item").forEach(i=>{
    i.classList.toggle("active", i.dataset.sec===sec && visible(sec));
  });
}

function switchWorkspace(ws){
  state.ws = ws;
  document.querySelectorAll("#ws-wshop button").forEach(b=>{
    b.classList.toggle("active", b.dataset.ws===ws);
  });
  $("#ws-over-now").textContent = ws;
  $("#ws-proj-now").textContent = ws;
  $("#ws-fin-now").textContent = ws;
  $("#ws-ai-now").textContent = ws;
  $("#ws-chips").innerHTML = "";
  refreshAll();
}

$("#ws-wshop").addEventListener("click", e=>{
  const b = e.target.closest("button[data-ws]");
  if(b) switchWorkspace(b.dataset.ws);
});

async function refreshAll(){
  try{
    const o = await api("/api/dashboard/overview");
    renderOverview(o);
    renderProjects();
    renderFinance();
    renderEmployees();
    renderMarketing();
    renderCrm();
    renderApprovals();
    renderSettings();
    renderRecent(o);
  }catch(e){}
}

async function renderOverview(o){
  $("#ws-over-now").textContent = state.ws;
  const s = $("#summary-cards");
  const pending = (o.pending_approvals||0);
  const audit = (o.recent_audit||[]);
  s.innerHTML = `
    <div class="c ${pending?"bad":"good"}"><div class="v">${pending}</div><div class="l">Pending approvals</div></div>
    <div class="c"><div class="v">${audit.length}</div><div class="l">Recent audit entries</div></div>
    <div class="c"><div class="v">${o.demo_seed?"DEMO":"—"}</div><div class="l">Demo seed active</div></div>
    <div class="c"><div class="v">${state.ws}</div><div class="l">Active workspace</div></div>
  `;
  $("#recent-activities").innerHTML = (o.recent_audit||[]).slice(0,20).map(a=>{
    const d = (a.details||a.target||"");
    return `<div class="kv"><span>${esc(a.action)} <span class="muted">→ ${esc(a.target||"")}</span></span><span class="muted">${new Date(a.created_at||"").toLocaleString()}</span></div>`;
  }).join("") || `<div class="empty">No audit entries yet.</div>`;
  $("#pending-approvals").innerHTML = (o.pending_approvals||[]).map(a=>`<div class="kv"><span>${esc(a.title)}</span><span class="pill pending">pending</span></div>`).join("") || `<div class="empty">No pending approvals.</div>`;
}

async function renderProjects(){
  try{
    const j = await api("/api/dashboard/projects");
    $("#project-list").innerHTML = j.resources.map(r=>`<div class="kv"><span>${esc(r.key||r.name||r.id)}</span><span>${esc(r.workspace_code||r.workspace_id)}</span></div>`).join("") || `<div class="empty">No resources found.</div>`;
  }catch(e){ $("#project-list").innerHTML = `<div class="empty">Failed to load.</div>`; }
}

async function renderFinance(){
  try{
    const j = await api("/api/dashboard/finance");
    $("#finance-list").innerHTML = j.approvals.map(a=>`<div class="kv"><span>${esc(a.title)}</span><span class="pill pending">${esc(a.status||"pending")}</span></div>`).join("") || `<div class="empty">No pending approvals.</div>`;
  }catch(e){ $("#finance-list").innerHTML = `<div class="empty">Failed to load.</div>`; }
}

async function renderEmployees(){
  try{
    const j = await api("/api/dashboard/employees");
    $("#employee-list").innerHTML = j.users.map(u=>`<div class="kv"><span>${esc(u.username)}</span><span>${esc(u.role||"—")}</span></div>`).join("") || `<div class="empty">No employees found.</div>`;
  }catch(e){ $("#employee-list").innerHTML = `<div class="empty">Failed to load.</div>`; }
}

async function renderMarketing(){
  try{
    const j = await api("/api/dashboard/marketing");
    $("#marketing-list").innerHTML = j.marketing_modules.map(m=>`<div class="kv"><span>${esc(m.code)} — ${esc(m.name)}</span><span class="pill ok">${esc(m.status)}</span></div>`).join("") || `<div class="empty">No marketing modules.</div>`;
  }catch(e){ $("#marketing-list").innerHTML = `<div class="empty">Failed to load.</div>`; }
}

async function renderCrm(){
  try{
    const j = await api("/api/dashboard/crm");
    $("#crm-list").innerHTML = j.resources.map(r=>`<div class="kv"><span>${esc(r.key||r.name||r.id)}</span><span>${esc(r.workspace_code||r.workspace_id)}</span></div>`).join("") || `<div class="empty">No resources found.</div>`;
    const leadCount = Array.isArray(j.leads) ? j.leads.length : (j.leads||0);
    $("#crm-stats").innerHTML = `<div class="kv"><span>Leads (M19 social_leads)</span><span class="pill pen">${leadCount}</span></div>`;
    if(Array.isArray(j.leads) && j.leads.length > 0){
      $("#crm-stats").innerHTML += `<div class="muted" style="font-size:12px;margin-top:8px">First: ${esc(j.leads[0].lead_name||j.leads[0].company||"—")}</div>`;
    }
  }catch(e){ $("#crm-list").innerHTML = `<div class="empty">Failed to load.</div>`; $("#crm-stats").innerHTML = `<div class="muted">Failed to load.</div>`; }
}

async function renderApprovals(){
  try{
    const j = await api("/api/approvals");
    const all = j.approvals || [];
    const pend = all.filter(a=>a.status==="pending");
    $("#pending-approvals2").innerHTML = pend.map(a=>`<div class="kv"><span>${esc(a.title)}</span><span class="pill ${a.status}">${esc(a.status)}</span></div>`).join("") || `<div class="empty">No approvals.</div>`;
    $("#all-approvals").innerHTML = all.map(a=>`<div class="kv"><span>${esc(a.title)}</span><span class="pill ${a.status}">${esc(a.status)}</span></div>`).join("") || `<div class="empty">No approvals.</div>`;
  }catch(e){ $("#pending-approvals2").innerHTML = `<div class="empty">Failed to load.</div>`; $("#all-approvals").innerHTML = `<div class="empty">Failed to load.</div>`; }
}

async function renderSettings(){
  try{
    const j = await api("/api/system");
    $("#cfg-json").textContent = JSON.stringify(j, null, 2);
    try{
      const j2 = await api("/api/dashboard/settings");
      $("#settings-roles").innerHTML = (j2.roles||[]).map(r=>`<div class="kv"><span>${esc(r)}</span></div>`).join("") || `<div class="empty">No roles.</div>`;
    }catch(e2){ $("#settings-roles").innerHTML = `<div class="muted">settings unavailable</div>`; }
  }catch(e){
    $("#cfg-json").textContent = "System: " + (e.message||"n/a");
    $("#settings-roles").innerHTML = `<div class="muted">settings unavailable</div>`;
  }
  await renderUserManagement();
}

async function renderUserManagement(){
  const box = $("#users-manage");
  if(!box) return;
  try{
    const j = await api("/api/users");
    const users = (j.users||[]).sort((a,b)=>a.id-b.id);
    let rows = "";
    for(const u of users) {
      const isAct = Boolean(u.active);
      rows += "<tr>" +
        "<td style='padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6'>" + esc(u.username) + "</td>" +
        "<td style='padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6'>" + esc(u.name) + "</td>" +
        "<td style='padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6'>" + esc(u.role) + "</td>" +
        "<td style='padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6'>" + esc(u.workspace_id || "?") + "</td>" +
        "<td style='padding:6px 8px;border-bottom:1px solid var(--line)'><span class='pill " + (isAct ? 'ok' : 'bad') + "'>" + (isAct ? 'active' : 'inactive') + "</span></td>" +
        "<td style='padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;display:flex;gap:6px'>" +
          "<button class='act btn-edit' data-id='" + u.id + "'>Edit</button>" +
          "<button class='act btn-toggle' data-id='" + u.id + "' data-active='" + (isAct ? "1" : "0") + "'>" + (isAct ? "Deactivate" : "Activate") + "</button>" +
        "</td>" +
      "</tr>";
    }
    box.innerHTML = "<div style='display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:8px'>" +
      "<h4 style='margin:0;font-size:13px;color:var(--muted)'>Manage users (Owner/Manager only)</h4>" +
      "<button id='cm-add' style='padding:4px 10px;border-radius:5px;border:1px solid var(--accent);background:var(--accent);color:#06101f;font-size:11px'>+ Add user</button>" +
    "</div>" +
    "<table style='width:100%;border-collapse:collapse;font-size:12px'>" +
      "<thead><tr style='background:#1a2744;color:#e6edf6'>" +
        "<th style='padding:6px 8px;text-align:left;border-bottom:1px solid var(--line)'>Username</th>" +
        "<th style='padding:6px 8px;text-align:left;border-bottom:1px solid var(--line)'>Name</th>" +
        "<th style='padding:6px 8px;text-align:left;border-bottom:1px solid var(--line)'>Role</th>" +
        "<th style='padding:6px 8px;text-align:left;border-bottom:1px solid var(--line)'>Workspace</th>" +
        "<th style='padding:6px 8px;text-align:left;border-bottom:1px solid var(--line)'>Status</th>" +
        "<th style='padding:6px 8px;text-align:left;border-bottom:1px solid var(--line)'>Actions</th>" +
      "</tr></thead>" +
      "<tbody>" + (rows || "<tr><td colspan='6' style='padding:8px;color:var(--muted)'>No users found.</td></tr>") + "</tbody>" +
    "</table>" +
    "<div class='muted' style='font-size:11px;margin-top:6px'>Owner/Manager only.</div>";

    box.querySelectorAll(".btn-edit").forEach(b=>{
      b.onclick = ()=>{
        const id = b.dataset.id;
        const u = users.find(x=>String(x.id)===String(id));
        if(!u) return;
        const modal = $("#user-form");
        modal.dataset.editId = String(u.id);
        modal.style.display = "block";
        $("#uf-msg").textContent = "Editing user #" + u.id + " (leave password blank to keep unchanged)";
        $("#uf-username").value = u.username||"";
        $("#uf-password").value = "";
        $("#uf-name").value = u.name||"";
        $("#uf-role").value = u.role||"";
        $("#uf-workspace").value = u.workspace_id||"";
      };
    });

    box.querySelectorAll(".btn-toggle").forEach(b=>{
      b.onclick = async ()=>{
        const id = b.dataset.id;
        const isAct = b.dataset.active === "1";
        const action = isAct ? "deactivate" : "activate";
        if(!confirm((isAct ? "Deactivate" : "Activate") + " this user?")) return;
        try{
          await api("/api/users/"+id+"/"+action, {method:"POST"});
          await renderUserManagement();
        }catch(e){ alert("Action failed: "+e.message); }
      };
    });

    $("#cm-add").onclick = ()=>{
      const modal = $("#user-form");
      delete modal.dataset.editId;
      modal.style.display = "block";
      $("#uf-msg").textContent = "";
      $("#uf-username").value = "";
      $("#uf-password").value = "";
      $("#uf-name").value = "";
      setTimeout(()=>$("#uf-username").focus(), 50);
    };

    $("#uf-cancel").onclick = ()=>{
      const modal = $("#user-form");
      delete modal.dataset.editId;
      modal.style.display = "none";
    };

    $("#uf-submit").onclick = async ()=>{
      const modal = $("#user-form");
      const editId = modal.dataset.editId;
      const msg = $("#uf-msg");
      msg.textContent = "Saving?";
      try{
        const body = {
          username: $("#uf-username").value.trim(),
          password: $("#uf-password").value,
          name: $("#uf-name").value.trim(),
          role: $("#uf-role").value.trim(),
          workspace_id: $("#uf-workspace").value.trim(),
        };
        if(editId){
          if(!body.username||!body.name||!body.role||!body.workspace_id) throw new Error("Username, name, role, workspace required");
          if(!body.password) delete body.password;
          await api("/api/users/"+editId, {method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
          msg.textContent = "User updated.";
        } else {
          if(!body.username||!body.password||!body.name||!body.role||!body.workspace_id) throw new Error("All fields required");
          await api("/api/users", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
          msg.textContent = "User created.";
        }
        delete modal.dataset.editId;
        modal.style.display = "none";
        await renderUserManagement();
      }catch(e){ msg.textContent = "Error: "+e.message; }
    };
  }catch(e){
    box.innerHTML = "<div class='empty'>User management unavailable: " + esc(e.message) + "</div>";
  }
}
async function renderRecent(o){
  const box = $("#recent-activities");
  const rows = (o.recent_audit||[]).slice(0,20).map(a=>{
    const d = (a.details||a.target||"");
    return `<div class="kv"><span>${esc(a.action)} <span class="muted">→ ${esc(a.target||"")}</span></span><span class="muted">${new Date(a.created_at||"").toLocaleString()}</span></div>`;
  }).join("");
  box.innerHTML = rows || `<div class="empty">No audit entries yet.</div>`;
}

async function askAI(q){
  const box = $("#ai-resp");
  box.textContent = "Thinking…";
  try{
    const r = await fetch("/api/ai-brain", { headers:{"Authorization":"Bearer "+state.token}, method:"GET" });
    const j = await r.json().catch(()=>({}));
    let body = j.brain || {};
    body.agents = [];
    try{
      const agentsRes = await fetch("/api/ai-brain/agents", { headers:{"Authorization":"Bearer "+state.token} });
      const a2 = await agentsRes.json().catch(()=>({}));
      body.agents = a2.agents || [];
      body.workspace = state.ws;
      body.role = state.role;
    }catch(e){ body.agents = []; }
    box.textContent = JSON.stringify(body, null, 2);
  }catch(e){
    box.textContent = "Brain error: " + e.message;
  }
}

$("#ai-send").onclick = () => askAI($("#ai-input").value);
$("#ai-input").addEventListener("keydown", e=>{ if(e.key==="Enter") askAI($("#ai-input").value); });

(function(){
  auth().then(() => {
    bindNav();
    switchWorkspace(state.ws || "SSC");
  }).catch(function(e) { console.error('Init failed:', e); });
})();
