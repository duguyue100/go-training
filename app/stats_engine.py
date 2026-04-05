"""
Statistics engine: compute per-game statistics from parsed comments.
Mirrors KaTrain's game_report() logic as closely as possible.
"""

import math

from app.comment_parser import ParsedComment

# KaTrain's default evaluation thresholds (from config.json)
EVAL_THRESHOLDS = [12, 6, 3, 1.5, 0.5, 0]

# KaTrain phase boundaries as board fractions (from popups.kv)
# boundary_move = ceil(fraction * boardW * boardH)
PHASE_FRACTIONS = {
    "opening": (0.0, 0.14),
    "midgame": (0.14, 0.40),
    "endgame": (0.40, 1e9),
}

# Minimum human moves required in a phase to report a meaningful value
PHASE_MIN_MOVES = 5


def evaluation_class(
    points_lost: float, thresholds: list[float] = EVAL_THRESHOLDS
) -> int:
    """
    Mirrors katrain.core.utils.evaluation_class exactly.
    Returns index: 0 = worst (>= highest threshold), len-1 = best (< lowest nonzero).

    With default thresholds [12, 6, 3, 1.5, 0.5, 0]:
      >= 12    → 0 (Critical)
      >= 6     → 1 (Blunder)
      >= 3     → 2 (Mistake)
      >= 1.5   → 3 (Inaccuracy)
      >= 0.5   → 4 (Good)
      < 0.5    → 5 (Excellent)
    """
    i = 0
    while i < len(thresholds) - 1 and points_lost < thresholds[i]:
        i += 1
    return i


def phase_boundaries(board_size: tuple[int, int]) -> dict[str, tuple[int, int]]:
    """
    Convert KaTrain's board-fraction phase definitions to absolute move-number ranges.
    Uses ceil(fraction * boardW * boardH) exactly as KaTrain does.

    Returns dict: phase_name → (start_move_inclusive, end_move_exclusive)
    Move numbers are 1-based (first move = move 1).
    """
    bw, bh = board_size
    squares = bw * bh
    bounds = {}
    for name, (lo, hi) in PHASE_FRACTIONS.items():
        start = math.ceil(lo * squares) + 1  # convert to 1-based
        end = math.ceil(hi * squares) + 1 if hi < 1e8 else 10_000
        bounds[name] = (start, end)
    return bounds


def _stddev(values: list[float]) -> float | None:
    """Population standard deviation, None if fewer than 2 values."""
    n = len(values)
    if n < 2:
        return None
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    return math.sqrt(variance)


