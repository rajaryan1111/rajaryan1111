#!/usr/bin/env python3
"""Render the fetched GitHub contribution calendar as a self-animating SVG."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    days = payload.get("days", [])
    if len(days) < 300:
        raise RuntimeError("Contribution data is incomplete; refusing to render a misleading heatmap.")
    # Align the oldest date to its weekday, then render one column per calendar week.
    first = date.fromisoformat(days[0]["date"])
    start_offset = (first.weekday() + 1) % 7  # Sunday-first, matching GitHub
    cells = []
    for index, item in enumerate(days):
        day = date.fromisoformat(item["date"])
        slot = index + start_offset
        col, row = slot // 7, slot % 7
        level = max(0, min(4, int(item.get("level", 0))))
        x, y = 18 + col * 15, 58 + row * 12
        delay = min(4.5, col * 0.045 + row * 0.06)
        title = f'{item["date"]}: {int(item.get("count", 0))} contributions'
        cells.append(f'<rect class="day" x="{x}" y="{y}" width="10" height="8" rx="2" fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"><title>{escape(title)}</title></rect>')
    total = int(payload.get("total_contributions", sum(int(d.get("count", 0)) for d in days)))
    updated = escape(str(payload.get("updated_at", "unknown"))[:10])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="155" viewBox="0 0 860 155" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution calendar for {escape(payload.get("username", "GitHub user"))}</title>
<desc id="desc">A 53-week contribution grid generated from public GitHub contribution data. {total} contributions reported by the source calendar.</desc>
<defs><style>.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.day{{animation:reveal .5s ease-out both}}@keyframes reveal{{from{{opacity:0;transform:translateY(-5px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.day{{animation:none}}}}</style></defs>
<rect x="1" y="1" width="858" height="153" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="2"/>
<text x="18" y="24" fill="#7ee787" font-size="12" class="mono">$ git log --contributions --last-year</text>
<text x="18" y="46" fill="#8b949e" font-size="10" class="mono">{total:,} contributions · source: github.com/users/{escape(payload.get("username", ""))}/contributions · updated {updated}</text>
{''.join(cells)}
<text x="18" y="145" fill="#8b949e" font-size="10" class="mono">Less</text>
{''.join(f'<rect x="{54+i*13}" y="137" width="10" height="8" rx="2" fill="{color}"/>' for i,color in enumerate(PALETTE))}
<text x="123" y="145" fill="#8b949e" font-size="10" class="mono">More</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Rendered {len(cells)} contribution cells to {OUT}")


if __name__ == "__main__":
    main()
