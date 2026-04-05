"""
Pydantic models for API responses.
"""

from pydantic import BaseModel
from datetime import datetime


class UndoEvent(BaseModel):
    move_number: int
    player: str
    coordinate: str
    points_lost: float
    best_move_coord: str | None = None


class GameSummary(BaseModel):
    # Metadata
    filename: str
    date: datetime
    board_size: list[int]  # [19, 19]
    komi: float
    ruleset: str
    human_player: str  # "B" or "W"
    human_name: str
    ai_name: str
    ai_rank: str | None = None
    game_mode: str  # "teaching" | "even" | "ranked" | "unknown"
    total_moves: int
    sgf_language: str  # "cn" | "en" | "tw"

    # Computed statistics (human player only)
    mean_points_lost: float
    max_points_lost: float
    stddev_points_lost: float | None = None  # population std-dev of per-move pts lost
    best_move_rate: float  # fraction
    good_move_rate: float  # fraction (points_lost < 1.0)

    # Histogram: 6 buckets [excellent, good, inaccuracy, mistake, blunder, critical]
    histogram: list[int]

    # Undo stats
    undo_count: int
    undo_total_points_lost: float

    # Policy stats
    avg_policy_rank: float | None = None
    top1_policy_rate: float | None = None
    top5_policy_rate: float | None = None

    # Phase breakdown (KaTrain boundaries: ceil(fraction × boardW × boardH))
    # None when fewer than 5 human moves fall in that phase
    phase_opening_pts_lost: float | None = (
        None  # fraction [0, 0.14) → moves 0–50 on 19×19
    )
    phase_midgame_pts_lost: float | None = (
        None  # fraction [0.14, 0.40) → moves 51–144 on 19×19
    )
    phase_endgame_pts_lost: float | None = (
        None  # fraction [0.40, ∞)  → moves 145+ on 19×19
    )

    # Opening policy rank: avg policy rank restricted to opening-phase moves
    opening_avg_policy_rank: float | None = None


class MoveCoord(BaseModel):
    """A single move as player + board coordinates for the board renderer."""

    player: str  # "B" or "W"
    col: int  # 0-based, 0 = left (A)
    row: int  # 0-based, 0 = bottom (1)
    is_pass: bool = False


class GameDetail(BaseModel):
    """Extended game data for per-game drill-down."""

    summary: GameSummary
    score_trajectory: list[float]  # Score after each main-line move
    winrate_trajectory: list[float]  # Winrate after each main-line move
    move_labels: list[str]  # ["B R16", "W D16", "B Q3", ...]
    move_coords: list[MoveCoord]  # Parsed (col, row) for board rendering
    undo_details: list[UndoEvent]


class TrendData(BaseModel):
    dates: list[str]
    mean_points_lost: list[float]
    stddev_points_lost: list[float | None]
    best_move_rate: list[float]
    top5_policy_rate: list[float | None]
    undo_count: list[int]
    avg_policy_rank: list[float | None]


class OverallStats(BaseModel):
    avg_mean_points_lost: float
    avg_policy_rank: float | None = None
    avg_best_move_rate: float
    total_undos: int


class AggregateStats(BaseModel):
    total_games: int
    date_range: list[str]  # [earliest_date, latest_date]
    trends: TrendData
    overall: OverallStats
