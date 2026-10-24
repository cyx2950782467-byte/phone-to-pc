import subprocess, os, re, json

SRC = "/tmp/voiceover.md"
OUT = "/home/cyx/whale-render/vo"
os.makedirs(OUT, exist_ok=True)

lines = []
for ln in open(SRC, encoding="utf-8"):
    m = re.match(r"^0?(\d{3})\s+\[([\d.]+)s\]\s+(.+)$", ln.strip())
    if m:
        lines.append({"id": int(m.group(1)), "start": float(m.group(2)), "text": m.group(3)})

print("lines:", len(lines))
voice = "zh-CN-XiaoyiNeural"
ok = 0
meta = []
for it in lines:
    f = f"{OUT}/v{it['id']:03d}.mp3"
    if not os.path.exists(f):
        r = subprocess.run(
            ["edge-tts", "--voice", voice, "--text", it["text"],
             "--rate", "+8%", "--write-media", f],
            capture_output=True, text=True, timeout=90)
        if r.returncode != 0:
            print("FAIL", it["id"], r.stderr[:200])
            continue
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", f],
        capture_output=True, text=True).stdout.strip() or 0)
    meta.append({**it, "file": f, "dur": round(dur, 3)})
    ok += 1
    print(f"{it['id']:03d} {dur:6.2f}s  {it['text'][:28]}")

json.dump(meta, open(f"{OUT}/meta.json", "w"), ensure_ascii=False, indent=1)
print("OK", ok, "/", len(lines))
