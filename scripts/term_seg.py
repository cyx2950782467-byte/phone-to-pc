from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1280, 720
FPS = 24
OUT = "/home/cyx/whale-render/term"
os.makedirs(OUT, exist_ok=True)

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
MONO2 = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
CJK  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

FS = 20
FM = ImageFont.truetype(MONO, FS)

# 终端配色（偏 Ubuntu）
BG   = (24, 22, 34)
FG   = (222, 222, 222)
GRN  = (120, 220, 130)
CYN  = (110, 200, 230)
YEL  = (240, 210, 120)
RED  = (240, 120, 120)
DIM  = (140, 140, 150)
PROMPT_C = (120, 220, 130)

PROMPT = "cyx@cyx-GI5CN54:~$ "
PAD_X, PAD_Y = 40, 36
LH = 30

# 脚本：(类型, 内容, 停留秒数)
#   cmd  = 逐字敲出的命令
#   out  = 直接输出的行（颜色, 文本）
#   wait = 空等
SCRIPT = [
    ("label", "— 从头跑一遍 —", 0.6),
    ("cmd", "tailscale status", 0.7),
    ("out", (DIM,  "100.98.151.78   3               android   -"), 0.0),
    ("out", (GRN,  "100.112.77.54   cyx-gi5cn54     linux     -"), 1.0),
    ("wait", 0.4),
    ("cmd", "ping -c 2 100.112.77.54", 0.6),
    ("out", (FG,   "64 bytes from 100.112.77.54: icmp_seq=1 ttl=64 time=41.2 ms"), 0.0),
    ("out", (FG,   "64 bytes from 100.112.77.54: icmp_seq=2 ttl=64 time=38.7 ms"), 0.9),
    ("wait", 0.3),
    ("cmd", "ssh cyx@100.112.77.54 \"hostname; uname -m\"", 0.8),
    ("out", (CYN,  "cyx-GI5CN54"), 0.0),
    ("out", (CYN,  "x86_64"), 1.0),
    ("wait", 0.3),
    ("cmd", "echo '它没问我要密码'", 0.8),
    ("out", (YEL,  "它没问我要密码"), 0.0),
    ("wait", 2.2),
]

def load_cjk(sz):
    try: return ImageFont.truetype(CJK, sz)
    except Exception: return FM
FC = load_cjk(20)
FCB = load_cjk(26)

# 预生成每一行在"完全敲完"后的字符数，用于逐字动画
def build_schedule():
    """返回 (total_frames, frame -> (已完成的script索引, 当前行已敲字符数))"""
    events = []   # (frame_start, frame_end, kind, payload)
    f = 0
    for kind, *rest in SCRIPT:
        if kind == "cmd":
            txt, hold = rest
            n = len(txt)
            typ = 22 * 0.045        # 每字符 ~0.045s
            dur_frames = max(1, int(n * typ * FPS))
            events.append((f, f + dur_frames, "cmd", txt, n))
            f += dur_frames
            f += int(hold * FPS)
        elif kind == "out":
            color, txt, hold = rest
            events.append((f, f, "out", (color, txt), 0))
            f += int(hold * FPS)
        elif kind == "wait":
            events.append((f, f, "wait", None, 0))
            f += int(rest[0] * FPS)
        elif kind == "label":
            txt, hold = rest
            events.append((f, f, "label", txt, 0))
            f += int(hold * FPS)
    return events, f

events, total = build_schedule()
print("TERM TOTAL FRAMES", total)

def render_frame(target):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 顶部标题栏
    d.rectangle([0, 0, W, 30], fill=(44, 40, 56))
    d.ellipse([14, 10, 24, 20], fill=(240, 100, 90))
    d.ellipse([30, 10, 40, 20], fill=(240, 200, 90))
    d.ellipse([46, 10, 56, 20], fill=(110, 200, 110))
    d.text((W//2, 15), "cyx@cyx-GI5CN54:~", font=FM, fill=(180, 180, 190), anchor="mm")

    y = PAD_Y + 20
    lines = []
    for (fs, fe, kind, payload, n) in events:
        if target < fs:
            break
        if kind == "cmd":
            if target >= fe:
                lines.append(("cmd_full", payload))
            else:
                frac = (target - fs) / max(1, (fe - fs))
                k = int(frac * n)
                lines.append(("cmd_part", payload[:k]))
        elif kind == "out":
            lines.append(("out", payload))
        elif kind == "label":
            lines.append(("label", payload))

    for kind, payload in lines:
        if kind == "label":
            d.text((PAD_X, y), payload, font=FCB, fill=(140, 170, 210))
        elif kind == "cmd_full":
            d.text((PAD_X, y), PROMPT, font=FM, fill=PROMPT_C)
            pw = d.textlength(PROMPT, font=FM)
            d.text((PAD_X + pw, y), payload, font=FM, fill=FG)
        elif kind == "cmd_part":
            d.text((PAD_X, y), PROMPT, font=FM, fill=PROMPT_C)
            pw = d.textlength(PROMPT, font=FM)
            d.text((PAD_X + pw, y), payload, font=FM, fill=FG)
            cw = d.textlength(payload, font=FM)
            d.rectangle([PAD_X+pw+cw+2, y+2, PAD_X+pw+cw+12, y+FS+3], fill=(200, 200, 200))
        elif kind == "out":
            color, txt = payload
            # 含中文的用 CJK 字体
            if any('\u4e00' <= ch <= '\u9fff' for ch in txt):
                d.text((PAD_X, y), txt, font=FC, fill=color)
            else:
                d.text((PAD_X, y), txt, font=FM, fill=color)
        y += LH

    return img

for i in range(total):
    render_frame(i).save(f"{OUT}/f{i:05d}.png")
print("DONE", total)
