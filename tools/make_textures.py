"""Paper texture + film grain tiles for the Remotion project."""
import numpy as np, pathlib
from PIL import Image, ImageFilter

OUT = pathlib.Path(__file__).resolve().parents[1] / "video/public/tex"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(1956)
W, H = 1920, 1080


def blur_noise(scale, sigma):
    n = rng.random((H // scale + 2, W // scale + 2)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sigma))
    a = np.asarray(im).astype(np.float32) / 255
    return (a - a.mean()) / (a.std() + 1e-6)


base = np.array([0xED, 0xE5, 0xD4], np.float32)
mott = 0.55 * blur_noise(60, 40) + 0.3 * blur_noise(12, 6)
fine = rng.normal(0, 1, (H, W)).astype(np.float32)
fib = np.zeros((H, W), np.float32)
for _ in range(2600):
    x, y = rng.integers(0, W), rng.integers(0, H)
    ang, L = rng.random() * np.pi, rng.integers(8, 40)
    xs = (x + np.cos(ang) * np.arange(L)).astype(int).clip(0, W - 1)
    ys = (y + np.sin(ang) * np.arange(L) + np.sin(np.arange(L) / 6) * 2).astype(int).clip(0, H - 1)
    fib[ys, xs] += rng.choice([-1, 1]) * rng.uniform(0.4, 1.0)
fib = np.asarray(Image.fromarray(((fib + 3) * 40).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 40 - 3

yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
vig = 1 - 0.10 * np.clip(r - 0.35, 0, None) ** 1.6

lum = (1 + 0.018 * mott + 0.010 * fine + 0.012 * fib) * vig
img = base[None, None, :] * lum[..., None]
img[..., 2] -= 3 * np.clip(r - 0.6, 0, None)
Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(OUT / "paper.jpg", quality=95)

for i in range(6):
    g = rng.normal(128, 38, (540, 960)).clip(0, 255).astype(np.uint8)
    Image.fromarray(g).resize((1920, 1080), Image.NEAREST).filter(ImageFilter.GaussianBlur(0.5)).save(OUT / f"grain{i}.png")
print("ok")
