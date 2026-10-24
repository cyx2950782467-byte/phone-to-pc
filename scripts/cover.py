from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1146, 717
OUT = "/home/cyx/whale-render/cover.png"

def F(sz, bold=True):
    p = ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold
         else "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    return ImageFont.truetype(p, sz)

img = Image.new("RGB", (W, H), "#0a1020")
d = ImageDraw.Draw(img)

# 渐变背景
for y in range(H):
    k = y / H
    d.line([(0, y), (W, y)], fill=(int(10+8*k), int(16+14*k), int(32+34*k)))

# 深色终端条
d.rectangle([0, 0, W, 46], fill=(38, 34, 48))
d.ellipse([16, 16, 30, 30], fill=(240, 100, 90))
d.ellipse([38, 16, 52, 30], fill=(240, 200, 90))
d.ellipse([60, 16, 74, 30], fill=(110, 200, 110))

F_BIG = F(64)
F_SUB = F(30, bold=False)
F_SMALL = F(24, bold=False)
F_MONO = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 34)

# 主标题
d.text((W//2, 170), "手机 → 电脑", font=F_BIG, fill=(235, 244, 255), anchor="mm")
d.text((W//2, 245), "Tailscale + SSH 全过程", font=F_SUB, fill=(140, 185, 235), anchor="mm")

# 中间一条线 + 两个点
d.line([(220, 340), (926, 340)], fill=(70, 110, 160), width=3)
d.ellipse([196, 320, 244, 368], outline=(120, 200, 240), width=4)
d.ellipse([902, 320, 950, 368], outline=(120, 220, 150), width=4)
d.text((220, 400), "android", font=F_SMALL, fill=(120, 200, 240), anchor="mm")
d.text((926, 400), "linux", font=F_SMALL, fill=(120, 220, 150), anchor="mm")

# 那句台词
d.text((W//2, 490), "它没问我要密码", font=F(46), fill=(255, 200, 110), anchor="mm")

# 底部三行
d.text((W//2, 570), "实拍终端  ·  动画讲解  ·  三个真踩出来的坑", font=F_SMALL,
       fill=(140, 175, 215), anchor="mm")
d.text((W//2, 640), "公钥是名牌，私钥是签名 ｜ 验证状态，别信界面", font=F_SMALL,
       fill=(120, 155, 200), anchor="mm")

img.save(OUT)
print("SAVED", OUT, os.path.getsize(OUT), "bytes")
