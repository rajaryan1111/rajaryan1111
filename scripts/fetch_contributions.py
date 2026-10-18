#!/usr/bin/env python3
"""Fetch GitHub's public contribution calendar without a token."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "rajaryan1111"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")
HEADERS = {"User-Agent": "rajaryan1111-profile-art/1.0", "Accept": "text/html"}
COUNT_RE = re.compile(r"(\d[\d,]*)\s+contributions?", re.IGNORECASE)


def parse_count(cell) -> int:
    """Read the count from GitHub's accessible labels/title; never guess from color."""
    candidates: list[str] = []
    for node in [cell, *cell.find_all(True)]:
        for key in ("aria-label", "data-aria-label", "title"):
            value = node.get(key)
            if value:
                candidates.append(str(value))
    joined = " ".join(candidates)
    if re.search(r"\bno contributions?\b", joined, re.IGNORECASE):
        return 0
    match = COUNT_RE.search(joined)
    if match:
        return int(match.group(1).replace(",", ""))
    # A zero-level cell is not enough evidence to infer a count, and a nonzero
    # cell without an accessible count should fail the refresh rather than lie.
    level = str(cell.get("data-level", "0"))
    if level == "0":
        return 0
    raise ValueError(f"Could not parse contribution count from cell {cell.get('data-date')}: {joined!r}")


def streaks(days: list[dict]) -> tuple[int, int]:
    counted = {date.fromisoformat(str(item["date"])): int(item["count"]) for item in days}
    today = datetime.now(timezone.utc).date()
    current = 0
    cursor = today
    if counted.get(cursor, 0) == 0 and counted.get(cursor - timedelta(days=1), 0) > 0:
        cursor -= timedelta(days=1)
    while counted.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    longest = run = 0
    previous = None
    for day in sorted(counted):
        if counted[day] > 0:
            run = run + 1 if previous == day - timedelta(days=1) else 1
            longest = max(longest, run)
        else:
            run = 0
        previous = day
    return current, longest


def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("[data-date][data-level]")
    parsed: dict[str, dict] = {}
    for cell in cells:
        raw_date = cell.get("data-date", "")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            continue
        level_raw = cell.get("data-level", "0")
        if not str(level_raw).isdigit():
            raise ValueError(f"Invalid contribution level for {raw_date}: {level_raw!r}")
        level = max(0, min(5, int(level_raw)))
        parsed[raw_date] = {"date": raw_date, "level": level, "count": parse_count(cell)}
    days = [parsed[key] for key in sorted(parsed)]
    if len(days) < 350:
        raise RuntimeError(f"Expected a full public contribution calendar, parsed only {len(days)} days from {URL}")
    if not any(int(day["count"]) > 0 for day in days) and any(int(day["level"]) > 0 for day in days):
        raise RuntimeError("GitHub returned colored contribution cells but no readable counts; refusing to publish false totals.")

    current_streak, longest_streak = streaks(days)
    monthly: dict[str, int] = defaultdict(int)
    for item in days:
        monthly[str(item["date"])[:7]] += int(item["count"])
    best = max(days, key=lambda item: int(item["count"]))
    total = sum(int(item["count"]) for item in days[-365:])
    payload = {
        "username": USERNAME,
        "source": URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": {"date": best["date"], "count": int(best["count"])},
        "monthly_totals": dict(sorted(monthly.items())),
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(days)} days and {total} contributions to {OUT}")


if __name__ == "__main__":
    main()
