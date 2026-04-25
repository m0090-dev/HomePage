import os
import json
from PIL import Image

BASE = "files/images"
THUMB = "files/thumbs"
OUT_INDEX = "index.html"
OUT_DIR = "pages"

IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}

os.makedirs(THUMB, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


# ----------------------------
# サムネ生成
# ----------------------------
def make_thumb(src, dst, size=400):
    img = Image.open(src)
    img.thumbnail((size, size))
    img.save(dst)


# ----------------------------
# 画像スキャン
# ----------------------------
def scan():
    data = []

    if not os.path.exists(BASE):
        print("files/images not found")
        return data

    for f in os.listdir(BASE):
        ext = f.split(".")[-1].lower()
        if ext not in IMAGE_EXT:
            continue

        src = f"{BASE}/{f}"
        thumb = f"{THUMB}/{f}"

        if not os.path.exists(thumb):
            make_thumb(src, thumb)

        data.append({
            "name": f,
            "src": src,
            "thumb": thumb
        })

    return data


# ----------------------------
# 詳細ビューア生成
# ----------------------------
def make_detail_page(item):
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{item['name']}</title>

<style>
body {{
  margin:0;
  background:#111;
  overflow:hidden;
  font-family:sans-serif;
  color:#fff;
}}

#wrap {{
  width:100vw;
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  cursor:grab;
}}

#img {{
  max-width:none;
  transform-origin:center;
}}

.toolbar {{
  position:fixed;
  top:10px;
  left:10px;
  z-index:9999;
  background:rgba(30,30,30,0.95);
  padding:10px;
  border-radius:8px;
  display:flex;
  flex-direction:column;
  gap:6px;
  width:220px;
  box-sizing:border-box;
}}

.toolbar.hidden {{
  display:none;
}}

button {{
  background:#333;
  color:#fff;
  border:none;
  padding:6px;
  cursor:pointer;
  font-size:12px;
}}

button:hover {{
  background:#555;
}}

.toggle {{
  position:fixed;
  top:10px;
  right:10px;
  z-index:10000;
  background:#333;
  padding:8px;
  cursor:pointer;
  color:#fff;
  border-radius:6px;
  font-size:12px;
}}

.info {{
  font-size:12px;
  line-height:1.4;
  opacity:0.9;
  margin-bottom:6px;
}}

@media (max-width:768px) {{

  .toolbar {{
    width:85vw;
    left:7.5vw;
    padding:14px;
  }}

  button {{
    padding:12px;
    font-size:14px;
  }}

  .info {{
    font-size:14px;
  }}

  .toggle {{
    padding:12px;
    font-size:14px;
  }}
}}
</style>
</head>

<body>

<div class="toggle" onclick="toggleUI()">UI</div>

<div class="toolbar" id="ui">
  <div class="info" id="info">
    file: {item['name']}<br>
    size: loading...
  </div>

  <button onclick="zoom(1.1)">＋ zoom</button>
  <button onclick="zoom(0.9)">－ zoom</button>
  <button onclick="rotate(90)">rotate</button>
  <button onclick="flipX()">flip X</button>
  <button onclick="flipY()">flip Y</button>
  <button onclick="reset()">reset</button>
  <button onclick="toggleFull()">fullscreen</button>
</div>

<div id="wrap">
  <img id="img" src="../{item['src']}">
</div>

<script>
let scale = 1;
let rot = 0;
let fx = 1;
let fy = 1;

let pos = {{x:0,y:0}};
let dragging = false;
let last = {{x:0,y:0}};

const img = document.getElementById("img");
const wrap = document.getElementById("wrap");
const ui = document.getElementById("ui");
const info = document.getElementById("info");

img.onload = () => {{
  info.innerHTML =
    "file: {item['name']}<br>" +
    "size: " + img.naturalWidth + " x " + img.naturalHeight;
}};

function update() {{
  img.style.transform =
    `translate(${{pos.x}}px, ${{pos.y}}px)
     scale(${{scale}})
     rotate(${{rot}}deg)
     scaleX(${{fx}})
     scaleY(${{fy}})`;
}}

function zoom(v) {{
  scale *= v;
  update();
}}

function rotate(v) {{
  rot += v;
  update();
}}

function flipX() {{
  fx *= -1;
  update();
}}

function flipY() {{
  fy *= -1;
  update();
}}

function reset() {{
  scale = 1;
  rot = 0;
  fx = 1;
  fy = 1;
  pos = {{x:0,y:0}};
  update();
}}

function toggleUI() {{
  ui.classList.toggle("hidden");
}}

