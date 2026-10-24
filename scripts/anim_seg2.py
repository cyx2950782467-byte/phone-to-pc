from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1280, 720
FPS = 24
OUT = "/home/cyx/whale-render/anim2"
os.makedirs(OUT, exist_ok=True)

def F(size, bold=True):
    p = ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold
         else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    try: return ImageFont.truetype(p, size)
    except Exception: return ImageFont.load_default()

def FD(size):
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)

F_BIG   = F(46)
F_MID   = F(30)
F_TXT   = F(26, False)
F_CODE  = F(23)
F_SMALL = F(20, False)
F_MARK  = FD(64)

BG1 = (10, 16, 30)
BG2 = (16, 26, 48)

def bg(d):
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)],
               fill=(int(BG1[0]+(BG2[0]-BG1[0])*k),
                     int(BG1[1]+(BG2[1]-BG1[1])*k),
                     int(BG1[2]+(BG2[2]-BG1[2])*k)))

def fade(t, start, dur=0.35):
    return 0.0 if t < start else min(1.0, (t - start) / dur)

def C(c, a):
    return (int(c[0]*a), int(c[1]*a), int(c[2]*a))

def code_box(d, x, y, w, h, lines, a):
    d.rounded_rectangle([x, y, x+w, y+h], radius=10,
                        fill=(int(18*a), int(26*a), int(44*a)),
                        outline=C((60, 110, 170), a), width=2)
    cy = y + 18
    for ln in lines:
        d.text((x+22, cy), ln, font=F_CODE, fill=C((150, 200, 250), a))
        cy += 34

