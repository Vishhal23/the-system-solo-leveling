"""
THE SYSTEM — Leveling Engine Tests
════════════════════════════════════
Unit tests for XP formulas, level-up logic,
and rank reward tables.
"""

import sys
import os
import math

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.leveling import (
    xp_for_level,
    check_level_up,
    xp_to_next_level,
    xp_progress_pct,
    RANK_XP,
    RANK_STATS,
)


class TestXPFormula:
    """Tests for xp_for_level()."""

    def test_level_1(self):
        assert xp_for_level(1) == 100

    def test_level_5(self):
        # 100 * 5^1.5 = 100 * 11.18 = 1118
        expected = int(100 * math.pow(5, 1.5))
        assert xp_for_level(5) == expected

    def test_level_10(self):
        expected = int(100 * math.pow(10, 1.5))
        assert xp_for_level(10) == expected

    def test_level_20(self):
        expected = int(100 * math.pow(20, 1.5))
        assert xp_for_level(20) == expected

    def test_monotonically_increasing(self):
        """Higher levels should always require more XP."""
        for lvl in range(1, 100):
            assert xp_for_level(lvl + 1) > xp_for_level(lvl)


class TestLevelUp:
    """Tests for check_level_up()."""

    def test_no_level_up(self):
        # Level 1 requires 100 XP. With 50 XP, no level-up.
        new_level, leveled_up = check_level_up(50, 1)
        assert new_level == 1
        assert leveled_up is False

    def test_exact_level_up(self):
        # Exactly 100 XP at level 1 should push to level 2.
        new_level, leveled_up = check_level_up(100, 1)
        assert new_level == 2
        assert leveled_up is True

    def test_multi_level_up(self):
        # Huge XP dump should skip multiple levels.
        new_level, leveled_up = check_level_up(10000, 1)
        assert new_level > 3
        assert leveled_up is True

    def test_level_preserved_when_no_change(self):
        # Already at level 5 with just enough XP to be there, no surplus.
        cumulative = sum(xp_for_level(i) for i in range(1, 5))
        new_level, leveled_up = check_level_up(cumulative, 5)
        assert new_level == 5
        assert leveled_up is False

    def test_level_up_from_high_level(self):
        # At level 10 with enough XP to be at 11.
        cumulative_to_10 = sum(xp_for_level(i) for i in range(1, 10))
        total_xp = cumulative_to_10 + xp_for_level(10) + 1
        new_level, leveled_up = check_level_up(total_xp, 10)
        assert new_level == 11
        assert leveled_up is True


class TestXPProgress:
    """Tests for xp_to_next_level() and xp_progress_pct()."""

    def test_fresh_start(self):
        current, needed = xp_to_next_level(0, 1)
        assert current == 0
        assert needed == 100

    def test_half_progress(self):
        current, needed = xp_to_next_level(50, 1)
        assert current == 50
        assert needed == 100

    def test_progress_pct_zero(self):
        pct = xp_progress_pct(0, 1)
        assert pct == 0.0

    def test_progress_pct_half(self):
        pct = xp_progress_pct(50, 1)
        assert abs(pct - 0.5) < 0.01

    def test_progress_pct_capped(self):
        pct = xp_progress_pct(999999, 1)
        assert pct <= 1.0


class TestRankTables:
    """Tests for rank reward tables."""

    def test_all_ranks_have_xp(self):
        for rank in ["E", "D", "C", "B", "A", "S"]:
            assert rank in RANK_XP
            assert RANK_XP[rank] > 0

    def test_all_ranks_have_stats(self):
        for rank in ["E", "D", "C", "B", "A", "S"]:
            assert rank in RANK_STATS
            assert RANK_STATS[rank] > 0

    def test_xp_increases_with_rank(self):
        ranks = ["E", "D", "C", "B", "A", "S"]
        for i in range(len(ranks) - 1):
            assert RANK_XP[ranks[i]] < RANK_XP[ranks[i + 1]]

    def test_stats_increase_with_rank(self):
        ranks = ["E", "D", "C", "B", "A", "S"]
        for i in range(len(ranks) - 1):
            assert RANK_STATS[ranks[i]] < RANK_STATS[ranks[i + 1]]


# ── Run with: python -m pytest tests/test_leveling.py -v ──
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
