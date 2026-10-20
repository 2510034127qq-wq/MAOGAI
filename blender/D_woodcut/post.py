"""任务 D：从保留的生成原图重建木刻交付物。仅做任务书授权的印前后期。

运行：python blender/D_woodcut/post.py
依赖：Pillow、numpy、scipy。所有路径相对本文件解析，与工作目录无关。
原图绝不覆写。阈值与随机种子固定；生成模型本身不承诺可复现。
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import platform
from pathlib import Path

import numpy as np
import PIL
import scipy
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / "assets" / "img" / "raw"
INK = np.array((28, 26, 23), dtype=np.uint8)
PAPER = np.array((237, 229, 212), dtype=np.uint8)
MASTER_SIZE = (2560, 1440)
PAPER_SIZE = (1920, 1080)
# 全景版心占画布 74%，四边各留约 13% 纸边，不加边框或字。
# 主体位于中央 70%；最外围约 2% 是可以再裁去的环境。
PLATE_SCALE = 0.74
THRESHOLD = 155
MIN_COMPONENT_AREA = 4
SEED = 20261020
SUBJECTS = (
    "nongqingzhong", "yanhai", "neidi",
    "muji_maer", "aq", "kongqi_senlin_baozang",
)
SELECTED = {name: f"{name}_v4.png" for name in SUBJECTS}
SELECTED.update(yanhai="yanhai_v5.png", aq="aq_v5.png")
HORIZONTAL_SHIFT = {"muji_maer": -0.008, "neidi": -0.008}
# 原图归一化关键内容框。由逐张目视确定，用于裁切检查而非自动识别。
ESSENTIAL_BOXES = {
    "nongqingzhong": [0.20, 0.16, 0.86, 0.91],
    "yanhai": [0.105, 0.073, 0.969, 0.72],
    "neidi": [0.13, 0.29, 0.978, 0.82],
    "muji_maer": [0.115, 0.20, 0.982, 0.855],
    "aq": [0.205, 0.21, 0.782, 0.91],
    "kongqi_senlin_baozang": [0.11, 0.05, 0.75, 0.96],
}
# 局部检查：刀痕、结构、人物/动物、关键叙事元素。
DETAIL_BOXES = {
    "nongqingzhong": [0.20, 0.16, 0.86, 0.91],
    "yanhai": [0.105, 0.073, 0.969, 0.72],
    "neidi": [0.13, 0.29, 0.978, 0.82],
    "muji_maer": [0.115, 0.20, 0.982, 0.855],
    "aq": [0.205, 0.21, 0.782, 0.91],
    "kongqi_senlin_baozang": [0.11, 0.05, 0.75, 0.96],
}


def png_bytes(image: Image.Image) -> bytes:
    output = io.BytesIO()
    image.save(output, format="PNG", compress_level=9)
    return output.getvalue()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def print_mask(path: Path, name: str) -> tuple[np.ndarray, dict]:
    with Image.open(path) as source:
        source.load()
        source_size = list(source.size)
        gray = source.convert("L")
    # 只做不足 0.1% 的纵横比归一化；没有生成超分细节。
    plate_size = tuple(round(v * PLATE_SCALE) for v in MASTER_SIZE)
    gray = gray.resize(plate_size, Image.Resampling.LANCZOS)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.0, percent=85, threshold=3))
    mask = np.asarray(gray) < THRESHOLD
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    areas = np.bincount(labels.ravel())
    remove = areas < MIN_COMPONENT_AREA
    remove[0] = False
    dropped = remove[labels]
    mask[dropped] = False
    # 不做开闭运算或轮廓平滑，保留连接着主体的刀痕毛边与白色刀口。
    canvas = np.zeros((MASTER_SIZE[1], MASTER_SIZE[0]), dtype=bool)
    x = (MASTER_SIZE[0] - plate_size[0]) // 2
    y = (MASTER_SIZE[1] - plate_size[1]) // 2
    x += round(MASTER_SIZE[0] * HORIZONTAL_SHIFT.get(name, 0))
    canvas[y:y + plate_size[1], x:x + plate_size[0]] = mask
    stats = {
        "source_size": source_size,
        "plate_pixels": list(plate_size),
        "plate_origin": [x, y],
        "threshold": THRESHOLD,
        "removed_black_components": int(np.count_nonzero(remove)),
        "removed_black_pixels": int(dropped.sum()),
        "ink_fraction_of_canvas": round(float(canvas.mean()), 6),
        "original_black_components": int(count),
    }
    return canvas, stats


def transparent_ink(mask: np.ndarray) -> Image.Image:
    # 透明像素的隐藏 RGB 也用墨色，避免非预乘合成的白色描边。
    rgba = np.empty((*mask.shape, 4), dtype=np.uint8)
    rgba[:, :, :3] = INK
    rgba[:, :, 3] = mask.astype(np.uint8) * 255
    return Image.fromarray(rgba)


def normalized_field(rng: np.random.Generator, size: tuple[int, int],
                     sigma: float | tuple[float, float]) -> np.ndarray:
    noise = rng.standard_normal(size).astype(np.float32)
    field = ndimage.gaussian_filter(noise, sigma=sigma)
    return field / max(float(field.std()), 1e-6)


def paper_print(mask: np.ndarray, index: int) -> tuple[Image.Image, dict]:
    rng = np.random.default_rng(SEED + index)
    # 缩小后再次阈值化，纸版也不使用半透明灰边。
    small = Image.fromarray(mask.astype(np.uint8) * 255).resize(
        PAPER_SIZE, Image.Resampling.LANCZOS
    )
    coverage = np.asarray(small) >= 128
    shape = coverage.shape
    paper_noise = (
        0.45 * rng.standard_normal(shape).astype(np.float32)
        + 0.42 * normalized_field(rng, shape, 7)
        + 0.24 * normalized_field(rng, shape, (0.6, 4.5))
    )
    # 极淡纤维，仅 ±2 RGB；不添加棕色污渍、暗角、渐变光照。
    paper_delta = np.clip(np.rint(paper_noise), -2, 2).astype(np.int16)
    paper = np.clip(PAPER.astype(np.int16) + paper_delta[:, :, None], 0, 255)
    ink_noise = (
        0.70 * normalized_field(rng, shape, 16)
        + 0.40 * normalized_field(rng, shape, 1.5)
    )
    ink_delta = np.clip(np.rint(ink_noise), -2, 3).astype(np.int16)
    ink = INK.astype(np.int16) + ink_delta[:, :, None]
    # 漏白仅出现在粗墨块内部，保护细吊索、辫子、腿与脚手架。
    interior = ndimage.distance_transform_edt(coverage) > 1.5
    dropout = (rng.random(shape) < 0.0013) & interior
    printed = coverage & ~dropout
    rgb = np.where(printed[:, :, None], ink, paper).astype(np.uint8)
    return Image.fromarray(rgb), {
        "seed": SEED + index,
        "paper_base": "#EDE5D4",
        "paper_channel_variation": [-2, 2],
        "ink_channel_variation": [-2, 3],
        "white_dropouts": int(dropout.sum()),
        "white_dropouts_fraction_of_ink": round(
            float(dropout.sum() / max(coverage.sum(), 1)), 7
        ),
    }


def final_box(source_box: list[float], stats: dict) -> list[float]:
    x, y = stats["plate_origin"]
    w, h = stats["plate_pixels"]
    x0, y0, x1, y1 = source_box
    return [(x + x0 * w) / MASTER_SIZE[0],
            (y + y0 * h) / MASTER_SIZE[1],
            (x + x1 * w) / MASTER_SIZE[0],
            (y + y1 * h) / MASTER_SIZE[1]]


def pixel_box(box: list[float], size: tuple[int, int]) -> tuple[int, ...]:
    return tuple(round(v * size[i % 2]) for i, v in enumerate(box))


def validate_pair(name: str, ink_path: Path, paper_path: Path, box: list[float]) -> dict:
    with Image.open(ink_path) as image:
        image.load()
        assert image.mode == "RGBA" and image.size == MASTER_SIZE, name
        ink = np.asarray(image)
    assert np.array_equal(np.unique(ink[:, :, 3]), [0, 255]), name
    assert np.all(ink[:, :, :3] == INK), name
    assert np.count_nonzero(ink[:, :, 3] == 0) > 0, name
    black_fraction = float(np.mean(ink[:, :, 3] == 255))
    assert 0.35 <= black_fraction <= 0.50, (name, black_fraction)
    assert np.all(ink[:100, :, 3] == 0), name
    assert np.all(ink[-100:, :, 3] == 0), name
    with Image.open(paper_path) as image:
        image.load()
        assert image.mode == "RGB" and image.size == PAPER_SIZE, name
        paper = np.asarray(image).astype(np.int16)
    near_paper = np.all(np.abs(paper - PAPER.astype(np.int16)) <= 2, axis=2)
    near_ink = np.all(
        (paper - INK.astype(np.int16) >= -2)
        & (paper - INK.astype(np.int16) <= 3), axis=2
    )
    assert np.all(near_paper | near_ink), name
    assert np.all(np.median(paper[near_paper], axis=0) == PAPER), name
    assert box[0] >= 0.15 and box[1] >= 0.15, (name, box)
    assert box[2] <= 0.85 and box[3] <= 0.85, (name, box)
    versions = sorted(RAW.glob(f"{name}_v*.png"))
    assert len(versions) >= 2, name
    return {
        "pass": True,
        "raw_versions": len(versions),
        "ink_size": list(MASTER_SIZE),
        "ink_mode": "RGBA",
        "ink_rgb_unique": ["#1C1A17"],
        "alpha_unique": [0, 255],
        "intermediate_alpha_pixels": 0,
        "black_fraction_of_entire_canvas": round(black_fraction, 6),
        "director_black_mass_35_to_50_percent_pass": True,
        "paper_size": list(PAPER_SIZE),
        "paper_mode": "RGB",
        "paper_median_rgb": [237, 229, 212],
        "paper_pixels_outside_two_print_bands": 0,
        "essential_box_normalized": [round(v, 5) for v in box],
        "essential_box_within_central_70_percent": True,
        "essential_box_method": "manual visual annotation, numeric containment check",
    }


def previews(out_dir: Path, qa: Path, statistics: dict) -> None:
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 18)
    contact = Image.new("RGB", (1440, 3 * 445), tuple(PAPER))
    safe_sheet = Image.new("RGB", (1440, 3 * 435), tuple(PAPER))
    for i, name in enumerate(SUBJECTS):
        with Image.open(out_dir / f"{name}_paper.png") as opened:
            paper = opened.copy()
        col, row = i % 2, i // 2
        contact.paste(paper.resize((720, 405), Image.Resampling.LANCZOS),
                      (col * 720, row * 445 + 32))
        ImageDraw.Draw(contact).text((col * 720 + 20, row * 445 + 7),
                                    name, font=font, fill=tuple(INK))
        safe = paper.crop((288, 162, 1632, 918))
        safe.save(qa / f"{name}_crop70.png")
        safe_sheet.paste(safe.resize((704, 396), Image.Resampling.LANCZOS),
                         (col * 720 + 8, row * 435 + 32))
        ImageDraw.Draw(safe_sheet).text((col * 720 + 20, row * 435 + 7),
                                       name, font=font, fill=tuple(INK))
        with Image.open(out_dir / f"{name}_ink.png") as opened:
            opaque = Image.new("RGB", MASTER_SIZE, "white")
            opaque.paste(opened, mask=opened.getchannel("A"))
        detail = final_box(DETAIL_BOXES[name], statistics[name]["processing"])
        opaque.crop(pixel_box(detail, MASTER_SIZE)).save(qa / f"{name}_detail.png")
        # 各题全部版本同尺度比较，标注仅在 QA 图中出现。
        versions = sorted(RAW.glob(f"{name}_v*.png"))
        comparison = Image.new("RGB", (1800, 375 * ((len(versions) + 2) // 3)), "white")
        for version_index, version_path in enumerate(versions):
            with Image.open(version_path) as raw:
                thumb = raw.convert("RGB").resize((600, 338), Image.Resampling.LANCZOS)
            column, line = version_index % 3, version_index // 3
            comparison.paste(thumb, (column * 600, line * 375 + 32))
            ImageDraw.Draw(comparison).text(
                (column * 600 + 12, line * 375 + 5),
                version_path.stem + (" / SELECTED" if version_path.name == SELECTED[name] else ""),
                font=font, fill="black",
            )
        comparison.save(qa / f"{name}_versions.jpg", quality=94)
    contact.save(qa / "contact_sheet.jpg", quality=95)
    safe_sheet.save(qa / "crop70_contact_sheet.jpg", quality=95)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "assets" / "img")
    parser.add_argument("--qa-dir", type=Path, default=HERE / "qa")
    parser.add_argument("--skip-previews", action="store_true")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((HERE / "generation.json").read_text(encoding="utf-8"))
    statistics = {}
    for index, name in enumerate(SUBJECTS):
        raw_path = RAW / SELECTED[name]
        source = next(r for r in manifest["records"]
                      if r["id"] == raw_path.stem)
        # 在原始路径仍存在时，同时核对复制件，防止将缩略图误当原图。
        original = Path(source["source"])
        if original.exists():
            assert sha(raw_path.read_bytes()) == sha(original.read_bytes())
        mask, processing = print_mask(raw_path, name)
        ink = transparent_ink(mask)
        paper, paper_stats = paper_print(mask, index)
        paths = (args.out_dir / f"{name}_ink.png",
                 args.out_dir / f"{name}_paper.png")
        hashes = {}
        for image, path in zip((ink, paper), paths):
            data = png_bytes(image)
            path.write_bytes(data)
            hashes[path.name] = {"sha256": sha(data), "bytes": len(data)}
        box = final_box(ESSENTIAL_BOXES[name], processing)
        validation = validate_pair(name, *paths, box)
        statistics[name] = {
            "selected_raw": SELECTED[name],
            "raw_sha256": sha(raw_path.read_bytes()),
            "processing": processing,
            "paper_print": paper_stats,
            "validation": validation,
            "outputs": hashes,
        }
        print(f"PASS {name}: RGBA 2560x1440 + RGB 1920x1080; "
              f"alpha=0/255; crop-safe; black={processing['ink_fraction_of_canvas']:.2%}")
    report = {
        "all_numeric_checks_pass": True,
        "visual_review": "See REVIEW.md; not inferred from pixel tests.",
        "generated_original_count": len(manifest["records"]),
        "delivered_png_count": len(statistics) * 2,
        "environment": {
            "python": platform.python_version(),
            "Pillow": PIL.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "settings": {
            "master_size": MASTER_SIZE, "paper_size": PAPER_SIZE,
            "plate_scale": PLATE_SCALE, "threshold": THRESHOLD,
            "minimum_black_component_area": MIN_COMPONENT_AREA,
            "ink": "#1C1A17", "paper": "#EDE5D4",
        },
        "subjects": statistics,
    }
    (args.qa_dir / "validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not args.skip_previews:
        previews(args.out_dir, args.qa_dir, statistics)


if __name__ == "__main__":
    main()
