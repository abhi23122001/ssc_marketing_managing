import sys

def main():
    path = "foundation/dashboard/dashboard.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Target snippet in renderLiveInternetResearch
    target = """        <!-- Recommendations -->
        <div style="background:#0b1120;padding:12px;border-radius:8px;border:1px solid var(--line);margin-bottom:12px">
          <h4 style="margin:0 0 8px;color:var(--accent);font-size:13px">&#127919; Actionable Business Directives &amp; Next Steps</h4>
          <ul style="margin:0;padding-left:18px;font-size:12px;color:var(--text);line-height:1.6">
            ${recs.length ? recs.map(r=>`<li>${esc(r)}</li>`).join("") : '<li>Incorporate findings into tender rate analysis and site methodology.</li>'}
          </ul>
        </div>"""

    replacement = """        <!-- Recommendations -->
        <div style="background:#0b1120;padding:12px;border-radius:8px;border:1px solid var(--line);margin-bottom:12px">
          <h4 style="margin:0 0 8px;color:var(--accent);font-size:13px">&#127919; Actionable Business Directives &amp; Next Steps</h4>
          <ul style="margin:0;padding:0;list-style:none;font-size:12px;color:var(--text);line-height:1.6">
            ${recs.length ? recs.map((r, ri)=>`
              <li style="display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:8px;padding:6px 10px;background:#1e293b;border-radius:6px;border:1px solid var(--line)">
                <span><strong>#${ri+1}.</strong> ${esc(r)}</span>
                <button class="btn btn-primary btn-sm" style="font-size:11px;padding:4px 10px;white-space:nowrap;flex-shrink:0" onclick="convertResearchRecToTask(${JSON.stringify(r)}, ${JSON.stringify(query)}, ${JSON.stringify(category)})">
                  + Convert to Task
                </button>
              </li>
            `).join("") : '<li>Incorporate findings into tender rate analysis and site methodology.</li>'}
          </ul>
        </div>"""

    if target not in content:
        print("Target not found!")
        return 1

    content = content.replace(target, replacement)

    # Now add convertResearchRecToTask function definition
    fn_code = """
// -----------------------------------------------------------------------------
// Convert Research Recommendation to Task
// -----------------------------------------------------------------------------
window.convertResearchRecToTask = async function(recText, query, category){
  if(!recText) return toast("No recommendation text to convert", "bad");
  try {
    const titleSnippet = recText.length > 60 ? recText.slice(0, 57) + "..." : recText;
    const res = await api(`/api/tasks?workspace=${encodeURIComponent(state.ws || 'SSC')}`, {
      method: "POST",
      body: {
        title: `[AI Directive] ${titleSnippet}`,
        description: `Source Recommendation:\n${recText}\n\nContext Query: ${query || 'Industry Research'}\nDomain Category: ${category || 'survey_tech'}\nGenerated via: SHAH Group Autonomous Daily AI Research Engine`,
        priority: "high",
        category: "operations"
      }
    });
    if(res && (res.task || res.ok)){
      const tid = (res.task && (res.task.id || res.task.task_id)) ? `#${res.task.id || res.task.task_id}` : "";
      toast(`Task created successfully ${tid}!`, "good");
      // If task feed is visible or tasks subtab exists, refresh
      if(typeof renderTasks === "function") renderTasks();
    } else {
      toast("Task created successfully", "good");
    }
  } catch(err){
    console.error("convertResearchRecToTask error:", err);
    toast("Failed to convert task: " + err.message, "bad");
  }
};
"""
    # Insert right before renderLiveInternetResearch()
    if "window.convertResearchRecToTask" not in content:
        insert_marker = "function renderLiveInternetResearch(){"
        if insert_marker in content:
            content = content.replace(insert_marker, fn_code + "\n" + insert_marker)
            print("Successfully injected convertResearchRecToTask!")
        else:
            print("Could not find renderLiveInternetResearch function marker!")
            return 1

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Updated dashboard.html successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
