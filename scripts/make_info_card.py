#!/usr/bin/env python3
"""Generate a self-contained, line-by-line animated Neofetch-style SVG."""
from __future__ import annotations

import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("assets/info-card.svg")
ROWS = [
    ("Now", "AI Career Agent · local-first desktop alpha"),
    ("Prev", "AI/ML prototypes · RAG · voice workflows"),
    ("Stack", "Python · TypeScript · React · SQL"),
    ("Tools", "FastAPI · PostgreSQL · Docker · Git"),
    ("Focus", "Agentic AI · LLM apps · computer vision"),
    ("Build", "Tests · evidence · safe defaults"),
]


def main() -> None:
    static = os.getenv("STATIC", "").lower() in {"1", "true", "yes"}
    rows = []
    for i, (key, value) in enumerate(ROWS):
        y = 104 + i * 29
        delay = i * 0.18
        animation = "" if static else f' class="line" style="animation-delay:{delay:.2f}s"'
        rows.append(
            f'<g{animation}><text x="20" y="{y}" fill="#79c0ff" font-size="12" class="mono">{escape(key)}</text>'
            f'<text x="102" y="{y}" fill="#c9d1d9" font-size="11" class="mono">{escape(value)}</text></g>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="490" height="320" viewBox="0 0 490 320" role="img" aria-labelledby="title desc">
<title id="title">Raj Aryan Neofetch-style developer profile</title>
<desc id="desc">Role, current project, previous work themes, technology stack, tools, and engineering principles reveal line by line.</desc>
<defs><style>.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.line{{opacity:0;animation:linein .45s ease-out forwards}}@keyframes linein{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.line{{animation:none;opacity:1}}}}</style></defs>
<rect x="1" y="1" width="488" height="318" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="2"/>
<path d="M1 35H489" stroke="#30363d"/>
<circle cx="16" cy="18" r="4" fill="#ff6b6b"/><circle cx="29" cy="18" r="4" fill="#ffd166"/><circle cx="42" cy="18" r="4" fill="#06d6a0"/>
<text x="58" y="22" fill="#8b949e" font-size="10" class="mono">rajaryan@github: ~</text>
<text x="20" y="61" fill="#7ee787" font-size="12" class="mono">$ neofetch --profile</text>
<text x="20" y="83" fill="#f0f6fc" font-size="16" font-weight="700" class="mono">RAJ ARYAN</text>
<text x="20" y="96" fill="#8b949e" font-size="9" class="mono">AI/ML ENGINEERING · AGENTIC SYSTEMS</text>
{''.join(rows)}
<text x="20" y="296" fill="#7ee787" font-size="11" class="mono">[ profile loaded ]{' ' if static else '<tspan class="cursor">_</tspan>'}</text>
</svg>
'''
    if not static:
        svg = svg.replace(".line{opacity:0;", ".cursor{animation:blink 1s steps(2,start) infinite}@keyframes blink{to{visibility:hidden}}.line{opacity:0;")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT}{' (static preview)' if static else ''}.")


if __name__ == "__main__":
    main()
