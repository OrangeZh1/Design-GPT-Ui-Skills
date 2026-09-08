#!/usr/bin/env python3
"""Normalize generated images to an exact delivery size.

Default behavior is cover-resize plus center crop, which preserves full-frame UI
mockups better than arbitrary stretching.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def parse_size(raw: str) -> tuple[int, int]:
    try:
        width_raw, height_raw = raw.lower().split("x", 1)
        width = int(width_raw)
        height = int(height_raw)
    except Exception as exc:  # noqa: BLE001
        raise argparse.ArgumentTypeError("size must be WIDTHxHEIGHT") from exc
    if width <= 0 or height <= 0:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return width, height


def normalize_cover_crop(image: Image.Image, target: tuple[int, int]) -> Image.Image:
    target_w, target_h = target
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    resized_w = round(src_w * scale)
    resized_h = round(src_h * scale)
    resized = image.resize((resized_w, resized_h), Image.Resampling.LANCZOS)

    left = max(0, (resized_w - target_w) // 2)
    top = max(0, (resized_h - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h))


def normalize_stretch(image: Image.Image, target: tuple[int, int]) -> Image.Image:
    return image.resize(target, Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Source generated image")
    parser.add_argument("--out", required=True, help="Normalized output image")
    parser.add_argument("--size", required=True, type=parse_size, help="Delivery size, e.g. 750x1624")
    parser.add_argument(
        "--mode",
        choices=["cover-crop", "stretch"],
        default="cover-crop",
        help="Normalization mode",
    )
    args = parser.parse_args()

    src = Path(args.input)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(src) as image:
        image = image.convert("RGBA")
        if args.mode == "stretch":
            normalized = normalize_stretch(image, args.size)
        else:
            normalized = normalize_cover_crop(image, args.size)
        normalized.save(out)

    print(f"normalized {src} -> {out} ({args.size[0]}x{args.size[1]})")


if __name__ == "__main__":
    main()
