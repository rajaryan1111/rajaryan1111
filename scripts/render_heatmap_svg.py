#!/usr/bin/env python3
"""Render GitHub's public contribution activity as a self-animating SVG."""
from __future__ import annotations

import json
from datetime import date
from html import escape
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def counts_are_available(days: list[dict]) -> bool:
    """Return true only when every day has a verified integer count."""
    return bool(days) and all(
        isinstance(item.get("count"), int) and not isinstance(item.get("count"), bool)
        for item in days
    )


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    all_days = payload.get("days", [])
    if len(all_days) < 350:
        raise RuntimeError("Contribution data is incomplete; refusing to render a misleading heatmap.")
    # GitHub's calendar is a rolling year; trim to the latest 365 days.
    days = all_days[-365:]
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday-first, as on GitHub
    has_counts = counts_are_available(days)
    cells: list[str] = []
    for index, item in enumerate(days):
        day = date.fromisoformat(item["date"])
        slot = index + offset
        col, row = slot // 7, slot % 7
        level = max(0, min(5, int(item.get("level", 0))))
        x, y = 18 + col * 15, 62 + row * 12
        delay = min(5.0, col * 0.035 + row * 0.055)
        count = item.get("count")
        if has_counts:
            title = escape(f'{day.isoformat()}: {int(count)} contribution{"s" if int(count) != 1 else ""}')
        else:
            title = escape(f"{day.isoformat()}: activity level {level}; contribution count unavailable")
        cells.append(
            f'<rect class="day" x="{x}" y="{y}" width="10" height="8" rx="2" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay:.3f}s"><title>{title}</title></rect>'
        )

    updated = escape(str(payload.get("updated_at", "unknown"))[:10])
    username = escape(str(payload.get("username", "GitHub user")))
    if has_counts:
        total = sum(int(day["count"]) for day in days)
        current = int(payload.get("current_streak") or 0)
        longest = int(payload.get("longest_streak") or 0)
        best = payload.get("best_day") or {}
        best_label = escape(str(best.get("date", "unknown")) + " (" + str(int(best.get("count", 0))) + ")")
        month_key = date.today().strftime("%Y-%m")
        month_total = int(payload.get("monthly_totals", {}).get(month_key, 0))
        summary = f"{total:,} contributions · streak {current}d · longest {longest}d · best {best_label} · this month {month_total} · updated {updated}"
        desc = f"A 53-week contribution grid generated from GitHub's public contribution calendar. {total} contributions reported for the available calendar."
    else:
        summary = f"Activity intensity from public GitHub calendar · contribution counts awaiting refresh · snapshot {updated}"
        desc = "A contribution activity grid generated from GitHub's public calendar. Cell intensity is available, but contribution counts have not been verified in this snapshot."

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="860" height="170" viewBox="0 0 860 170" role="img" aria-labelledby="title desc">
<title id="title">GitHub contribution calendar for {username}</title>
<desc id="desc">{escape(desc)}</desc>
<defs><style>.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.day{{opacity:0;animation:reveal .45s ease-out both}}@keyframes reveal{{from{{opacity:0;transform:translateY(-5px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.day{{animation:none;opacity:1}}}}</style></defs>
<rect x="1" y="1" width="858" height="168" rx="10" fill="#0d1117" stroke="#30363d" stroke-width="2"/>
<text x="18" y="24" fill="#7ee787" font-size="12" class="mono">$ git log --contributions --last-year</text>
<text x="18" y="45" fill="#8b949e" font-size="10" class="mono">{escape(summary)}</text>
{''.join(cells)}
<text x="18" y="157" fill="#8b949e" font-size="10" class="mono">Less</text>
{''.join(f'<rect x="{54+i*13}" y="149" width="10" height="8" rx="2" fill="{color}"/>' for i,color in enumerate(PALETTE))}
<text x="137" y="157" fill="#8b949e" font-size="10" class="mono">More</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Rendered {len(cells)} contribution cells to {OUT}; verified counts: {has_counts}")


if __name__ == "__main__":
    main()
