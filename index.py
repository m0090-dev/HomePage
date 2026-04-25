import os
import json

FILES_DIR = "files"
OUTPUT = "index.html"

def scan_files():
    files = []

    for name in os.listdir(FILES_DIR):
        path = os.path.join(FILES_DIR, name)

        if os.path.isfile(path):
            files.append({
                "name": name,
                "path": f"{FILES_DIR}/{name}"
            })

    return files


def generate_html(files_json):
    files_str = json.dumps(files_json, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>File Viewer</title>

<style>
body {{
  margin: 0;
  font-family: Arial;
  background: #ddd;
}}

.container {{
  display: flex;
  height: 100vh;
}}

.file-list {{
  width: 250px;
  overflow-y: auto;
  background: rgba(255,255,255,0.3);
  padding: 10px;
}}

.file-item {{
  padding: 10px;
  cursor: pointer;
  border-bottom: 1px solid #ccc;
}}

.viewer {{
  flex: 1;
  padding: 20px;
  overflow: auto;
}}

img {{
  max-width: 100%;
}}
</style>
</head>

<body>

<div class="container">
  <div id="list" class="file-list"></div>
  <div id="viewer" class="viewer">Select file</div>
</div>

<script>
const files = {files_str};

const list = document.getElementById("list");
const viewer = document.getElementById("viewer");

files.forEach(f => {{
  const div = document.createElement("div");
  div.className = "file-item";
  div.textContent = f.name;

  div.onclick = async () => {{
    const ext = f.name.split('.').pop().toLowerCase();

    if (["png","jpg","jpeg","gif","webp"].includes(ext)) {{
      viewer.innerHTML = `<img src="${{f.path}}">`;
    }} else {{
      const res = await fetch(f.path);
      const text = await res.text();
      viewer.innerHTML = `<pre>${{escapeHtml(text)}}</pre>`;
    }}
  }};

  list.appendChild(div);
}});

function escapeHtml(str) {{
  return str.replace(/[&<>"']/g, m => ({{
    '&':'&amp;',
    '<':'&lt;',
    '>':'&gt;',
    '"':'&quot;',
    "'":'&#39;'
  }}[m]));
}}
</script>

</body>
</html>
"""

    return html


def main():
    files = scan_files()
    html = generate_html(files)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated {OUTPUT} with {len(files)} files")


if __name__ == "__main__":
    main()