function toggleFull() {{
  if (!document.fullscreenElement) {{
    document.documentElement.requestFullscreen();
  }} else {{
    document.exitFullscreen();
  }}
}}

wrap.addEventListener("mousedown", e => {{
  dragging = true;
  wrap.style.cursor = "grabbing";
  last = {{x:e.clientX,y:e.clientY}};
}});

window.addEventListener("mouseup", () => {{
  dragging = false;
  wrap.style.cursor = "grab";
}});

window.addEventListener("mousemove", e => {{
  if (!dragging) return;
  pos.x += e.clientX - last.x;
  pos.y += e.clientY - last.y;
  last = {{x:e.clientX,y:e.clientY}};
  update();
}});

window.addEventListener("wheel", e => {{
  scale *= (e.deltaY < 0 ? 1.1 : 0.9);
  update();
}});

const files = {json.dumps(sorted(os.listdir(BASE)))};

let current = files.indexOf("{item['name']}");

window.addEventListener("keydown", e => {{
  if (e.key === "ArrowLeft") navigate(-1);
  if (e.key === "ArrowRight") navigate(1);
  if (e.key === "f") toggleFull();
}});

function navigate(dir) {{
  current += dir;
  if (current < 0) current = files.length - 1;
  if (current >= files.length) current = 0;
  window.location = "../pages/" + files[current] + ".html";
}}

/* touch */
let touches = [];

window.addEventListener("touchstart", e => {{
  touches = e.touches;
}});

window.addEventListener("touchmove", e => {{
  if (e.touches.length == 1) {{
    let t = e.touches[0];
    pos.x += (t.clientX - (touches[0]?.clientX || 0)) * 1.2;
    pos.y += (t.clientY - (touches[0]?.clientY || 0)) * 1.2;
    update();
  }}

  if (e.touches.length == 2) {{
    let dx = e.touches[0].clientX - e.touches[1].clientX;
    let dy = e.touches[0].clientY - e.touches[1].clientY;
    let dist = Math.sqrt(dx*dx + dy*dy);

    let odx = touches[0].clientX - touches[1].clientX;
    let ody = touches[0].clientY - touches[1].clientY;
    let odist = Math.sqrt(odx*odx + ody*ody);

    scale *= dist / odist;
    update();
  }}

  touches = e.touches;
}});

let lastTap = 0;
window.addEventListener("touchend", () => {{
  const now = Date.now();
  if (now - lastTap < 300) {{
    scale *= 1.2;
    update();
  }}
  lastTap = now;
}});

update();
</script>

</body>
</html>
"""

    path = f"{OUT_DIR}/{item['name']}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


# ----------------------------
# index生成（モバイル対応済み）
# ----------------------------
def build_index(data):
    js = json.dumps(data, ensure_ascii=False)

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Viewer</title>

<style>
body {{
  margin:0;
  font-family:sans-serif;
  background:#1a1a1a;
  color:#eee;
}}

.topbar {{
  padding:10px;
  background:#222;
  position:sticky;
  top:0;
}}

input {{
  width:300px;
  padding:8px;
}}

.grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
  gap:10px;
  padding:10px;
}}

.card {{
  background:#222;
  cursor:pointer;
}}

.card img {{
  width:100%;
}}

@media (max-width:768px) {{
  input {{
    width:95%;
    font-size:16px;
    padding:12px;
  }}

  .grid {{
    grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
    gap:12px;
  }}
}}
</style>
</head>

<body>

<div class="topbar">
  <input id="search" placeholder="search filename...">
</div>

<div class="grid" id="grid"></div>

<script>
const data = {js};

const grid = document.getElementById("grid");
const search = document.getElementById("search");

function render(list) {{
  grid.innerHTML = "";

  list.forEach(item => {{
    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
      <img src="${{item.thumb}}">
      <div>${{item.name}}</div>
    `;

    div.onclick = () => {{
      window.location = "pages/" + item.name + ".html";
    }};

    grid.appendChild(div);
  }});
}}

search.addEventListener("input", () => {{
  const q = search.value.toLowerCase();
  render(data.filter(d => d.name.toLowerCase().includes(q)));
}});

render(data);
</script>

</body>
</html>
"""

    with open(OUT_INDEX, "w", encoding="utf-8") as f:
        f.write(html)


# ----------------------------
# main
# ----------------------------
def main():
    data = scan()

    for item in data:
        make_detail_page(item)

    build_index(data)

    print(f"build complete ({len(data)} images)")


if __name__ == "__main__":
    main()