def compute_game_stats(
    human_comments: list[ParsedComment],
    board_size: tuple[int, int] = (19, 19),
) -> dict:
    """
    Compute aggregate statistics for the human player's moves.

    Parameters:
        human_comments:   ParsedComment list for the human player's moves only.
                          Moves without analysis (score=None) are excluded.
        board_size:       (width, height) used for phase boundary computation.

    Returns dict with keys:
        mean_points_lost, max_points_lost, stddev_points_lost,
        best_move_rate, good_move_rate, histogram,
        avg_policy_rank, top1_policy_rate, top5_policy_rate,
        phase_opening_pts_lost, phase_midgame_pts_lost, phase_endgame_pts_lost,
        opening_avg_policy_rank
    """
    # Filter to moves that have analysis data
    analyzed = [c for c in human_comments if c.score is not None]

    if not analyzed:
        return _empty_stats()

    # Points lost values (clamped to >= 0, matching KaTrain's max(0, points_lost))
    pts_lost_values = [max(0.0, c.points_lost) for c in analyzed]

    # --- Mean points lost (exact match to KaTrain) ---
    mean_ptloss = sum(pts_lost_values) / len(pts_lost_values)

    # --- Max points lost ---
    max_ptloss = max(pts_lost_values) if pts_lost_values else 0.0

    # --- Best move rate (= KaTrain's ai_top_move) ---
    best_count = sum(1 for c in analyzed if c.is_best_move)
    best_move_rate = best_count / len(analyzed)

    # --- Good move rate (points_lost < 1.0) ---
    good_count = sum(1 for c in analyzed if c.points_lost < 1.0)
    good_move_rate = good_count / len(analyzed)

    # --- Histogram (6 buckets matching KaTrain thresholds) ---
    # KaTrain uses: bucket = len(thresholds) - 1 - evaluation_class(pts_lost)
    # bucket 0 = best (Excellent), bucket 5 = worst (Critical)
    histogram = [0] * len(EVAL_THRESHOLDS)
    for pts in pts_lost_values:
        eval_cls = evaluation_class(pts)
        bucket = len(EVAL_THRESHOLDS) - 1 - eval_cls
        histogram[bucket] += 1

    # --- Policy statistics ---
    policy_ranks = [c.policy_rank for c in analyzed if c.policy_rank is not None]
    avg_policy_rank = (sum(policy_ranks) / len(policy_ranks)) if policy_ranks else None
    top1_count = sum(1 for r in policy_ranks if r == 1)
    top1_policy_rate = (top1_count / len(policy_ranks)) if policy_ranks else None
    top5_count = sum(1 for r in policy_ranks if r <= 5)
    top5_policy_rate = (top5_count / len(policy_ranks)) if policy_ranks else None

    # --- Std-dev of points lost (consistency within a game) ---
    stddev_points_lost = _stddev(pts_lost_values)

    # --- Phase breakdown ---
    bounds = phase_boundaries(board_size)

    def _phase_ptloss(phase_name: str) -> float | None:
        start, end = bounds[phase_name]
        phase_pts = [
            max(0.0, c.points_lost) for c in analyzed if start <= c.move_number < end
        ]
        if len(phase_pts) < PHASE_MIN_MOVES:
            return None
        return round(sum(phase_pts) / len(phase_pts), 2)

    phase_opening_pts_lost = _phase_ptloss("opening")
    phase_midgame_pts_lost = _phase_ptloss("midgame")
    phase_endgame_pts_lost = _phase_ptloss("endgame")

    # --- Opening policy rank ---
    op_start, op_end = bounds["opening"]
    opening_policy_ranks = [
        c.policy_rank
        for c in analyzed
        if op_start <= c.move_number < op_end and c.policy_rank is not None
    ]
    opening_avg_policy_rank = (
        round(sum(opening_policy_ranks) / len(opening_policy_ranks), 1)
        if opening_policy_ranks
        else None
    )

    return {
        "mean_points_lost": round(mean_ptloss, 2),
        "max_points_lost": round(max_ptloss, 1),
        "stddev_points_lost": round(stddev_points_lost, 2)
        if stddev_points_lost is not None
        else None,
        "best_move_rate": round(best_move_rate, 3),
        "good_move_rate": round(good_move_rate, 3),
        "histogram": histogram,
        "avg_policy_rank": round(avg_policy_rank, 1)
        if avg_policy_rank is not None
        else None,
        "top1_policy_rate": round(top1_policy_rate, 3)
        if top1_policy_rate is not None
        else None,
        "top5_policy_rate": round(top5_policy_rate, 3)
        if top5_policy_rate is not None
        else None,
        "phase_opening_pts_lost": phase_opening_pts_lost,
        "phase_midgame_pts_lost": phase_midgame_pts_lost,
        "phase_endgame_pts_lost": phase_endgame_pts_lost,
        "opening_avg_policy_rank": opening_avg_policy_rank,
    }


def _empty_stats() -> dict:
    return {
        "mean_points_lost": 0.0,
        "max_points_lost": 0.0,
        "stddev_points_lost": None,
        "best_move_rate": 0.0,
        "good_move_rate": 0.0,
        "histogram": [0] * len(EVAL_THRESHOLDS),
        "avg_policy_rank": None,
        "top1_policy_rate": None,
        "top5_policy_rate": None,
        "phase_opening_pts_lost": None,
        "phase_midgame_pts_lost": None,
        "phase_endgame_pts_lost": None,
        "opening_avg_policy_rank": None,
    }
