import os
import json
from PIL import Image

BASE = "files"
THUMB = "files/thumbs"
OUT_INDEX = "index.html"
OUT_DIR = "pages"

IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif"}
TEXT_EXT = {"txt", "md", "py", "js", "html", "css", "json", "xml", "csv"}

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
# 画像サイズ取得
# ----------------------------
def get_image_size(src):
    try:
        with Image.open(src) as img:
            return img.size  # (width, height)
    except:
        return (0, 0)


# ----------------------------
# ファイルサイズ整形
# ----------------------------
def format_size(path):
    try:
        b = os.path.getsize(path)
        if b < 1024:
            return f"{b} B"
        elif b < 1024 * 1024:
            return f"{b/1024:.1f} KB"
        else:
            return f"{b/1024/1024:.1f} MB"
    except:
        return "?"


# ----------------------------
# 種別判定
# ----------------------------
def get_type(file):
    ext = file.rsplit(".", 1)[-1].lower() if "." in file else ""
    if ext in IMAGE_EXT:
        return "image"
    return "text"


# ----------------------------
# スキャン
# ----------------------------
def scan():
    data = []

    if not os.path.exists(BASE):
        print("files/ not found")
        return data

    for f in sorted(os.listdir(BASE)):
        if f == "thumbs":
            continue
        src = f"{BASE}/{f}"
        if not os.path.isfile(src):
            continue
        kind = get_type(f)
        fsize = format_size(src)

        if kind == "image":
            thumb = f"{THUMB}/{f}"
            if not os.path.exists(thumb):
                try:
                    make_thumb(src, thumb)
                except:
                    thumb = src
            w, h = get_image_size(src)
            data.append({
                "name": f,
                "type": "image",
                "src": src,
                "thumb": thumb,
                "size": fsize,
                "width": w,
                "height": h
            })
        else:
            data.append({
                "name": f,
                "type": "text",
                "src": src,
                "size": fsize
            })

    return data


