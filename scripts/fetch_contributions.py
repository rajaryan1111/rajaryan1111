#!/usr/bin/env python3
"""Fetch public contribution-day metadata from the user's GitHub profile without a token."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from html.parser import HTMLParser

USERNAME = "rajaryan1111"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path("data/contributions.json")


class ContributionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.days: list[dict[str, object]] = []
        self._capture = False
        self._attrs: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {k: v or "" for k, v in attrs}
        if tag == "td" and ("data-date" in values or "ContributionCalendar-day" in values.get("class", "")):
            self._capture = True
            self._attrs = values

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._attrs.setdefault("title", "")
            self._attrs["title"] += data.strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._capture:
            date = self._attrs.get("data-date", "")
            level = self._attrs.get("data-level", "0")
            if date and re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                match = re.search(r"(\d+) contribution", self._attrs.get("aria-label", "") + " " + self._attrs.get("title", ""), re.I)
                count = int(match.group(1)) if match else 0
                self.days.append({"date": date, "level": max(0, min(4, int(level) if level.isdigit() else 0)), "count": count})
            self._capture = False
            self._attrs = {}


def main() -> None:
    request = Request(URL, headers={"User-Agent": "rajaryan1111-profile-art/1.0", "Accept": "text/html"})
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = ContributionParser()
    parser.feed(html)
    unique = {str(day["date"]): day for day in parser.days}
    days = sorted(unique.values(), key=lambda item: str(item["date"]))
    if len(days) < 300:
        raise RuntimeError(f"Expected a public contribution calendar, parsed only {len(days)} days from {URL}")
    total = sum(int(day["count"]) for day in days)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "username": USERNAME,
        "source": URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total,
        "days": days,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(days)} contribution days ({total} contributions) to {OUT}")


if __name__ == "__main__":
    main()
