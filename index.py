import os
import json
from PIL import Image

BASE = "files/images"
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
# 種別判定
# ----------------------------
def get_type(file):
    ext = file.split(".")[-1].lower()

    if ext in IMAGE_EXT:
        return "image"
    if ext in TEXT_EXT:
        return "text"
    return "text"


# ----------------------------
# スキャン
# ----------------------------
def scan():
    data = []

    if not os.path.exists(BASE):
        print("files/images not found")
        return data

    for f in os.listdir(BASE):
        src = f"{BASE}/{f}"
        kind = get_type(f)

        if kind == "image":
            thumb = f"{THUMB}/{f}"

            if not os.path.exists(thumb):
                try:
                    make_thumb(src, thumb)
                except:
                    thumb = src

            data.append({
                "name": f,
                "type": "image",
                "src": src,
                "thumb": thumb
            })
        else:
            data.append({
                "name": f,
                "type": "text",
                "src": src
            })

    return data


# ----------------------------
# 詳細ページ
# ----------------------------
def make_detail_page(item):

    is_image = item["type"] == "image"

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>{item['name']}</title>

<style>
body {{
  margin:0;
  background:#111;
  font-family:sans-serif;
  color:#fff;
}}

.toolbar {{
  position:fixed;
  top:10px;
  left:10px;
  z-index:9999;
  background:rgba(30,30,30,0.95);
  padding:10px;
  border-radius:8px;
  width:240px;
}}

button {{
  background:#333;
  color:#fff;
  border:none;
  padding:8px;
  margin:2px 0;
  width:100%;
  cursor:pointer;
}}

.info {{
  font-size:12px;
  margin-bottom:8px;
  word-break:break-all;
}}

#wrap {{
  width:100vw;
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  overflow:hidden;
}}

#img {{
  max-width:none;
  transform-origin:center;
}}

pre {{
  white-space:pre-wrap;
  word-break:break-word;
  padding:20px;
}}

.copyBtn {{
  position:fixed;
  bottom:10px;
  right:10px;
  background:#444;
  padding:10px;
  cursor:pointer;
}}
</style>
</head>

<body>
"""

    if is_image:
        html += f"""
<div class="toolbar">
  <div class="info">{item['name']}</div>
  <button onclick="zoom(1.1)">＋</button>
  <button onclick="zoom(0.9)">－</button>
  <button onclick="rotate(90)">rotate</button>
  <button onclick="reset()">reset</button>
</div>

<div id="wrap">
  <img id="img" src="../{item['src']}">
</div>

<script>
let scale=1, rot=0;
const img=document.getElementById("img");

function update(){{
  img.style.transform=`scale(${{scale}}) rotate(${{rot}}deg)`;
}}

function zoom(v){{scale*=v;update();}}
function rotate(v){{rot+=v;update();}}
function reset(){{scale=1;rot=0;update();}}

update();
</script>
"""
    else:
        html += f"""
<div class="toolbar">
  <div class="info">{item['name']}</div>
</div>

<pre id="text"></pre>
<div class="copyBtn" onclick="copyText()">COPY</div>

<script>
fetch("../{item['src']}")
.then(r=>r.text())
.then(t=>document.getElementById("text").textContent=t);

function copyText(){{
  navigator.clipboard.writeText(
    document.getElementById("text").textContent
  );
}}
</script>
"""

    html += """
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

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Viewer</title>

<style>
body {{
  margin:0;
  font-family:sans-serif;
  background:#1a1a1a;
  color:#fff;
}}

.grid {{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
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
</style>
</head>

<body>

<input id="search" placeholder="search">

<div class="grid" id="grid"></div>

<script>
const data = {js};

const grid = document.getElementById("grid");
const search = document.getElementById("search");

function render(list){{
  grid.innerHTML="";

  list.forEach(i=>{{
    const div=document.createElement("div");
    div.className="card";

    div.innerHTML =
      i.type==="image"
      ? `<img src="${{i.thumb}}"><div>${{i.name}}</div>`
      : `<div style="padding:10px">${{i.name}}</div>`;

    div.onclick=()=>location="pages/"+i.name+".html";
    grid.appendChild(div);
  }});
}}

search.addEventListener("input", ()=>{{
  const q=search.value.toLowerCase();
  render(data.filter(d=>d.name.toLowerCase().includes(q)));
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
    print("done", len(data))


if __name__ == "__main__":
    main()
