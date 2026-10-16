"""Build index.html: inline the guide sprites (from ../isms-animation/assets/characters) and the narration timing."""
import base64, json, pathlib, re
root = pathlib.Path(__file__).parent
tpl = (root / "src/template.html").read_text(encoding="utf-8")
chars = root.parent / "isms-animation/assets/characters"
names = sorted(set(re.findall(r'"((?:allan|arale)_[a-z0-9]+)"', tpl)) | set(re.findall(r'SPRITES\.((?:allan|arale)_[a-z0-9]+)', tpl)))
sprites = {n: "data:image/webp;base64," + base64.b64encode((chars / f"{n}.webp").read_bytes()).decode() for n in names}
audio = (root / "src/audio.json").read_text(encoding="utf-8") if (root / "src/audio.json").exists() else "[]"
html = tpl.replace("__SPRITES__", json.dumps(sprites)).replace("__AUDIO__", audio)
(root / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written ({len(html)//1024} KB, sprites: {', '.join(names)})")
