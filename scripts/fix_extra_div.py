with open('foundation/dashboard/dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        <div class="card">
          <h4 style="margin:0 0 10px">&#128190; Saved Canvas Projects</h4>
          <div id="canvas-saved-projects-list" style="overflow-x:auto"></div>
        </div>
      </div>


        <div class="card">
          <h4 style="margin:0 0 10px">Exported Slide PNG Gallery</h4>
          <div id="canvas-exports-gallery" class="grid3"></div>
        </div>
      </div>"""

replacement = """        <div class="card" style="margin-top:14px">
          <h4 style="margin:0 0 10px">&#128190; Saved Canvas Projects</h4>
          <div id="canvas-saved-projects-list" style="overflow-x:auto"></div>
        </div>

        <div class="card" style="margin-top:14px">
          <h4 style="margin:0 0 10px">Exported Slide PNG Gallery</h4>
          <div id="canvas-exports-gallery" class="grid3"></div>
        </div>
      </div>"""

if target in text:
    text = text.replace(target, replacement)
    with open('foundation/dashboard/dashboard.html', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Fixed extra div successfully!")
else:
    print("Target not found!")
