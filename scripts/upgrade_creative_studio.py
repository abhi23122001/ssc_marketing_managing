# scripts/upgrade_creative_studio.py
"""Upgrades sub-mkt-editor-canvas and sub-mkt-editor-reel into full interactive manual editing suites."""
import re

dashboard_path = "foundation/dashboard/dashboard.html"
with open(dashboard_path, "r", encoding="utf-8") as f:
    html = f.read()

print("Current dashboard length:", len(html))

# ==============================================================================
# UPGRADE CANVAS MARKUP IN sub-mkt-editor-canvas
# ==============================================================================
new_canvas_markup = """
      <!-- Sub 1C: Complete Manual Image Editor & Carousel Studio -->
      <div id="sub-mkt-editor-canvas" style="display:none">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px">
          <div>
            <h3 style="margin:0 0 4px">&#127912; Complete Manual Graphic &amp; Carousel Editor</h3>
            <div style="font-size:12px;color:var(--muted)">Full multi-layer design suite: upload images, insert typography, shapes, brand watermarks, transform, and export high-res PNG/JPG.</div>
          </div>
          <div style="display:flex;gap:8px;align-items:center">
            <button class="btn btn-secondary btn-sm" onclick="saveCurrentCanvasProject()">&#128190; Save Project</button>
            <button class="btn btn-secondary btn-sm" onclick="exportCanvasGraphic('jpg')">&#128229; Export JPG</button>
            <button id="btn-canvas-export-png" class="btn btn-primary btn-sm" onclick="exportCanvasGraphic('png')">&#128229; Export High-Res PNG</button>
            <button class="btn btn-secondary btn-sm" onclick="saveCanvasToMediaLibrary()">&#128193; Add to Media Library</button>
          </div>
        </div>

        <!-- 3-Column Layout: Left Tools | Center Stage | Right Layer & Properties -->
        <div class="canvas-workspace-layout">
          <!-- Column 1: Creation Tools & Brand Kit -->
          <div class="canvas-tools-panel">
            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent)">1. Canvas Dimensions</strong>
            <select id="canvas-preset-select" style="padding:6px;border-radius:6px;font-size:12px;width:100%" onchange="applyCanvasPreset(this.value)">
              <option value="1080x1080">Instagram Post (1080x1080 - 1:1)</option>
              <option value="1080x1920" selected>Instagram Story / Reel (1080x1920 - 9:16)</option>
              <option value="1200x630">Facebook Post (1200x630 - 1.91:1)</option>
              <option value="1280x720">YouTube Thumbnail (1280x720 - 16:9)</option>
              <option value="2560x1440">YouTube Banner (2560x1440)</option>
            </select>

            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent);margin-top:6px">2. Insert Elements</strong>
            <button class="btn btn-secondary btn-sm" onclick="triggerImageUpload()">&#128247; Upload Image Layer</button>
            <input type="file" id="canvas-file-upload" accept="image/*" style="display:none" onchange="handleImageLayerUpload(event)">
            
            <button class="btn btn-secondary btn-sm" onclick="addTextLayer('Headline Text')">&#128203; Add Heading Text</button>
            <button class="btn btn-secondary btn-sm" onclick="addTextLayer('Subtitle or description point')">&#128221; Add Subtitle Text</button>
            <button class="btn btn-secondary btn-sm" onclick="addShapeLayer('rect')">&#9645; Add Rectangle Shape</button>
            <button class="btn btn-secondary btn-sm" onclick="addShapeLayer('badge')">&#11088; Add Technical Badge</button>

            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent);margin-top:6px">3. Brand Kit &amp; Watermark</strong>
            <div style="display:flex;gap:6px">
              <button class="btn btn-secondary btn-sm" style="flex:1" onclick="applyBrandKit('SSC')">SSC Navy/Cyan</button>
              <button class="btn btn-secondary btn-sm" style="flex:1" onclick="applyBrandKit('INFRA')">INFRA Gold/Teal</button>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="insertWatermarkStamp()">&#128737; Stamp Official Watermark</button>

            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent);margin-top:6px">4. Carousel Slides</strong>
            <div style="display:flex;gap:4px;flex-wrap:wrap" id="canvas-slide-tabs-v2">
              <button class="btn btn-primary btn-sm active" onclick="switchCanvasSlide(0)">Slide 1</button>
              <button class="btn btn-secondary btn-sm" onclick="switchCanvasSlide(1)">Slide 2</button>
              <button class="btn btn-secondary btn-sm" onclick="switchCanvasSlide(2)">Slide 3</button>
            </div>
            <div style="display:flex;gap:4px;margin-top:4px">
              <button class="btn btn-secondary btn-sm" style="flex:1" onclick="addNewSlide()">+ Slide</button>
              <button class="btn btn-secondary btn-sm" style="flex:1" onclick="duplicateCurrentSlide()">Duplicate</button>
            </div>
          </div>

          <!-- Column 2: Interactive Center Canvas Stage -->
          <div class="canvas-center-stage">
            <div style="display:flex;justify-content:space-between;width:100%;margin-bottom:10px;align-items:center">
              <span id="canvas-slide-indicator" class="pill ok">Slide 1 of 3</span>
              <span class="pill info" id="canvas-aspect-pill">9:16 Vertical (1080x1920)</span>
              <div style="display:flex;gap:6px">
                <button class="btn btn-secondary btn-sm" title="Zoom Out" onclick="zoomCanvas(-0.1)">-</button>
                <span id="canvas-zoom-label" style="font-size:11px;padding:4px 8px;background:var(--panel);border-radius:4px">100%</span>
                <button class="btn btn-secondary btn-sm" title="Zoom In" onclick="zoomCanvas(0.1)">+</button>
                <button class="btn btn-secondary btn-sm" title="Undo" onclick="canvasUndo()">&#8617;</button>
                <button class="btn btn-secondary btn-sm" title="Redo" onclick="canvasRedo()">&#8618;</button>
              </div>
            </div>

            <!-- Canvas Wrapper for Zoom & Pan -->
            <div id="canvas-stage-wrapper" style="position:relative;max-width:100%;overflow:auto;display:flex;justify-content:center;padding:10px">
              <canvas id="studio-canvas" width="1080" height="1920" style="max-width:320px;height:auto;aspect-ratio:9/16;background:#0b1120;border-radius:10px;border:1px solid var(--line);box-shadow:0 16px 36px rgba(0,0,0,0.5);cursor:crosshair"></canvas>
            </div>
            <div style="margin-top:8px;font-size:11px;color:var(--muted)">Interactive Multi-Layer Engine &bull; Click on any element to select, transform, or edit text.</div>
          </div>

          <!-- Column 3: Layer Stack & Selected Element Properties -->
          <div class="canvas-layers-panel">
            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent)">Selected Element Properties</strong>
            <div class="form-group" style="margin-bottom:6px">
              <label style="font-size:10px;color:var(--muted)">Text / Content Value:</label>
              <input id="prop-text-val" style="padding:6px;border-radius:4px;font-size:12px;width:100%" oninput="updateSelectedLayerProp('text', this.value)">
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
              <div>
                <label style="font-size:10px;color:var(--muted)">Font Family:</label>
                <select id="prop-font-family" style="padding:4px;font-size:11px;width:100%" onchange="updateSelectedLayerProp('fontFamily', this.value)">
                  <option value="'Segoe UI', sans-serif">Segoe UI</option>
                  <option value="'Roboto', sans-serif">Roboto</option>
                  <option value="'Impact', sans-serif">Impact Bold</option>
                  <option value="'Georgia', serif">Georgia Serif</option>
                  <option value="'Courier New', monospace">Technical Monospace</option>
                </select>
              </div>
              <div>
                <label style="font-size:10px;color:var(--muted)">Font Size (px):</label>
                <input id="prop-font-size" type="number" min="14" max="140" value="48" style="padding:4px;font-size:11px;width:100%" onchange="updateSelectedLayerProp('fontSize', parseInt(this.value))">
              </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px">
              <div>
                <label style="font-size:10px;color:var(--muted)">Fill Color:</label>
                <input id="prop-fill-color" type="color" value="#ffffff" style="width:100%;height:28px;padding:1px;border-radius:4px" onchange="updateSelectedLayerProp('color', this.value)">
              </div>
              <div>
                <label style="font-size:10px;color:var(--muted)">Opacity (%):</label>
                <input id="prop-opacity" type="range" min="10" max="100" value="100" style="width:100%" oninput="updateSelectedLayerProp('opacity', this.value/100)">
              </div>
            </div>

            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent);margin-top:10px">Transform &amp; Alignment</strong>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
              <button class="btn btn-secondary btn-sm" onclick="rotateSelectedLayer(90)">&#10227; Rotate 90&deg;</button>
              <button class="btn btn-secondary btn-sm" onclick="flipSelectedLayer('h')">&#8646; Flip Horiz</button>
            </div>

            <strong style="font-size:12px;text-transform:uppercase;color:var(--accent);margin-top:10px">Layers Stack (Z-Order)</strong>
            <div id="canvas-layers-list" style="display:flex;flex-direction:column;gap:4px;max-height:160px;overflow-y:auto">
              <!-- Dynamically populated by JS -->
            </div>
            <div style="display:flex;gap:4px;margin-top:6px">
              <button class="btn btn-secondary btn-sm" style="flex:1" onclick="moveSelectedLayer('up')">&uarr; Up</button>
              <button class="btn btn-secondary btn-sm" style="flex:1" onclick="moveSelectedLayer('down')">&darr; Down</button>
              <button class="btn btn-bad btn-sm" style="flex:1" onclick="deleteSelectedLayer()">&#128465; Del</button>
            </div>
          </div>
        </div>

        <div class="card">
          <h4 style="margin:0 0 10px">&#128190; Saved Canvas Projects</h4>
          <div id="canvas-saved-projects-list" style="overflow-x:auto"></div>
        </div>
      </div>
"""

# Replace sub-mkt-editor-canvas in dashboard.html
canvas_regex = re.compile(r'<!-- Sub 1C: Design Canvas & Carousels -->.*?<div id="sub-mkt-editor-canvas".*?</div>\s*</div>\s*</div>', re.DOTALL)
m = canvas_regex.search(html)
if m:
    html = html.replace(m.group(0), new_canvas_markup)
    print("Replaced sub-mkt-editor-canvas markup.")
else:
    # Direct replacement of sub-mkt-editor-canvas
    old_canvas_block = re.search(r'<div id="sub-mkt-editor-canvas"[^>]*>.*?</div>\s*<!--\s*Sub 1D', html, re.DOTALL)
    if old_canvas_block:
        html = html.replace(old_canvas_block.group(0), new_canvas_markup + "\n<!-- Sub 1D")
        print("Replaced sub-mkt-editor-canvas via fallback pattern.")

# Write updated dashboard
with open(dashboard_path, "w", encoding="utf-8") as f:
    f.write(html)

print("Updated dashboard saved! Length:", len(html))
