import glob, os, json, subprocess

BASE = "/home/cyx/whale-render"
DIRS = ["term", "anim3", "end4"]
VO   = os.path.join(BASE, "vo")
OUT  = os.path.join(BASE, "tutorial_av.mp4")

# 1) 拼帧清单
out = []
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(BASE, d, "f*.png"))):
        out.append(f"file '{f}'")
        out.append("duration 0.0416667")
out.append(f"file '{os.path.join(BASE, DIRS[-1], sorted(os.listdir(os.path.join(BASE, DIRS[-1])))[-1])}'")
open(os.path.join(BASE, "list2.txt"), "w").write("\n".join(out) + "\n")
total_frames = sum(len(glob.glob(os.path.join(BASE, d, "f*.png"))) for d in DIRS)
vlen = total_frames / 24.0
print(f"帧数 {total_frames} -> 视频 {vlen:.2f}s")

# 2) 无声视频
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", os.path.join(BASE, "list2.txt"), "-r", "24",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                "-preset", "medium", os.path.join(BASE, "silent.mp4")],
               check=True, capture_output=True)
print("silent.mp4 ok")

# 3) 按 timeline 排配音（每句紧接上句，间隔 0.15s）
meta = json.load(open(os.path.join(VO, "meta.json")))
t = 0.4
filters = []
inputs = ["-i", os.path.join(BASE, "silent.mp4")]
for idx, x in enumerate(meta):
    inputs += ["-i", x["file"]]
    delay = int(t * 1000)
    filters.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    t += x["dur"] + 0.15
print(f"配音铺到 {t:.1f}s / 视频 {vlen:.1f}s")

# 混音
mix_in = "".join(f"[a{i}]" for i in range(len(meta)))
fc = ";".join(filters) + f";{mix_in}amix=inputs={len(meta)}:duration=longest:normalize=0[aout]"
cmd = ["ffmpeg", "-y"] + inputs + [
    "-filter_complex", fc,
    "-map", "0:v", "-map", "[aout]",
    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
    "-t", str(vlen), OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
print("rc:", r.returncode)
if r.returncode != 0:
    print(r.stderr[-800:])
else:
    print("OUT", OUT)
