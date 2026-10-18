#!/usr/bin/env python3
"""Fetch the public GitHub avatar and prepare a high-contrast grayscale source."""
from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageOps

USERNAME = "rajaryan1111"
PROFILE_API = f"https://api.github.com/users/{USERNAME}"
OUT = Path("data/source-prepped.png")


def get_source(source: str | None) -> Image.Image:
    if source:
        path = Path(source)
        if path.exists():
            return Image.open(path).convert("RGBA")
        response = requests.get(source, headers={"User-Agent": "profile-art-generator/1.0"}, timeout=30)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert("RGBA")
    profile = requests.get(PROFILE_API, headers={"User-Agent": "profile-art-generator/1.0"}, timeout=30)
    profile.raise_for_status()
    avatar_url = profile.json().get("avatar_url")
    if not avatar_url:
        raise RuntimeError("GitHub profile API did not return an avatar URL.")
    image = requests.get(avatar_url, headers={"User-Agent": "profile-art-generator/1.0"}, timeout=30)
    image.raise_for_status()
    return Image.open(BytesIO(image.content)).convert("RGBA")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", nargs="?", help="Optional local photo path or image URL; defaults to the public GitHub avatar.")
    parser.add_argument("--output", default=str(OUT))
    args = parser.parse_args()
    image = get_source(args.source)
    image.thumbnail((900, 900), Image.Resampling.LANCZOS)

    # Prefer background removal when rembg is available. If the model cannot load,
    # retain the original avatar and continue with contrast enhancement.
    try:
        from rembg import remove
        image = remove(image)
    except Exception as exc:
        print(f"Background removal unavailable; using avatar background as-is ({type(exc).__name__}).")

    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image.convert("RGBA"))
    gray = ImageOps.grayscale(background.convert("RGB"))
    try:
        import cv2
        array = np.asarray(gray)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(array)
        gray = Image.fromarray(enhanced)
    except Exception:
        gray = ImageOps.autocontrast(gray, cutoff=1)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    gray.save(output)
    print(f"Prepared {output} ({gray.width}x{gray.height}).")


if __name__ == "__main__":
    main()
