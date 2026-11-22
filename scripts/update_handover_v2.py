# -*- coding: utf-8 -*-
"""Update master handover and test records with ChatGPT layout & DOM fix."""

# 1. Update OVERNIGHT_TASK_LEDGER.md
ledger_path = "OVERNIGHT_TASK_LEDGER.md"
with open(ledger_path, "r", encoding="utf-8") as f:
    text = f.read()

new_tasks = """| **TSK-027** | Root-Cause HTML DOM Tag Balance Fix | `dashboard.html:2097-2104` | Fixed extra `</div>` at end of canvas gallery that closed `<main>` early | **COMPLETED** |
| **TSK-028** | Enterprise Sidebar & Subnav Styling | `dashboard.html:85-180` | Restored active pills, hover effects, icon alignments in Dark/Light themes | **COMPLETED** |
| **TSK-029** | ChatGPT-Style AI Brain Interface | `#sec-ai / #sub-ai-assistant` | Full ChatGPT layout with left sidebar, prompt cards, message stream, dock | **COMPLETED** |
| **TSK-030** | Multi-Turn Conversational Memory | `initChatGptEngine()` | History list, session titles, instant SQLite grounded responses, task conversion | **COMPLETED** |
| **TSK-031** | Full 11-Module CDP Verification | `verify_all_modules_and_errors.js` | All 11 modules and 16 subtabs verified; 0 console errors; 0 exceptions | **COMPLETED** |
"""

target = "| **TSK-026** | Complete Master Handover & Operating Guide | `MASTER_HANDOVER.md` | Executive summary, baseline comparison, operating guide | **COMPLETED** |\n"
if target in text and "TSK-027" not in text:
    text = text.replace(target, target + new_tasks)
    with open(ledger_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated OVERNIGHT_TASK_LEDGER.md")

# 2. Update SHAH_GROUP_AI_OS_COMPLETE_MASTER_HANDOVER.md
handover_path = "SHAH_GROUP_AI_OS_COMPLETE_MASTER_HANDOVER.md"
with open(handover_path, "r", encoding="utf-8") as f:
    htext = f.read()

addendum = """
---

## 8. Post-Handover Refinements: ChatGPT-Style AI Brain & Complete DOM Tag Restoration

In response to immediate user feedback regarding layout alignment and the AI Brain experience:
1. **Root-Cause DOM Tag Imbalance Resolved**:
   - Identified an extraneous `</div>` tag in the canvas gallery inside `#sec-marketing`. This closing tag caused the browser HTML parser to prematurely close the main `<main id="main">` container, ejecting `#sec-crm`, `#sec-ai`, `#sec-approvals`, `#sec-integrations`, and `#sec-settings` into `<body>` where `overflow: hidden` made them invisible.
   - Restored exact HTML tag balance (`Final stack depth: 0`). All 11 corporate modules now reside securely within `<main id="main">`.
2. **ChatGPT-Style AI Brain Suite (`#sec-ai`)**:
   - **Left AI Sidebar**: Includes a prominent `+ New Chat` button, persona selector (⚡ Universal Business Intelligence, 🛰️ DGPS & Drone Survey, 🏗️ Highway & Civil Engineer, 💰 Finance & GST Advisor, 📑 Tenders & GeM Specialist), and persistent conversation history.
   - **Centered Welcome Hero**: Features 4 clickable prompt starter cards covering financial P&L, DGPS tolerances, MoRTH specifications, and 18% GST quotations.
   - **Conversational Message Stream**: User speech bubbles on the right and AI response cards on the left with formatted bullets, intent pills, and one-click `📋 Copy` and `➕ Convert to Task` action buttons.
   - **ChatGPT Floating Bottom Dock**: Centered capsule with auto-growing textarea, instant send button (`➤`), and company database attribution footer.
3. **Comprehensive CDP Headless Browser Audit**:
   - Ran automated test suite `scripts/verify_all_modules_and_errors.js`.
   - Verified all 11 modules (`overview`, `workspaces`, `projects`, `finance`, `employees`, `marketing`, `crm`, `ai`, `approvals`, `integrations`, `settings`) and all subtabs.
   - Result: **100% PASS &bull; 0 Console Errors &bull; 0 Uncaught Exceptions**.
"""

if "Post-Handover Refinements" not in htext:
    htext += addendum
    with open(handover_path, "w", encoding="utf-8") as f:
        f.write(htext)
    print("Updated SHAH_GROUP_AI_OS_COMPLETE_MASTER_HANDOVER.md")