# ---------- 段 1：公钥是名牌（4s） ----------
def seg1(t):
    img = Image.new("RGB", (W, H), BG1); d = ImageDraw.Draw(img); bg(d)
    a = fade(t, 0.1)
    d.text((W//2, 88), "公钥是名牌，私钥是签名", font=F_BIG,
           fill=C((230, 240, 255), a), anchor="mm")
    a2 = fade(t, 0.5)
    code_box(d, 110, 185, 1060, 165, [
        "$ ssh-keygen -t ed25519 -N \"\" -f ~/.ssh/id_ed25519",
        "$ cat ~/.ssh/id_ed25519.pub",
        "ssh-ed25519 AAAAC3... whale-phone   <- 这个可以随便给人",
    ], a2)
    a3 = fade(t, 1.6)
    d.text((W//2, 430), "另一半（id_ed25519，没有 .pub）永远不要出门", font=F_MID,
           fill=C((255, 170, 120), a3), anchor="mm")
    a4 = fade(t, 2.4)
    d.text((W//2, 530), "它不能冒充你，只能验证你", font=F_TXT,
           fill=C((140, 180, 220), a4), anchor="mm")
    return img

# ---------- 段 2：xclip vs xsel（4s） ----------
def seg2(t):
    img = Image.new("RGB", (W, H), BG1); d = ImageDraw.Draw(img); bg(d)
    a = fade(t, 0.1)
    d.text((W//2, 78), "剪贴板：xclip 会空，xsel 不会", font=F_BIG,
           fill=C((230, 240, 255), a), anchor="mm")

    a1 = fade(t, 0.4)
    d.rounded_rectangle([80, 155, 620, 545], radius=12,
                        fill=(int(30*a1), int(20*a1), int(24*a1)),
                        outline=C((200, 80, 80), a1), width=3)
    d.text((350, 195), "xclip", font=F_MID, fill=C((255, 120, 120), a1), anchor="mm")
    d.text((350, 265), "进程一退出", font=F_TXT, fill=C((230, 180, 180), a1), anchor="mm")
    d.text((350, 315), "剪贴板就空了", font=F_TXT, fill=C((230, 180, 180), a1), anchor="mm")
    if a1 > 0.5:
        pulse = (math.sin(t * 6) + 1) / 2
        d.text((350, 425), "\u2717", font=F_MARK,
               fill=C((220, 70, 70), a1 * (0.45 + 0.55*pulse)), anchor="mm")

    a2 = fade(t, 0.9)
    d.rounded_rectangle([660, 155, 1200, 545], radius=12,
                        fill=(int(18*a2), int(30*a2), int(24*a2)),
                        outline=C((80, 200, 120), a2), width=3)
    d.text((930, 195), "xsel", font=F_MID, fill=C((120, 240, 160), a2), anchor="mm")
    d.text((930, 265), "内容一直留着", font=F_TXT, fill=C((180, 230, 190), a2), anchor="mm")
    d.text((930, 315), "进程活着就在", font=F_TXT, fill=C((180, 230, 190), a2), anchor="mm")
    if a2 > 0.5:
        d.text((930, 425), "\u2713", font=F_MARK,
               fill=C((80, 220, 130), a2), anchor="mm")

    a3 = fade(t, 2.4)
    d.text((W//2, 620), "实测：中英文 Mixed Test —— 一个字没丢", font=F_SMALL,
           fill=C((140, 180, 220), a3), anchor="mm")
    return img

# ---------- 段 3：中文为什么进不去（4s） ----------
def seg3(t):
    img = Image.new("RGB", (W, H), BG1); d = ImageDraw.Draw(img); bg(d)
    a = fade(t, 0.1)
    d.text((W//2, 78), "为什么中文打不进去", font=F_BIG,
           fill=C((230, 240, 255), a), anchor="mm")

    a1 = fade(t, 0.4)
    d.text((W//2, 190), "xdotool / pyautogui  ->  XTEST  ->  键盘扫描码", font=F_MID,
           fill=C((150, 200, 250), a1), anchor="mm")

    a2 = fade(t, 1.0)
    d.rounded_rectangle([140, 275, 1140, 400], radius=10,
                        fill=(int(20*a2), int(28*a2), int(46*a2)),
                        outline=C((90, 130, 190), a2), width=2)
    d.text((640, 338), "中文在 X11 里没有对应的扫描码", font=F_TXT,
           fill=C((220, 230, 245), a2), anchor="mm")

    a3 = fade(t, 1.9)
    d.text((W//2, 470), "不是「偶尔丢字」，是一个都进不去", font=F_MID,
           fill=C((255, 170, 120), a3), anchor="mm")

    a4 = fade(t, 2.7)
    d.text((W//2, 565), "所以走剪贴板 —— 让浏览器自己把字符放进去", font=F_SMALL,
           fill=C((140, 180, 220), a4), anchor="mm")
    return img

# ---------- 段 4：验证状态，别信界面（4s） ----------
def seg4(t):
    img = Image.new("RGB", (W, H), BG1); d = ImageDraw.Draw(img); bg(d)
    a = fade(t, 0.1)
    d.text((W//2, 78), "验证状态，别信界面", font=F_BIG,
           fill=C((230, 240, 255), a), anchor="mm")

    rows = [
        ("登录页说 Login successful", "tailscale status 说 Logged out", 0.4),
        ("xclip 没报错", "剪贴板已经空了", 0.9),
        ("xdotool type 退出码 0", "九个字符丢了八个", 1.4),
    ]
    y = 190
    for left, right, st in rows:
        ra = fade(t, st, 0.3)
        if ra > 0:
            d.text((150, y), left, font=F_TXT, fill=C((200, 210, 230), ra), anchor="lm")
            d.text((640, y), "->", font=F_MID, fill=C((120, 160, 210), ra), anchor="lm")
            d.text((710, y), right, font=F_TXT, fill=C((255, 150, 120), ra), anchor="lm")
        y += 88

    a5 = fade(t, 2.3)
    d.text((W//2, 545), "三句谎话，出在三个不同的层", font=F_MID,
           fill=C((255, 200, 120), a5), anchor="mm")
    a6 = fade(t, 2.9)
    d.text((W//2, 625), "去问机器要状态，然后读它的回答", font=F_SMALL,
           fill=C((140, 180, 220), a6), anchor="mm")
    return img

SEGS = [(seg1, 4), (seg2, 4), (seg3, 4), (seg4, 4)]
idx = 0
for fn, dur in SEGS:
    for i in range(FPS * dur):
        fn(i / FPS).save(f"{OUT}/f{idx:05d}.png")
        idx += 1
print("FRAMES", idx)
