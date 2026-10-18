from datetime import datetime, timedelta, timezone
import unittest

from bs4 import BeautifulSoup

from scripts.fetch_contributions import parse_count, streaks


class ContributionParsingTests(unittest.TestCase):
    def test_reads_accessible_data_aria_label(self):
        cell = BeautifulSoup(
            '<td data-date="2026-10-18" data-level="4" data-aria-label="12 contributions on Oct 18, 2026"></td>',
            "html.parser",
        ).select_one("td")
        self.assertEqual(parse_count(cell), 12)

    def test_reads_nested_tooltip_label(self):
        cell = BeautifulSoup(
            '<td data-date="2026-10-18" data-level="2"><tool-tip aria-label="3 contributions on Oct 18, 2026"></tool-tip></td>',
            "html.parser",
        ).select_one("td")
        self.assertEqual(parse_count(cell), 3)

    def test_zero_level_cell_is_zero(self):
        cell = BeautifulSoup('<td data-date="2026-10-18" data-level="0"></td>', "html.parser").select_one("td")
        self.assertEqual(parse_count(cell), 0)

    def test_nonzero_cell_without_count_fails_closed(self):
        cell = BeautifulSoup('<td data-date="2026-10-18" data-level="3"></td>', "html.parser").select_one("td")
        with self.assertRaises(ValueError):
            parse_count(cell)

    def test_streak_stats(self):
        today = datetime.now(timezone.utc).date()
        days = [
            {"date": (today - timedelta(days=4)).isoformat(), "count": 1},
            {"date": (today - timedelta(days=3)).isoformat(), "count": 1},
            {"date": (today - timedelta(days=2)).isoformat(), "count": 0},
            {"date": (today - timedelta(days=1)).isoformat(), "count": 1},
            {"date": today.isoformat(), "count": 1},
        ]
        self.assertEqual(streaks(days), (2, 2))


if __name__ == "__main__":
    unittest.main()
