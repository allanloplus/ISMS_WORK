"""Generate voice lines (LINES in src/template.html) with Microsoft Edge neural TTS.

Allan 顧問：zh-TW-YunJheNeural（台灣男聲），語速 +20%
阿拉蕾：  zh-TW-HsiaoYuNeural，語速 +20%、音高 +35Hz（活潑俏皮的小女生）
Writes audio/*.mp3 and src/audio.json. Run: python3 build_audio.py && python3 build.py
"""
import asyncio, hashlib, json, os, pathlib, re, ssl, subprocess
import edge_tts, edge_tts.communicate as comm

CA = "/root/.ccr/ca-bundle.crt"
if os.path.exists(CA):
    comm._SSL_CTX = ssl.create_default_context(cafile=CA)
VOICES = {"A": dict(voice="zh-TW-YunJheNeural", rate="+20%", pitch="+0Hz"),
          "R": dict(voice="zh-TW-HsiaoYuNeural", rate="+20%", pitch="+35Hz")}
SAY = [("ISO 27001", "ISO 二七零零一"), ("ISMS", "I S M S")]

root = pathlib.Path(__file__).parent
src = (root / "src/template.html").read_text(encoding="utf-8")
block = src.split("const LINES = {", 1)[1].split("\n};", 1)[0]
rows = re.findall(r'(\w+): \["([AR])", "(\w+)", "((?:[^"\\]|\\.)*)"\]', block)
out = root / "audio"; out.mkdir(exist_ok=True)

def duration(p):
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return round(float(r.stdout.strip()), 3)

async def main():
    res, used = {}, set()
    for key, who, _f, text in rows:
        say = text
        for a, b in SAY: say = say.replace(a, b)
        v = VOICES[who]
        h = hashlib.sha1(json.dumps([v, say], ensure_ascii=False).encode()).hexdigest()[:8]
        name = f"{key}_{who}_{h}.mp3"; path = out / name; used.add(name)
        if not path.exists():
            for k in range(4):
                try:
                    await edge_tts.Communicate(say, v["voice"], rate=v["rate"], pitch=v["pitch"]).save(str(path)); break
                except Exception as e:
                    print("retry", name, e); await asyncio.sleep(2 ** k)
            print("generated", name)
        res[key] = {"src": f"audio/{name}", "dur": duration(path)}
    for p in out.glob("*.mp3"):
        if p.name not in used: p.unlink()
    (root / "src/audio.json").write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    print(len(res), "lines,", round(sum(x["dur"] for x in res.values())), "s")

asyncio.run(main())
