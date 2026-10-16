"""Build the single-file animation page: inline the character sprites into src/template.html."""
import base64, json, pathlib
root = pathlib.Path(__file__).parent
sprites = {p.stem: "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode()
           for p in sorted((root / "assets/characters").glob("*.webp"))}
html = (root / "src/template.html").read_text(encoding="utf-8").replace("__SPRITES__", json.dumps(sprites))
(root / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written ({len(html)//1024} KB, {len(sprites)} sprites)")
