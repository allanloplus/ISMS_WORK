"""Generate one MP3 per dialogue line with Microsoft Edge neural TTS (edge-tts).

Allan 顧問：zh-TW-YunJheNeural（台灣男聲），語速 +20%
阿拉蕾：  zh-TW-HsiaoYuNeural（台灣女聲），語速 +20%、音高 +35Hz，活潑俏皮的小女生
（與先前動畫課的配音設定一致）

Reads the SCRIPT lines from src/template.html, writes audio/*.mp3 and src/timing.json.
Files are named by a hash of voice settings + text, so unchanged lines are not regenerated.
Run: python3 build_audio.py && python3 build.py
"""
import asyncio, hashlib, json, os, pathlib, re, ssl, subprocess
import edge_tts, edge_tts.communicate as comm

CA = "/root/.ccr/ca-bundle.crt"
if os.path.exists(CA):  # sandbox proxy CA; harmless elsewhere
    comm._SSL_CTX = ssl.create_default_context(cafile=CA)

VOICES = {
    "A": dict(voice="zh-TW-YunJheNeural", rate="+20%", pitch="+0Hz"),
    "R": dict(voice="zh-TW-HsiaoYuNeural", rate="+20%", pitch="+35Hz"),
}
# 發音修正：畫面字幕不變，只改朗讀文字
SAY = [("ISO 27001", "ISO 二七零零一"), ("OS／AP／DB", "OS、AP、DB")]

root = pathlib.Path(__file__).parent
src = (root / "src/template.html").read_text(encoding="utf-8")
block = src.split("const SCRIPT = {", 1)[1].split("\n};", 1)[0]
scenes = re.findall(r'^\s*(\w+): \{ name: "[^"]*", lines: \[(.*?)\n\s*\]\},', block, re.S | re.M)
out_dir = root / "audio"; out_dir.mkdir(exist_ok=True)

def duration(path):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return round(float(r.stdout.strip()), 3)

async def main():
    timing, used = {}, set()
    for si, (sid, body) in enumerate(scenes):
        rows = re.findall(r'\["([AR])", "(\w+)", "((?:[^"\\]|\\.)*)"\]', body)
        timing[sid] = []
        for li, (who, _face, text) in enumerate(rows):
            say = text
            for a, b in SAY: say = say.replace(a, b)
            v = VOICES[who]
            h = hashlib.sha1(json.dumps([v, say], ensure_ascii=False).encode()).hexdigest()[:8]
            name = f"s{si:02d}_l{li + 1:02d}_{who}_{h}.mp3"
            path = out_dir / name; used.add(name)
            if not path.exists():
                for attempt in range(4):
                    try:
                        await edge_tts.Communicate(say, v["voice"], rate=v["rate"], pitch=v["pitch"]).save(str(path)); break
                    except Exception as e:
                        print("retry", name, e); await asyncio.sleep(2 ** attempt)
                print("generated", name)
            timing[sid].append({"src": f"audio/{name}", "dur": duration(path)})
    for p in out_dir.glob("*.mp3"):
        if p.name not in used: p.unlink()
    (root / "src/timing.json").write_text(json.dumps(timing, ensure_ascii=False, indent=1), encoding="utf-8")
    print(sum(len(v) for v in timing.values()), "lines,", round(sum(x["dur"] for v in timing.values() for x in v)), "s of audio")

asyncio.run(main())
