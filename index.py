import os
import json
from PIL import Image

BASE = "files/images"
THUMB = "files/thumbs"
OUT_INDEX = "index.html"
OUT_DIR = "pages"

IMAGE_EXT = {"png","jpg","jpeg","webp","gif"}

os.makedirs(THUMB, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)


def make_thumb(src, dst, size=400):
    img = Image.open(src)
    img.thumbnail((size, size))
    img.save(dst)


def scan():
    data = []

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
  display:flex;
  justify-content:center;
  align-items:center;
  height:100vh;
}}
img {{
  max-width:90%;
  max-height:90%;
}}
</style>
</head>
<body>
<img src="../{item['src']}">
</body>
</html>
"""

    path = f"{OUT_DIR}/{item['name']}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


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

  render(data.filter(d =>
    d.name.toLowerCase().includes(q)
  ));
}});

render(data);
</script>

</body>
</html>
"""

    with open(OUT_INDEX, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    data = scan()

    for item in data:
        make_detail_page(item)

    build_index(data)

    print("build complete")


if __name__ == "__main__":
    main()