# ----------------------------
# 詳細ページ
# ----------------------------
def make_detail_page(item):
    is_image = item["type"] == "image"
    fsize = item.get("size", "?")

    if is_image:
        w = item.get("width", 0)
        h = item.get("height", 0)
        meta_line = f"{item['name']} &nbsp;·&nbsp; {fsize} &nbsp;·&nbsp; {w}×{h}px"
    else:
        meta_line = f"{item['name']} &nbsp;·&nbsp; {fsize}"

    if is_image:
        viewer_html = f"""
<div id="wrap">
  <img id="img" src="../{item['src']}" draggable="false">
</div>
"""
        viewer_js = f"""
let scale = 1, rot = 0;
let isDrag = false, startX, startY, ox = 0, oy = 0, dx = 0, dy = 0;
const img = document.getElementById("img");
const wrap = document.getElementById("wrap");

function applyTransform() {{
  img.style.transform = `translate(${{ox+dx}}px, ${{oy+dy}}px) scale(${{scale}}) rotate(${{rot}}deg)`;
}}

function zoom(v) {{ scale = Math.max(0.1, scale * v); applyTransform(); }}
function rotate(v) {{ rot += v; applyTransform(); }}
function reset() {{ scale = 1; rot = 0; ox = 0; oy = 0; dx = 0; dy = 0; applyTransform(); }}

// ドラッグ（マウス）
wrap.addEventListener("mousedown", e => {{
  isDrag = true; startX = e.clientX; startY = e.clientY;
  wrap.style.cursor = "grabbing";
}});
window.addEventListener("mousemove", e => {{
  if (!isDrag) return;
  dx = e.clientX - startX; dy = e.clientY - startY;
  applyTransform();
}});
window.addEventListener("mouseup", () => {{
  if (!isDrag) return;
  isDrag = false; ox += dx; oy += dy; dx = 0; dy = 0;
  wrap.style.cursor = "grab";
}});

// ドラッグ（タッチ）
let lastTouchDist = null;
wrap.addEventListener("touchstart", e => {{
  if (e.touches.length === 1) {{
    isDrag = true;
    startX = e.touches[0].clientX; startY = e.touches[0].clientY;
  }} else if (e.touches.length === 2) {{
    isDrag = false;
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    lastTouchDist = Math.sqrt(dx*dx + dy*dy);
  }}
  e.preventDefault();
}}, {{passive: false}});
wrap.addEventListener("touchmove", e => {{
  if (e.touches.length === 1 && isDrag) {{
    dx = e.touches[0].clientX - startX; dy = e.touches[0].clientY - startY;
    applyTransform();
  }} else if (e.touches.length === 2 && lastTouchDist) {{
    const ddx = e.touches[0].clientX - e.touches[1].clientX;
    const ddy = e.touches[0].clientY - e.touches[1].clientY;
    const dist = Math.sqrt(ddx*ddx + ddy*ddy);
    scale = Math.max(0.1, scale * (dist / lastTouchDist));
    lastTouchDist = dist;
    applyTransform();
  }}
  e.preventDefault();
}}, {{passive: false}});
wrap.addEventListener("touchend", e => {{
  if (e.touches.length === 0) {{
    ox += dx; oy += dy; dx = 0; dy = 0;
    isDrag = false; lastTouchDist = null;
  }}
}});

// ホイールズーム
wrap.addEventListener("wheel", e => {{
  e.preventDefault();
  zoom(e.deltaY < 0 ? 1.1 : 0.9);
}}, {{passive: false}});

applyTransform();
"""
        toolbar_html = f"""
<div class="toolbar" id="toolbar">
  <div class="meta">{meta_line}</div>
  <div class="btns">
    <button onclick="zoom(1.15)" title="拡大">＋</button>
    <button onclick="zoom(1/1.15)" title="縮小">－</button>
    <button onclick="rotate(90)" title="回転">↻</button>
    <button onclick="reset()" title="リセット">⊡</button>
    <a class="btn-a" href="../{item['src']}" download="{item['name']}" title="ダウンロード">↓</a>
    <a class="btn-a" href="../index.html" title="一覧へ">☰</a>
  </div>
</div>
<button class="toggle-ui" id="toggleBtn" onclick="toggleUI()" title="UI表示切替">✕</button>
"""
    else:
        viewer_html = f"""
<div id="text-wrap">
  <pre id="text"></pre>
</div>
"""
        viewer_js = f"""
fetch("../{item['src']}")
  .then(r => r.text())
  .then(t => {{
    document.getElementById("text").textContent = t;
  }});

function copyText() {{
  const t = document.getElementById("text").textContent;
  navigator.clipboard.writeText(t).then(() => {{
    const btn = document.getElementById("copyBtn");
    btn.textContent = "✓ Copied";
    setTimeout(() => btn.textContent = "Copy", 1500);
  }});
}}
"""
        toolbar_html = f"""
<div class="toolbar" id="toolbar">
  <div class="meta">{meta_line}</div>
  <div class="btns">
    <button id="copyBtn" onclick="copyText()">Copy</button>
    <a class="btn-a" href="../{item['src']}" download="{item['name']}" title="ダウンロード">↓</a>
    <a class="btn-a" href="../index.html" title="一覧へ">☰</a>
  </div>
</div>
<button class="toggle-ui" id="toggleBtn" onclick="toggleUI()" title="UI表示切替">✕</button>
"""

    toggle_js = """
function toggleUI() {
  const hidden = document.body.classList.toggle("ui-hidden");
  document.getElementById("toggleBtn").textContent = hidden ? "☰" : "✕";
}
"""

    image_specific_css = """
  #wrap {
    width: 100vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    cursor: grab;
    user-select: none;
  }
  #img {
    max-width: none;
    max-height: none;
    display: block;
    transform-origin: center;
    pointer-events: none;
  }
""" if is_image else """
  #text-wrap {
    padding: 70px 24px 40px;
    max-width: 860px;
    margin: 0 auto;
  }
  pre {
    white-space: pre-wrap;
    word-break: break-word;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
    font-size: 13.5px;
    line-height: 1.75;
    color: #d4d4d4;
  }
"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<meta name="google" content="notranslate">
<title>{item['name']}</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: #111;
  color: #eee;
  font-family: 'Segoe UI', system-ui, sans-serif;
  overflow: {"hidden" if is_image else "auto"};
}}

/* ── ツールバー ── */
.toolbar {{
  position: fixed;
  top: 14px;
  left: 14px;
  z-index: 1000;
  background: rgba(20,20,20,0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 220px;
  max-width: 300px;
  transition: opacity 0.2s, transform 0.2s;
  box-shadow: 0 4px 24px rgba(0,0,0,0.5);
}}

.meta {{
  font-size: 11px;
  color: #aaa;
  word-break: break-all;
  line-height: 1.5;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  padding-bottom: 8px;
}}

.btns {{
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}}

.btns button,
.btns .btn-a {{
  background: rgba(255,255,255,0.07);
  color: #ddd;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 6px;
  padding: 6px 11px;
  font-size: 13px;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
}}

.btns button:hover,
.btns .btn-a:hover {{
  background: rgba(255,255,255,0.16);
  color: #fff;
}}

/* ── UI非表示トグル ── */
.toggle-ui {{
  position: fixed;
  top: 14px;
  right: 14px;
  z-index: 1001;
  width: 34px;
  height: 34px;
  background: rgba(20,20,20,0.75);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: #aaa;
  font-size: 15px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, opacity 0.2s;
}}
.toggle-ui:hover {{ background: rgba(60,60,60,0.9); color: #fff; }}

/* UI非表示状態 */
body.ui-hidden .toolbar {{
  opacity: 0;
  pointer-events: none;
  transform: translateY(-6px);
}}
body.ui-hidden .toggle-ui {{
  opacity: 0.25;
  background: transparent;
  border-color: transparent;
}}
body.ui-hidden .toggle-ui:hover {{
  opacity: 0.8;
}}

{image_specific_css}
</style>
</head>
<body>

{toolbar_html}
{viewer_html}

<script>
{viewer_js}
{toggle_js}
</script>
</body>
</html>
"""

    path = f"{OUT_DIR}/{item['name']}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


