"""Build index.html: inline the character sprites and the audio timing (src/timing.json) into src/template.html.
The page loads its voice files from audio/ next to index.html (run build_audio.py first)."""
import base64, json, pathlib
root = pathlib.Path(__file__).parent
sprites = {p.stem: "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode()
           for p in sorted((root / "assets/characters").glob("*.webp"))}
timing = (root / "src/timing.json").read_text(encoding="utf-8") if (root / "src/timing.json").exists() else "{}"
html = (root / "src/template.html").read_text(encoding="utf-8").replace("__SPRITES__", json.dumps(sprites)).replace("__TIMING__", timing)
(root / "index.html").write_text(html, encoding="utf-8")
print(f"index.html written ({len(html)//1024} KB, {len(sprites)} sprites)")
