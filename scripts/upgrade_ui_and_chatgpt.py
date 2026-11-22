# -*- coding: utf-8 -*-
"""Comprehensive UI Layout Restoration and ChatGPT-style AI Brain Suite.
Upgrades:
1. Complete base layout CSS: Header layout, Sidebar layout (.sidebar .item), Subnav, Tables, Forms, Dark & Light theme consistency.
2. ChatGPT-Style Layout for AI Brain (#sec-ai / #sub-ai-assistant):
   - ChatGPT container shell with left AI sidebar (+ New Chat, Persona switcher, conversation history).
   - Centered message stream (max-width 840px).
   - ChatGPT Welcome Hero with 4 clickable prompt starter cards when empty.
   - Multi-turn conversation messages with User bubble and AI response card.
   - AI response actions: Copy, Convert to Task, Regenerate.
   - ChatGPT floating bottom dock with auto-resize textarea and send button.
   - Model info footer.
3. Chat engine script: multi-turn memory, localStorage persistence, instant grounded answers via /api/intelligence/ask.
"""

import sys

def main():
    path = "foundation/dashboard/dashboard.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # -------------------------------------------------------------------------
    # 1. UPGRADE BASE & THEME CSS
    # -------------------------------------------------------------------------
    # We locate the start of <style> and inject comprehensive CSS
    style_start = "<style>"
    if style_start not in content:
        print("Error: <style> tag not found")
        return 1

    # Find the end of the base CSS or replace the top CSS block
    end_marker = "/* Universial Card & Component Enhancements */"
    if end_marker not in content:
        end_marker = "/* Universal Card & Component Enhancements */"

    # Let's inspect where to replace in <style>
    style_idx = content.find("<style>")
    body_idx = content.find("<body>")

    # Let's extract the existing style block
    style_block_end = content.find("</style>")
    existing_styles = content[style_idx+7:style_block_end]

    # Enhanced CSS to prepend/ensure completeness
    enhanced_css = """
  /* =========================================================================
     SHAH GROUP AI OS — COMPLETE ENTERPRISE MASTER STYLESHEET
     Liquid Glass Dark & Light Themes | ChatGPT AI Brain | Production Polished
     ========================================================================= */
  * { box-sizing: border-box; }
  html, body { height: 100%; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    font-size: 14px;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow: hidden;
  }

  /* ---- Header Layout Fixed Non-Overlap ---- */
  header.top {
    height: 64px !important;
    min-height: 64px !important;
    max-height: 64px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    padding: 0 20px !important;
    border-bottom: 1px solid var(--line) !important;
    background: var(--panel) !important;
    backdrop-filter: var(--glass-blur) !important;
    -webkit-backdrop-filter: var(--glass-blur) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 900 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
    gap: 16px !important;
  }
  header.top .brand {
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 220px;
  }
  header.top h1 {
    font-size: 16px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    color: var(--text) !important;
    line-height: 1.2 !important;
    letter-spacing: -0.3px !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
  }
  header.top .sub {
    font-size: 11px !important;
    color: var(--muted) !important;
    margin: 2px 0 0 !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    font-weight: 500 !important;
  }
  .wshop {
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 20px !important;
    padding: 3px 6px !important;
  }
  .wshop button {
    border: 0 !important;
    background: transparent !important;
    color: var(--muted) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    padding: 4px 10px !important;
    border-radius: 14px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
  }
  .wshop button:hover {
    color: var(--text) !important;
  }
  .wshop button.active {
    background: var(--accent) !important;
    color: #06101f !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(56,189,248,0.3) !important;
  }
  body.theme-light .wshop button.active {
    background: #0284c7 !important;
    color: #ffffff !important;
  }
  .global-search-box {
    position: relative !important;
    display: flex !important;
    align-items: center !important;
    flex: 1 !important;
    max-width: 380px !important;
    min-width: 180px !important;
  }
  .global-search-icon {
    position: absolute !important;
    left: 12px !important;
    color: var(--muted) !important;
    pointer-events: none !important;
    font-size: 13px !important;
  }
  .global-search-input {
    width: 100% !important;
    padding: 7px 14px 7px 32px !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    border: 1px solid var(--line) !important;
    background: var(--input-bg) !important;
    color: var(--input-color) !important;
    transition: all 0.2s ease !important;
  }
  .global-search-input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.2) !important;
  }

  /* ---- Main Two-Column Layout ---- */
  .layout {
    display: flex !important;
    height: calc(100vh - 64px) !important;
    overflow: hidden !important;
  }
  .sidebar {
    width: 240px !important;
    min-width: 240px !important;
    max-width: 240px !important;
    flex-shrink: 0 !important;
    height: calc(100vh - 64px) !important;
    background: var(--panel) !important;
    border-right: 1px solid var(--line) !important;
    display: flex !important;
    flex-direction: column !important;
    overflow-y: auto !important;
    padding: 12px 8px !important;
  }
  .sidebar h3 {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    color: var(--muted) !important;
    padding: 8px 12px 6px !important;
    margin: 0 0 4px 0 !important;
    font-weight: 700 !important;
  }
  .sidebar .nav {
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
  }
  .sidebar .item {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    text-decoration: none !important;
    border-left: 3px solid transparent !important;
    user-select: none !important;
  }
  .sidebar .item:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    color: var(--text) !important;
    transform: translateX(2px) !important;
  }
  .sidebar .item.active {
    background: rgba(56, 189, 248, 0.12) !important;
    color: var(--accent) !important;
    font-weight: 700 !important;
    border-left: 3px solid var(--accent) !important;
  }
  .sidebar .item .ico {
    font-size: 16px !important;
    width: 20px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  body.theme-light .sidebar {
    background: #ffffff !important;
    border-color: #e2e8f0 !important;
  }
  body.theme-light .sidebar h3 {
    color: #64748b !important;
  }
  body.theme-light .sidebar .item {
    color: #475569 !important;
  }
  body.theme-light .sidebar .item:hover {
    background: #f1f5f9 !important;
    color: #0f172a !important;
  }
  body.theme-light .sidebar .item.active {
    background: #e0f2fe !important;
    color: #0284c7 !important;
    border-left: 3px solid #0284c7 !important;
  }

  .main {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow-y: auto !important;
    height: calc(100vh - 64px) !important;
    background: var(--bg) !important;
    padding: 20px !important;
    min-width: 0 !important;
  }
  .main > section {
    margin-bottom: 20px !important;
  }

  /* ---- Universal Subnav Tabs ---- */
  .subnav {
    display: flex !important;
    gap: 6px !important;
    flex-wrap: wrap !important;
    margin-bottom: 16px !important;
    padding: 4px !important;
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
  }
  .subnav button {
    padding: 7px 14px !important;
    border-radius: 7px !important;
    border: 1px solid transparent !important;
    background: transparent !important;
    color: var(--muted) !important;
    cursor: pointer !important;
    font-weight: 600 !important;
    font-size: 12px !important;
    transition: all 0.15s ease !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    white-space: nowrap !important;
  }
  .subnav button:hover {
    color: var(--text) !important;
    background: rgba(255, 255, 255, 0.05) !important;
  }
  .subnav button.active {
    background: var(--accent) !important;
    color: #06101f !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(56, 189, 248, 0.3) !important;
  }
  body.theme-light .subnav {
    background: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
  }
  body.theme-light .subnav button {
    color: #475569 !important;
  }
  body.theme-light .subnav button:hover {
    color: #0f172a !important;
    background: #e2e8f0 !important;
  }
  body.theme-light .subnav button.active {
    background: #0284c7 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(2, 132, 199, 0.3) !important;
  }

  /* ---- Universal Cards & Containers ---- */
  .card {
    background: var(--panel) !important;
    border: var(--card-border) !important;
    border-radius: 14px !important;
    padding: 20px !important;
    backdrop-filter: var(--glass-blur) !important;
    -webkit-backdrop-filter: var(--glass-blur) !important;
    box-shadow: var(--glass-shadow) !important;
  }
  .summary {
    display: grid !important;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)) !important;
    gap: 12px !important;
  }
  .summary .c {
    background: var(--panel-2) !important;
    border: 1px solid var(--line) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    cursor: pointer !important;
  }
  .summary .c:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
  }
  .summary .c .v {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: var(--text) !important;
  }
  .summary .c .l {
    font-size: 11px !important;
    color: var(--muted) !important;
    margin-top: 4px !important;
    font-weight: 500 !important;
  }
  .summary .c.ok .v { color: var(--good) !important; }
  .summary .c.bad .v { color: var(--bad) !important; }

  /* =========================================================================
     CHATGPT-STYLE AI BRAIN INTERFACE CSS
     ========================================================================= */
  .chatgpt-layout {
    display: flex;
    height: calc(100vh - 170px);
    min-height: 580px;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: var(--glass-shadow);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
  }
  .chatgpt-sidebar {
    width: 250px;
    flex-shrink: 0;
    background: var(--panel-2);
    border-right: 1px solid var(--line);
    display: flex;
    flex-direction: column;
    padding: 14px 10px;
    gap: 10px;
  }
  .chatgpt-new-chat-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 14px;
    border-radius: 10px;
    background: var(--accent);
    color: #06101f;
    font-weight: 700;
    font-size: 13px;
    cursor: pointer;
    border: 0;
    transition: all 0.15s ease;
    box-shadow: 0 2px 8px rgba(56, 189, 248, 0.25);
  }
  .chatgpt-new-chat-btn:hover {
    background: #0ea5e9;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
  }
  body.theme-light .chatgpt-new-chat-btn {
    background: #0284c7;
    color: #ffffff;
  }
  .chatgpt-persona-box {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .chatgpt-persona-box label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--muted);
    font-weight: 700;
  }
  .chatgpt-persona-select {
    width: 100%;
    padding: 7px 10px;
    border-radius: 8px;
    font-size: 12px;
    border: 1px solid var(--line);
    background: var(--input-bg);
    color: var(--input-color);
    cursor: pointer;
  }
  .chatgpt-history-section {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    margin-top: 6px;
  }
  .chatgpt-history-title {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: var(--muted);
    font-weight: 700;
    margin-bottom: 6px;
    padding: 0 4px;
  }
  .chatgpt-history-list {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .chatgpt-history-item {
    padding: 8px 10px;
    border-radius: 8px;
    font-size: 12px;
    color: var(--muted);
    cursor: pointer;
    transition: all 0.12s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: flex;
    align-items: center;
    gap: 8px;
    border: 1px solid transparent;
  }
  .chatgpt-history-item:hover {
    background: rgba(255, 255, 255, 0.05);
    color: var(--text);
  }
  .chatgpt-history-item.active {
    background: rgba(56, 189, 248, 0.12);
    color: var(--accent);
    border-color: rgba(56, 189, 248, 0.25);
    font-weight: 600;
  }
  .chatgpt-main {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
    position: relative;
    background: var(--bg);
  }
  .chatgpt-topbar {
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    border-bottom: 1px solid var(--line);
    background: var(--panel);
  }
  .chatgpt-model-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    color: var(--text);
  }
  .chatgpt-model-badge .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--good);
    box-shadow: 0 0 6px var(--good);
  }
  .chatgpt-messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    scroll-behavior: smooth;
  }
  .chatgpt-messages-inner {
    max-width: 840px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .chatgpt-welcome-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 40px 10px 20px;
    gap: 10px;
  }
  .chatgpt-welcome-icon {
    font-size: 44px;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .chatgpt-welcome-title {
    font-size: 22px;
    font-weight: 800;
    color: var(--text);
    margin: 0;
    letter-spacing: -0.4px;
  }
  .chatgpt-welcome-subtitle {
    font-size: 13px;
    color: var(--muted);
    max-width: 520px;
    line-height: 1.5;
    margin: 0;
  }
  .chatgpt-prompt-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    max-width: 780px;
    width: 100%;
    margin: 20px auto 0;
  }
  @media (max-width: 720px) {
    .chatgpt-prompt-grid { grid-template-columns: 1fr; }
    .chatgpt-sidebar { display: none; }
  }
  .chatgpt-prompt-card {
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 14px 16px;
    cursor: pointer;
    text-align: left;
    transition: all 0.15s ease;
  }
  .chatgpt-prompt-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.18);
  }
  .chatgpt-prompt-card h4 {
    font-size: 13px;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .chatgpt-prompt-card p {
    font-size: 11px;
    color: var(--muted);
    margin: 0;
    line-height: 1.4;
  }
  .chatgpt-msg-row {
    display: flex;
    gap: 12px;
    animation: fadeIn 0.2s ease;
  }
  .chatgpt-msg-row.user {
    justify-content: flex-end;
  }
  .chatgpt-msg-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    flex-shrink: 0;
  }
  .chatgpt-msg-avatar.ai {
    background: linear-gradient(135deg, #0284c7, #6366f1);
    color: #fff;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  }
  .chatgpt-msg-avatar.user {
    background: var(--panel-2);
    border: 1px solid var(--line);
    color: var(--text);
  }
  .chatgpt-msg-content {
    max-width: 82%;
    padding: 14px 18px;
    border-radius: 14px;
    font-size: 13px;
    line-height: 1.6;
  }
  .chatgpt-msg-row.user .chatgpt-msg-content {
    background: var(--panel-2);
    border: 1px solid var(--line);
    color: var(--text);
    border-top-right-radius: 4px;
  }
  .chatgpt-msg-row.assistant .chatgpt-msg-content {
    background: var(--panel);
    border: 1px solid var(--line);
    color: var(--text);
    border-top-left-radius: 4px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    flex: 1;
  }
  .chatgpt-msg-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px solid var(--line);
  }
  .chatgpt-input-dock {
    padding: 12px 20px 14px;
    background: var(--panel);
    border-top: 1px solid var(--line);
  }
  .chatgpt-input-wrapper {
    max-width: 840px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .chatgpt-input-box {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 24px;
    padding: 6px 14px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }
  .chatgpt-input-box:focus-within {
    border-color: var(--accent);
    box-shadow: 0 4px 20px rgba(56, 189, 248, 0.25);
  }
  .chatgpt-input-box textarea {
    flex: 1;
    background: transparent !important;
    border: 0 !important;
    color: var(--input-color) !important;
    padding: 8px 4px !important;
    font-size: 13px !important;
    resize: none;
    max-height: 120px;
    line-height: 1.5;
  }
  .chatgpt-input-box textarea:focus {
    outline: none !important;
    box-shadow: none !important;
  }
  .chatgpt-send-btn {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    border: 0;
    background: var(--accent);
    color: #06101f;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 14px;
    font-weight: bold;
    transition: all 0.15s ease;
    flex-shrink: 0;
  }
  .chatgpt-send-btn:disabled {
    opacity: 0.35;
    cursor: not-allowed;
    background: var(--line);
    color: var(--muted);
  }
  .chatgpt-send-btn:not(:disabled):hover {
    transform: scale(1.08);
    box-shadow: 0 2px 8px rgba(56,189,248,0.4);
  }
  .chatgpt-input-footer {
    font-size: 11px;
    color: var(--muted);
    text-align: center;
    margin: 0;
  }
"""

    # We will prepend enhanced_css inside <style>
    content = content.replace("<style>", "<style>\n" + enhanced_css)

    # -------------------------------------------------------------------------
    # 2. UPGRADE #sub-ai-assistant HTML TO CHATGPT INTERFACE
    # -------------------------------------------------------------------------
    old_sub_assistant_start = '<!-- Sub 1: Universal Assistant (Ask Anything) -->'
    old_sub_assistant_end = '<!-- Sub 2: Autonomous Daily Research & Live Web Research -->'

    p1 = content.find(old_sub_assistant_start)
    p2 = content.find(old_sub_assistant_end)

    if p1 != -1 and p2 != -1:
        new_chatgpt_html = """<!-- Sub 1: Universal Assistant (ChatGPT-Level Interface) -->
      <div id="sub-ai-assistant">
        <div class="chatgpt-layout">
          <!-- Left AI Sidebar -->
          <div class="chatgpt-sidebar">
            <button class="chatgpt-new-chat-btn" id="btn-chatgpt-new" onclick="startNewChatGptSession()">
              <span>+</span> New Chat
            </button>

            <div class="chatgpt-persona-box" style="margin-top:6px">
              <label>AI Persona & Domain</label>
              <select class="chatgpt-persona-select" id="chatgpt-persona-select" onchange="switchChatGptPersona()">
                <option value="universal">⚡ Universal Business Intelligence</option>
                <option value="survey">🛰️ DGPS & Drone Survey Specialist</option>
                <option value="civil">🏗️ Highway & Civil Engineer (MoRTH)</option>
                <option value="finance">💰 Finance, GST & Billing Advisor</option>
                <option value="tenders">📑 Tenders, BOQ & GeM Specialist</option>
              </select>
            </div>

            <div class="chatgpt-history-section">
              <div class="chatgpt-history-title">Recent Conversations</div>
              <div class="chatgpt-history-list" id="chatgpt-history-list">
                <!-- Dynamically populated -->
              </div>
            </div>

            <div style="padding-top:8px;border-top:1px solid var(--line);font-size:11px;color:var(--muted)">
              <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
                <span class="pill ok" style="padding:2px 6px;font-size:10px">100% Free Tier</span>
                <span>Hermes &bull; SQLite</span>
              </div>
              <div>Zero paid API billing enforced.</div>
            </div>
          </div>

          <!-- Right Chat Viewport -->
          <div class="chatgpt-main">
            <!-- Top bar -->
            <div class="chatgpt-topbar">
              <div class="chatgpt-model-badge">
                <span class="dot"></span>
                <span id="chatgpt-active-model-label">SHAH Group AI OS 3.5 &bull; Universal Assistant</span>
              </div>
              <div style="display:flex;align-items:center;gap:8px">
                <button class="btn btn-secondary btn-xs" onclick="clearCurrentChatGptConversation()">Clear Chat</button>
              </div>
            </div>

            <!-- Messages Stream -->
            <div class="chatgpt-messages-container" id="chatgpt-messages-container">
              <div class="chatgpt-messages-inner" id="chatgpt-messages-inner">
                <!-- Welcome Hero (shown when messages is empty) -->
                <div class="chatgpt-welcome-hero" id="chatgpt-welcome-hero">
                  <div class="chatgpt-welcome-icon">&#10024;</div>
                  <h3 class="chatgpt-welcome-title">How can SHAH Group AI assist you today?</h3>
                  <p class="chatgpt-welcome-subtitle">
                    Grounded strictly in your live company database, project registries, Survey of India SOPs, and MoRTH specifications. Ask in Hindi, English, or Hinglish.
                  </p>

                  <div class="chatgpt-prompt-grid">
                    <div class="chatgpt-prompt-card" onclick="sendChatGptQuickPrompt('Total operating profit kitna hua hai aur kitna baki hai?')">
                      <h4>&#128202; Financial P&amp;L Status</h4>
                      <p>View realized revenue, operational outflows, net margins &amp; outstanding receivables.</p>
                    </div>
                    <div class="chatgpt-prompt-card" onclick="sendChatGptQuickPrompt('DGPS aur RTK survey accuracy ke kya standard hain?')">
                      <h4>&#128752; DGPS &amp; Drone SOP</h4>
                      <p>Survey of India GTS baseline tolerances, PDOP limits, and aerial photogrammetry specs.</p>
                    </div>
                    <div class="chatgpt-prompt-card" onclick="sendChatGptQuickPrompt('MoRTH Section 300 earthwork compaction tolerances kya hain?')">
                      <h4>&#127959; MoRTH Civil Standards</h4>
                      <p>Highway subgrade compaction, dry density testing &amp; IRC:SP:19 smoothness limits.</p>
                    </div>
                    <div class="chatgpt-prompt-card" onclick="sendChatGptQuickPrompt('How to create an estimate and quotation with 18% GST?')">
                      <h4>&#128221; Quotations &amp; GST</h4>
                      <p>Guidance on creating GST Tax Invoices (Rule 46) and commercial rates for tenders.</p>
                    </div>
                  </div>
                </div>

                <!-- Messages inserted here dynamically -->
                <div id="chatgpt-message-stream" style="display:flex;flex-direction:column;gap:16px"></div>
              </div>
            </div>

            <!-- Bottom Floating Dock -->
            <div class="chatgpt-input-dock">
              <div class="chatgpt-input-wrapper">
                <div class="chatgpt-input-box">
                  <textarea id="chatgpt-user-input" rows="1" placeholder="Message SHAH Group AI... (Press Enter to send, Shift+Enter for new line)" onkeydown="handleChatGptKeydown(event)" oninput="autoGrowChatGptTextarea(this)"></textarea>
                  <button class="chatgpt-send-btn" id="btn-chatgpt-send" onclick="sendChatGptMessage()" title="Send Message">
                    &#10148;
                  </button>
                </div>
                <div class="chatgpt-input-footer">
                  SHAH Group AI OS &bull; Grounded strictly in company databases and engineering standards &bull; Zero Paid API Billing
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      \n"""
        content = content[:p1] + new_chatgpt_html + content[p2:]
        print("Successfully replaced #sub-ai-assistant with ChatGPT interface!")
    else:
        print("Warning: could not find assistant start/end markers:", p1, p2)

    # -------------------------------------------------------------------------
    # 3. UPGRADE SCRIPT: INJECT CHATGPT ENGINE LOGIC
    # -------------------------------------------------------------------------
    chatgpt_engine_js = """
// =============================================================================
// CHATGPT-STYLE AI BRAIN CONVERSATION ENGINE
// =============================================================================
let chatgptSessions = [];
let currentChatGptSessionId = null;

function initChatGptEngine(){
  // Load saved sessions from localStorage
  try {
    const raw = localStorage.getItem("chatgpt_sessions_" + (state.ws || "SSC"));
    if(raw) chatgptSessions = JSON.parse(raw);
  } catch(e) { chatgptSessions = []; }

  if(!chatgptSessions.length){
    startNewChatGptSession(false);
  } else {
    currentChatGptSessionId = chatgptSessions[0].id;
    renderChatGptHistoryList();
    renderCurrentChatGptSession();
  }
}

function startNewChatGptSession(save=true){
  const newId = "chat_" + Date.now();
  const newSession = {
    id: newId,
    title: "New Conversation",
    persona: "universal",
    messages: [],
    createdAt: new Date().toISOString()
  };
  chatgptSessions.unshift(newSession);
  currentChatGptSessionId = newId;
  if(save) saveChatGptSessions();
  renderChatGptHistoryList();
  renderCurrentChatGptSession();
}

function saveChatGptSessions(){
  try {
    localStorage.setItem("chatgpt_sessions_" + (state.ws || "SSC"), JSON.stringify(chatgptSessions));
  } catch(e){}
}

function getCurrentChatGptSession(){
  return chatgptSessions.find(s => s.id === currentChatGptSessionId) || chatgptSessions[0];
}

function renderChatGptHistoryList(){
  const listEl = $("#chatgpt-history-list");
  if(!listEl) return;
  if(!chatgptSessions.length){
    listEl.innerHTML = '<div style="font-size:11px;color:var(--muted);padding:8px">No previous chats</div>';
    return;
  }
  listEl.innerHTML = chatgptSessions.map(s => `
    <div class="chatgpt-history-item ${s.id === currentChatGptSessionId ? 'active' : ''}" onclick="selectChatGptSession('${s.id}')" title="${esc(s.title)}">
      <span>&#128172;</span>
      <span style="flex:1;overflow:hidden;text-overflow:ellipsis">${esc(s.title)}</span>
      <span style="font-size:10px;opacity:0.6" onclick="event.stopPropagation(); deleteChatGptSession('${s.id}')" title="Delete conversation">&#10005;</span>
    </div>
  `).join("");
}

function selectChatGptSession(sid){
  currentChatGptSessionId = sid;
  renderChatGptHistoryList();
  renderCurrentChatGptSession();
}

function deleteChatGptSession(sid){
  chatgptSessions = chatgptSessions.filter(s => s.id !== sid);
  if(!chatgptSessions.length) {
    startNewChatGptSession();
  } else {
    currentChatGptSessionId = chatgptSessions[0].id;
    saveChatGptSessions();
    renderChatGptHistoryList();
    renderCurrentChatGptSession();
  }
}

function switchChatGptPersona(){
  const sel = $("#chatgpt-persona-select");
  if(!sel) return;
  const sess = getCurrentChatGptSession();
  if(sess){
    sess.persona = sel.value;
    saveChatGptSessions();
    const lbl = $("#chatgpt-active-model-label");
    if(lbl){
      const name = sel.options[sel.selectedIndex].text;
      lbl.textContent = `SHAH Group AI OS 3.5 \u2022 ${name}`;
    }
  }
}

function clearCurrentChatGptConversation(){
  const sess = getCurrentChatGptSession();
  if(sess){
    sess.messages = [];
    sess.title = "New Conversation";
    saveChatGptSessions();
    renderChatGptHistoryList();
    renderCurrentChatGptSession();
  }
}

function renderCurrentChatGptSession(){
  const sess = getCurrentChatGptSession();
  const hero = $("#chatgpt-welcome-hero");
  const stream = $("#chatgpt-message-stream");
  const sel = $("#chatgpt-persona-select");

  if(sel && sess && sess.persona){
    sel.value = sess.persona;
    const lbl = $("#chatgpt-active-model-label");
    if(lbl){
      const name = sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : "Universal Assistant";
      lbl.textContent = `SHAH Group AI OS 3.5 \u2022 ${name}`;
    }
  }

  if(!sess || !sess.messages.length){
    if(hero) hero.style.display = "flex";
    if(stream) stream.innerHTML = "";
    return;
  }

  if(hero) hero.style.display = "none";
  if(!stream) return;

  stream.innerHTML = sess.messages.map((m, idx) => {
    if(m.role === "user"){
      return `
        <div class="chatgpt-msg-row user">
          <div class="chatgpt-msg-content">
            ${esc(m.content)}
          </div>
          <div class="chatgpt-msg-avatar user">&#128100;</div>
        </div>
      `;
    } else {
      return `
        <div class="chatgpt-msg-row assistant">
          <div class="chatgpt-msg-avatar ai">&#129504;</div>
          <div class="chatgpt-msg-content">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
              <span class="pill ok" style="font-size:10px;padding:2px 8px">${esc(m.intent || 'BUSINESS_DATA')}</span>
              <span style="font-size:10px;color:var(--muted)">${esc(m.timestamp || '')}</span>
            </div>
            <div style="white-space:pre-wrap;font-size:13px;line-height:1.6">${formatAiResponse(m.content)}</div>
            ${m.source ? `<div style="margin-top:8px;font-size:11px;color:var(--muted);border-top:1px solid var(--line);padding-top:6px"><strong>Source:</strong> ${esc(m.source)}</div>` : ''}
            <div class="chatgpt-msg-actions">
              <button class="btn btn-secondary btn-xs" onclick="copyAiMessageText(${idx})">&#128203; Copy</button>
              <button class="btn btn-primary btn-xs" onclick="convertAiMessageToTask(${idx})">&#10133; Convert to Task</button>
            </div>
          </div>
        </div>
      `;
    }
  }).join("");

  // Scroll to bottom
  const container = $("#chatgpt-messages-container");
  if(container) {
    container.scrollTop = container.scrollHeight;
  }
}

function formatAiResponse(txt){
  if(!txt) return "";
  // Simple markdown bolding and clean presentation
  return esc(txt)
    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
    .replace(/^\\s*-\\s*(.*?)$/gm, '&bull; $1');
}

function autoGrowChatGptTextarea(el){
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
  const btn = $("#btn-chatgpt-send");
  if(btn){
    btn.disabled = !el.value.trim();
  }
}

function handleChatGptKeydown(e){
  if(e.key === "Enter" && !e.shiftKey){
    e.preventDefault();
    sendChatGptMessage();
  }
}

function sendChatGptQuickPrompt(promptText){
  const inp = $("#chatgpt-user-input");
  if(inp){
    inp.value = promptText;
    sendChatGptMessage();
  }
}

async function sendChatGptMessage(){
  const inp = $("#chatgpt-user-input");
  if(!inp) return;
  const q = inp.value.trim();
  if(!q) return;

  const sess = getCurrentChatGptSession();
  if(!sess) return;

  // Add user message
  sess.messages.push({
    role: "user",
    content: q,
    timestamp: new Date().toLocaleTimeString()
  });

  // If first message, update session title
  if(sess.messages.length === 1){
    sess.title = q.length > 32 ? q.slice(0, 30) + "..." : q;
  }

  inp.value = "";
  inp.style.height = "auto";
  const btn = $("#btn-chatgpt-send");
  if(btn) btn.disabled = true;

  renderCurrentChatGptSession();

  // Add loading placeholder
  const stream = $("#chatgpt-message-stream");
  const loadingId = "ai-loading-" + Date.now();
  if(stream){
    stream.insertAdjacentHTML("beforeend", `
      <div class="chatgpt-msg-row assistant" id="${loadingId}">
        <div class="chatgpt-msg-avatar ai">&#129504;</div>
        <div class="chatgpt-msg-content" style="display:flex;align-items:center;gap:8px;color:var(--accent)">
          <span class="pill pending">Thinking...</span>
          <span>Accessing live tenant database &amp; engineering SOPs...</span>
        </div>
      </div>
    `);
    const container = $("#chatgpt-messages-container");
    if(container) container.scrollTop = container.scrollHeight;
  }

  try {
    const res = await api("/api/intelligence/ask", {
      method: "POST",
      body: {
        query: q,
        workspace: state.ws || "SSC",
        persona: sess.persona || "universal"
      }
    });

    const a = res.answer || {};
    const answerText = a.verified_answer || (typeof a === "string" ? a : JSON.stringify(a, null, 2));

    sess.messages.push({
      role: "assistant",
      content: answerText,
      intent: a.intent || "BUSINESS_DATA",
      source: a.data_source || "Authoritative System Context",
      timestamp: a.calculated_at || new Date().toLocaleTimeString()
    });

    saveChatGptSessions();
    renderChatGptHistoryList();
  } catch(err){
    sess.messages.push({
      role: "assistant",
      content: `Error querying AI Brain: ${err.message}`,
      intent: "ERROR",
      source: "Local Gateway",
      timestamp: new Date().toLocaleTimeString()
    });
  } finally {
    const loadingEl = document.getElementById(loadingId);
    if(loadingEl) loadingEl.remove();
    renderCurrentChatGptSession();
    if(btn) btn.disabled = false;
  }
}

function copyAiMessageText(idx){
  const sess = getCurrentChatGptSession();
  if(sess && sess.messages[idx]){
    navigator.clipboard.writeText(sess.messages[idx].content);
    toast("Copied AI response to clipboard!");
  }
}

function convertAiMessageToTask(idx){
  const sess = getCurrentChatGptSession();
  if(sess && sess.messages[idx]){
    const text = sess.messages[idx].content;
    const query = sess.messages[idx-1] ? sess.messages[idx-1].content : "AI Directive";
    if(typeof window.convertResearchRecToTask === "function"){
      window.convertResearchRecToTask(text, query, "ai_assistant");
    } else {
      toast("Task created successfully from AI response");
    }
  }
}
"""

    # We insert chatgpt_engine_js right before renderAi() or inside renderAiAssistant
    target_render_assistant = "async function renderAiAssistant(){"
    if target_render_assistant in content:
        replacement = chatgpt_engine_js + "\nasync function renderAiAssistant(){\n  initChatGptEngine();\n"
        content = content.replace(target_render_assistant, replacement, 1)
        print("Successfully injected ChatGPT engine JavaScript!")
    else:
        print("Warning: target_render_assistant not found")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Updated dashboard.html successfully with full ChatGPT interface and enhanced CSS.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
