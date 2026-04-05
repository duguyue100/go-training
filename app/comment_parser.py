"""
Bilingual (Chinese/English) KaTrain SGF comment parser.
Handles Simplified Chinese (cn), Traditional Chinese (tw), and English (en).
"""

import re
from dataclasses import dataclass, field


@dataclass
class ParsedComment:
    move_number: int = 0
    player: str = ""  # "B" or "W"
    coordinate: str = ""  # GTP format, e.g., "R16"
    score: float | None = None  # From Black's perspective (positive = Black leads)
    winrate: float | None = None  # From Black's perspective (0.0-100.0)
    points_lost: float = 0.0  # 0 if best move or not shown; parsed value otherwise
    is_best_move: bool = False  # True if best-move marker found
    has_explicit_loss: bool = False  # True if points-lost line was present
    best_move_coord: str | None = None  # Recommended move (when not best)
    policy_rank: int | None = None
    policy_pct: float | None = None
    is_undo: bool = False  # True if auto-undo marker found


def detect_comment_language(comment: str) -> str:
    """Detect SGF comment language. Returns 'cn', 'tw', or 'en'."""
    if "手数" in comment:  # Simplified Chinese: 手数
        return "cn"
    if "手數" in comment:  # Traditional Chinese: 手數
        return "tw"
    if "Move " in comment:
        return "en"
    return "en"  # fallback


# --- Color mapping ---
COLOR_MAP = {"黑": "B", "白": "W", "B": "B", "W": "W"}

# --- Regex patterns ---

# Move identification
# CN: "手数 45: B D4"    TW: "手數 45: B D4"    EN: "Move 45: B D4"
MOVE_PATTERNS = [
    re.compile(r"手[数數]\s*(\d+):\s*([BW])\s+(\w+)"),  # CN/TW
    re.compile(r"Move\s+(\d+):\s*([BW])\s+(\w+)"),  # EN
]

# Score
# CN: "分数: 黑+3.5" / "分数: 白+1.2"
# EN: "Score: B+3.5" / "Score: W+1.2"
SCORE_PATTERNS = [
    re.compile(r"分[数數]:\s*(黑|白)\+?([\d.]+)"),  # CN/TW
    re.compile(r"Score:\s*([BW])\+?([\d.]+)"),  # EN
]

# Winrate
# CN: "胜率: 黑 65.3%"    TW: "勝率: 黑 65.3%"    EN: "Win rate: B 65.3%"
WINRATE_PATTERNS = [
    re.compile(r"[胜勝]率:\s*(黑|白)\s*([\d.]+)%"),  # CN/TW
    re.compile(r"Win rate:\s*([BW])\s*([\d.]+)%"),  # EN
]

# Points lost
# CN: "目数损失: 4.7"    TW: "目數損失: 4.7"    EN: "Estimated point loss: 4.7"
PTLOSS_PATTERNS = [
    re.compile(r"目[数數][损損]失:\s*([\d.]+)"),  # CN/TW
    re.compile(r"Estimated point loss:\s*([\d.]+)"),  # EN
]

# Best move indicators
BEST_MOVE_MARKERS = [
    "该手为最佳选点",  # CN
    "該手為最佳選點",  # TW
    "Move was predicted best move",  # EN
]

# Top move recommendation
# CN: "推荐最佳选点 Q16 (黑+3.5)."
# TW: "預測最佳選點為 Q16 (黑+3.5)."
# EN: "Predicted top move was Q16 (B+3.5)."
TOP_MOVE_PATTERNS = [
    re.compile(r"推荐最佳选点\s+(\w+)"),  # CN
    re.compile(r"預測最佳選點為\s+(\w+)"),  # TW
    re.compile(r"Predicted top move was\s+(\w+)"),  # EN
]

# Policy rank
# CN: "直觉选点下该手棋是 #3 (8.54%)."
# TW: "直覺選點下該手棋是 #3 (8.54%)."
# EN: "Move was #3 according to policy  (8.54%)."
POLICY_RANK_PATTERNS = [
    re.compile(r"直[觉覺]选点下该手棋是\s*#(\d+)\s*\(([\d.]+)%\)"),  # CN
    re.compile(r"直覺選點下該手棋是\s*#(\d+)\s*\(([\d.]+)%\)"),  # TW
    re.compile(r"Move was #(\d+) according to policy\s+\(([\d.]+)%\)"),  # EN
]

# Undo markers
UNDO_MARKERS = [
    "自动悔棋",  # CN
    "自動悔棋",  # TW
    "automatically undone",  # EN
]


def parse_comment(comment: str) -> ParsedComment:
    """
    Parse a KaTrain SGF comment into structured data.
    Handles Chinese (Simplified), Chinese (Traditional), and English.
    Returns ParsedComment with all extracted fields.
    """
    result = ParsedComment()

    # Strip KaTrain internal markers
    comment = comment.replace("\u3164\u200b", "").replace("\u3164\u3164", "\n")

    # Try each pattern group, first match wins
    for pattern in MOVE_PATTERNS:
        m = pattern.search(comment)
        if m:
            result.move_number = int(m.group(1))
            result.player = m.group(2)
            result.coordinate = m.group(3)
            break

    for pattern in SCORE_PATTERNS:
        m = pattern.search(comment)
        if m:
            color = COLOR_MAP.get(m.group(1), m.group(1))
            value = float(m.group(2))
            result.score = value if color == "B" else -value
            break

    for pattern in WINRATE_PATTERNS:
        m = pattern.search(comment)
        if m:
            color = COLOR_MAP.get(m.group(1), m.group(1))
            value = float(m.group(2))
            result.winrate = value if color == "B" else (100.0 - value)
            break

    for pattern in PTLOSS_PATTERNS:
        m = pattern.search(comment)
        if m:
            result.points_lost = float(m.group(1))
            result.has_explicit_loss = True
            break

    result.is_best_move = any(marker in comment for marker in BEST_MOVE_MARKERS)

    # If best move, points_lost is definitively 0
    if result.is_best_move:
        result.points_lost = 0.0

    for pattern in TOP_MOVE_PATTERNS:
        m = pattern.search(comment)
        if m:
            result.best_move_coord = m.group(1)
            break

    for pattern in POLICY_RANK_PATTERNS:
        m = pattern.search(comment)
        if m:
            result.policy_rank = int(m.group(1))
            result.policy_pct = float(m.group(2))
            break

    result.is_undo = any(marker in comment for marker in UNDO_MARKERS)

    return result