# ----------------------------
# index
# ----------------------------
def build_index(data):
    js = json.dumps(data, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Viewer</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; }}

body {{
  margin: 0;
  background: #111;
  color: #eee;
  font-family: 'Segoe UI', system-ui, sans-serif;
  min-height: 100vh;
}}

header {{
  padding: 18px 16px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  position: sticky;
  top: 0;
  background: rgba(17,17,17,0.95);
  backdrop-filter: blur(12px);
  z-index: 10;
}}

header span {{
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}}

#search {{
  flex: 1;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 7px;
  color: #eee;
  padding: 7px 12px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}}
#search:focus {{ border-color: rgba(255,255,255,0.28); }}
#search::placeholder {{ color: #555; }}

.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
  padding: 14px;
}}

.card {{
  background: #1c1c1c;
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.15s, transform 0.12s, background 0.15s;
}}
.card:hover {{
  border-color: rgba(255,255,255,0.2);
  background: #222;
  transform: translateY(-2px);
}}
.card:active {{
  transform: translateY(0);
}}

.card-thumb {{
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: #161616;
  display: flex;
  align-items: center;
  justify-content: center;
}}
.card-thumb img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}}
.card-thumb .icon {{
  font-size: 32px;
  opacity: 0.3;
}}

.card-info {{
  padding: 7px 9px 9px;
}}
.card-name {{
  font-size: 11.5px;
  color: #ccc;
  word-break: break-all;
  line-height: 1.4;
  margin-bottom: 3px;
}}
.card-meta {{
  font-size: 10px;
  color: #555;
  line-height: 1.4;
}}

.empty {{
  grid-column: 1/-1;
  text-align: center;
  color: #444;
  padding: 60px 0;
  font-size: 14px;
}}
</style>
</head>
<body>

<header>
  <input id="search" type="search" placeholder="ファイル名で絞り込み…" autocomplete="off">
  <span id="count"></span>
</header>

<div class="grid" id="grid"></div>

<script>
const data = {js};
const grid = document.getElementById("grid");
const countEl = document.getElementById("count");

function render(list) {{
  grid.innerHTML = "";
  countEl.textContent = list.length + " files";

  if (list.length === 0) {{
    grid.innerHTML = '<div class="empty">一致するファイルがありません</div>';
    return;
  }}

  list.forEach(item => {{
    const card = document.createElement("div");
    card.className = "card";

    let thumbHtml;
    if (item.type === "image") {{
      thumbHtml = `<div class="card-thumb"><img src="${{item.thumb}}" loading="lazy" alt="${{item.name}}"></div>`;
    }} else {{
      const ext = item.name.includes(".") ? item.name.split(".").pop().toUpperCase() : "FILE";
      thumbHtml = `<div class="card-thumb"><span class="icon">${{ext}}</span></div>`;
    }}

    let metaHtml = item.size || "";
    if (item.type === "image" && item.width) {{
      metaHtml += ` · ${{item.width}}×${{item.height}}px`;
    }}

    card.innerHTML = `
      ${{thumbHtml}}
      <div class="card-info">
        <div class="card-name">${{item.name}}</div>
        <div class="card-meta">${{metaHtml}}</div>
      </div>
    `;

    card.addEventListener("click", () => {{
      location.href = "pages/" + encodeURIComponent(item.name) + ".html";
    }});

    grid.appendChild(card);
  }});
}}

document.getElementById("search").addEventListener("input", e => {{
  const q = e.target.value.toLowerCase();
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
    print(f"done — {len(data)} files")


if __name__ == "__main__":
    main()
