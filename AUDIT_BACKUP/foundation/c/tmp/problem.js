        ${(users.map(u=>`<tr>
          <td style="padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6">${esc(u.username)}</td>
          <td style="padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6">${esc(u.name)}</td>
          <td style="padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6">${esc(u.role)}</td>
          <td style="padding:6px 8px;border-bottom:1px solid var(--line);color:#e6edf6">${esc(u.workspace_id||"—")}</td>
          <td style="padding:6px 8px;border-bottom:1px solid var(--line)"><span class="pill ${u.active?'ok':'bad'}">${u.active?'active':'inactive'}</span></td>
          <td style="padding:6px 8px;border-bottom:1px solid var(--line);text-align:left">
            <button class="act btn-edit" data-id="${u.id}">Edit</button>
            <button class="act btn-deactivate" data-id="${u.id}">Deactivate</button>
          </td>
        </tr>`)).join("")||`<tr><td colspan="6" style="padding:12px;color:var(--muted);text-align:center">No users.</td></tr>`}