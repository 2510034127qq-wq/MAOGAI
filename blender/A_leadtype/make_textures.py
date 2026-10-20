"""Deterministic, local STSONG ink impressions and paper-fibre maps."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "textures"
OUT.mkdir(exist_ok=True)
W, H = 4096, 3072
PW, PH = 10.5, 8.0
rng = np.random.default_rng(1976)


def noise(w, h, scale):
    a = rng.random((max(2, h // scale), max(2, w // scale)))
    return np.asarray(Image.fromarray(np.uint8(a * 255)).resize((w, h), Image.Resampling.BICUBIC), dtype=np.float32) / 255


def main():
    coarse = noise(W, H, 180)
    medium = noise(W, H, 22)
    fine = noise(W, H, 3)
    grain = rng.random((H, W), dtype=np.float32)
    fibre = Image.new("L", (W, H), 128)
    d = ImageDraw.Draw(fibre)
    for _ in range(35000):
        x, y = rng.integers(0, W), rng.integers(0, H)
        l = rng.uniform(3, 24)
        a = rng.uniform(-.5, .5)
        d.line((x, y, x + l, y + a * l), fill=int(rng.integers(70, 180)), width=1)
    fibres = np.asarray(fibre.filter(ImageFilter.GaussianBlur(.35)), dtype=np.float32) / 255
    texture = .35 * coarse + .22 * medium + .13 * fine + .10 * grain + .20 * fibres
    Image.fromarray(np.uint8(texture * 255)).save(OUT / "paper_fibre.png")
    mask = Image.new("L", (W, H), 0)
    for ch, x, y, degrees in [("破", -1.0, -2.0, -1.4), ("立", 1.0, -2.0, .7)]:
        font = ImageFont.truetype("C:/Windows/Fonts/STSONG.TTF", 700)
        box = font.getbbox(ch)
        glyph = Image.new("L", (box[2] - box[0] + 30, box[3] - box[1] + 30), 0)
        ImageDraw.Draw(glyph).text((15 - box[0], 15 - box[1]), ch, font=font, fill=255)
        crop = glyph.getbbox()
        glyph = glyph.crop(crop)
        glyph.thumbnail((int(1.30 / PW * W), int(1.30 / PH * H)), Image.Resampling.LANCZOS)
        glyph = glyph.rotate(degrees, resample=Image.Resampling.BICUBIC, expand=True)
        cx, cy = int((x / PW + .5) * W), int((.5 - y / PH) * H)
        mask.paste(glyph, (cx - glyph.width // 2, cy - glyph.height // 2))
    mask.save(OUT / "stamp_height.png")
    crisp = np.asarray(mask, dtype=np.float32) / 255
    bleed = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.1)), dtype=np.float32) / 255
    spread = np.asarray(mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(1.3)), dtype=np.float32) / 255
    patch = .68 + .20 * noise(W, H, 38) + .12 * fine
    pinhole = np.clip((grain - .986) * 25, 0, .36)
    alpha = np.maximum(crisp * (patch - pinhole), spread * .25 + bleed * .22)
    alpha = np.clip(alpha, 0, 1)
    rgba = np.empty((H, W, 4), np.uint8)
    rgba[:, :, :3] = (181, 48, 42)
    rgba[:, :, 3] = np.uint8(alpha * 255)
    Image.fromarray(rgba).save(OUT / "stamp_ink.png")
    Image.fromarray(np.uint8(alpha * 255)).save(OUT / "stamp_alpha.png")
    (OUT / "manifest.json").write_text(json.dumps({
        "font": "C:/Windows/Fonts/STSONG.TTF", "seed": 1976,
        "resolution": [W, H], "paper_size_units": [PW, PH],
        "stamp_characters_normal": ["破", "立"],
        "stamp_centres": [[-1, -2], [1, -2]], "ink_srgb": "#B5302A",
        "paper_srgb": "#EDE5D4", "physical_unit_metres": .004,
    }, ensure_ascii=False, indent=2), encoding="utf8")


if __name__ == "__main__":
    main()
