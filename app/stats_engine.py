"""
Statistics engine: compute per-game statistics from parsed comments.
Mirrors KaTrain's game_report() logic as closely as possible.
"""

from app.comment_parser import ParsedComment

# KaTrain's default evaluation thresholds (from config.json)
EVAL_THRESHOLDS = [12, 6, 3, 1.5, 0.5, 0]


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


def compute_game_stats(human_comments: list[ParsedComment]) -> dict:
    """
    Compute aggregate statistics for the human player's moves.

    This mirrors KaTrain's game_report() output structure.

    Parameters:
        human_comments: List of ParsedComment for the human player's moves only.
                       Moves without analysis (score=None) are excluded.

    Returns dict with keys:
        mean_points_lost, max_points_lost, accuracy,
        best_move_rate, good_move_rate, histogram,
        avg_policy_rank, top1_policy_rate
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

    # --- Accuracy (approximation: uniform weights) ---
    # KaTrain: accuracy = 100 * 0.75 ^ weighted_ptloss
    # We use: accuracy = 100 * 0.75 ^ mean_ptloss (since we lack complexity weights)
    accuracy = 100.0 * (0.75**mean_ptloss)

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

    return {
        "mean_points_lost": round(mean_ptloss, 2),
        "max_points_lost": round(max_ptloss, 1),
        "accuracy": round(accuracy, 1),
        "best_move_rate": round(best_move_rate, 3),
        "good_move_rate": round(good_move_rate, 3),
        "histogram": histogram,
        "avg_policy_rank": round(avg_policy_rank, 1)
        if avg_policy_rank is not None
        else None,
        "top1_policy_rate": round(top1_policy_rate, 3)
        if top1_policy_rate is not None
        else None,
    }


def _empty_stats() -> dict:
    return {
        "mean_points_lost": 0.0,
        "max_points_lost": 0.0,
        "accuracy": 100.0,
        "best_move_rate": 0.0,
        "good_move_rate": 0.0,
        "histogram": [0] * len(EVAL_THRESHOLDS),
        "avg_policy_rank": None,
        "top1_policy_rate": None,
    }
