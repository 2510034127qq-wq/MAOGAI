"""tile stills into one contact sheet: python tools/sheet.py out.jpg img1 img2 ..."""
import sys
from PIL import Image, ImageDraw, ImageFont

out, *paths = sys.argv[1:]
ims = [Image.open(p).convert("RGB") for p in paths]
w, h = ims[0].size
cols = 2 if len(ims) > 1 else 1
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), (40, 40, 40))
font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", 22)
for i, (im, p) in enumerate(zip(ims, paths)):
    x, y = (i % cols) * (w + 8), (i // cols) * (h + 8)
    sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), p.replace("\\", "/").split("/")[-1], fill=(255, 0, 255), font=font)
sheet.save(out, quality=88)
print(out, sheet.size)
