#!/usr/bin/env python3
"""Convert the prepared avatar into a row-by-row animated monochrome SVG."""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

from PIL import Image, ImageOps

RAMP = " .`:-=+*cs#%@"
DEFAULT_INPUT = Path("data/source-prepped.png")
DEFAULT_OUTPUT = Path("assets/avi-ascii.svg")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--columns", type=int, default=100)
    parser.add_argument("--rows", type=int, default=53)
    args = parser.parse_args()
    if args.columns < 20 or args.rows < 10:
        raise ValueError("Use at least a 20x10 character grid for a readable portrait.")
    image = ImageOps.fit(Image.open(args.input).convert("L"), (args.columns, args.rows), method=Image.Resampling.LANCZOS)
    pixels = list(image.getdata())
    lines = []
    for row in range(args.rows):
        chars = []
        for col in range(args.columns):
            brightness = pixels[row * args.columns + col]
            # Bright pixels use sparse glyphs; dark pixels use dense glyphs.
            index = round((255 - brightness) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[index])
        lines.append("".join(chars))

    width, height = 370, 320
    font_size = min(5.4, (width - 8) / (args.columns * 0.602))
    line_height = (height - 22) / args.rows
    row_markup = []
    for i, line in enumerate(lines):
        y = 16 + (i + 1) * line_height
        row_markup.append(
            f'<clipPath id="row{i}"><rect x="4" y="{y-line_height:.2f}" width="0" height="{line_height+1:.2f}">'
            f'<animate attributeName="width" from="0" to="{width-8}" dur="0.72s" begin="{i*0.075:.3f}s" fill="freeze" /></rect></clipPath>'
        )
    text_rows = []
    for i, line in enumerate(lines):
        y = 16 + (i + 1) * line_height
        text_rows.append(
            f'<text class="ascii" x="4" y="{y:.2f}" clip-path="url(#row{i})">{escape(line)}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">Animated ASCII portrait of Raj Aryan</title>
<desc id="desc">A monochrome ASCII portrait generated from the public GitHub avatar. Each row wipes in from left to right, top to bottom, and then freezes.</desc>
<rect x="1" y="1" width="368" height="318" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="2"/>
<path d="M1 35H369" stroke="#30363d"/>
<circle cx="16" cy="18" r="4" fill="#ff6b6b"/><circle cx="29" cy="18" r="4" fill="#ffd166"/><circle cx="42" cy="18" r="4" fill="#06d6a0"/>
<text x="58" y="22" fill="#8b949e" font-size="10" font-family="monospace">rajaryan@github: ~/avatar</text>
<defs><style>.ascii{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:{font_size:.2f}px;fill:#c9d1d9;white-space:pre}}@media(prefers-reduced-motion:reduce){{.ascii{{clip-path:none}}}}</style>{''.join(row_markup)}</defs>
{''.join(text_rows)}
</svg>
'''
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(svg, encoding="utf-8")
    print(f"Wrote {output} from a {args.columns}x{args.rows} character grid.")


if __name__ == "__main__":
    main()
