"""
SGF parsing orchestration: file → parse → extract comments → compute stats → GameDetail.
"""

from pathlib import Path
from datetime import datetime

from app.sgf_parser import SGF, SGFNode
from app.comment_parser import parse_comment, detect_comment_language, ParsedComment
from app.stats_engine import compute_game_stats
from app.models import GameSummary, GameDetail, MoveCoord, UndoEvent


def parse_sgf_file(filepath: Path) -> GameDetail:
    """
    Parse a single SGF file into a GameDetail (includes summary + trajectories).

    Steps:
    1. Parse SGF tree using vendored sgf_parser
    2. Extract metadata from root node properties
    3. Walk main line, parse each node's comment
    4. Walk branch nodes to find undo events
    5. Compute statistics via stats_engine
    6. Build and return GameDetail
    """
    root = SGF.parse_file(str(filepath))

    # --- Step 1: Extract metadata ---
    pb = _clean_player_name(root.get_property("PB", "Unknown"))
    pw = _clean_player_name(root.get_property("PW", "Unknown"))
    board_size = root.board_size  # (19, 19)
    komi = root.komi  # 6.5
    ruleset = root.get_property("RU", "unknown") or "unknown"
    date_str = root.get_property("DT", "")
    date = _parse_date(date_str)

    # --- Step 2: Detect human player ---
    br_raw = (
        _clean_player_name(root.get_property("BR", None))
        if root.get_property("BR", None)
        else None
    )
    wr_raw = (
        _clean_player_name(root.get_property("WR", None))
        if root.get_property("WR", None)
        else None
    )
    human_player = detect_human_player(pb, pw, br_raw, wr_raw)
    if human_player == "B":
        human_name, ai_name = pb, pw
        ai_rank = wr_raw
        # If both names are identical, the AI name is the rank string
        if pb == pw and ai_rank:
            ai_name = ai_rank
            ai_rank = None
    else:
        human_name, ai_name = pw, pb
        ai_rank = br_raw
        # If both names are identical, the AI name is the rank string
        if pb == pw and ai_rank:
            ai_name = ai_rank
            ai_rank = None

    game_mode = detect_game_mode(human_name)

    # --- Step 3: Walk main line, collect move data ---
    main_line_comments: list[ParsedComment] = []
    score_trajectory: list[float] = []
    winrate_trajectory: list[float] = []
    move_labels: list[str] = []
    move_coords: list[MoveCoord] = []
    sgf_language = "cn"  # default, will be detected from first comment

    node = root
    first_comment_seen = False
    move_counter = 0
    while node.children:
        node = node.children[0]  # Follow main branch (first child)
        comment_text = node.get_property("C", "")

        if comment_text and not first_comment_seen:
            sgf_language = detect_comment_language(comment_text)
            first_comment_seen = True

        # Determine player color from node properties
        node_player = None
        if node.get_property("B", None) is not None:
            node_player = "B"
        elif node.get_property("W", None) is not None:
            node_player = "W"

        # Collect MoveCoord for board renderer
        if node.move and node_player:
            if node.move.is_pass:
                move_coords.append(
                    MoveCoord(player=node_player, col=0, row=0, is_pass=True)
                )
            else:
                col, row = node.move.coords  # (col, row) 0-based
                move_coords.append(
                    MoveCoord(player=node_player, col=col, row=row, is_pass=False)
                )

        if comment_text:
            parsed = parse_comment(comment_text)
            # If move_number wasn't parsed from comment, use depth counter
            if parsed.move_number == 0:
                move_counter += 1
                parsed.move_number = move_counter
            else:
                move_counter = parsed.move_number

            # If player/coord not in comment, try to get from node properties
            if not parsed.player:
                parsed.player = node_player or ""
            if not parsed.coordinate and node.move:
                try:
                    parsed.coordinate = node.move.gtp()
                except Exception:
                    pass

            main_line_comments.append(parsed)

            if parsed.score is not None:
                score_trajectory.append(parsed.score)
            if parsed.winrate is not None:
                winrate_trajectory.append(parsed.winrate)
            if parsed.player and parsed.coordinate:
                move_labels.append(f"{parsed.player} {parsed.coordinate}")
        elif node.move:
            # Node has a move but no comment (no analysis)
            move_counter += 1
            player = node_player or "B"
            try:
                coord = node.move.gtp()
            except Exception:
                coord = "??"
            move_labels.append(f"{player} {coord}")
            main_line_comments.append(
                ParsedComment(player=player, coordinate=coord, move_number=move_counter)
            )

    # --- Step 4: Walk branches for undo events ---
    undo_events = _collect_undo_events(root)

    # --- Step 5: Compute statistics ---
    human_comments = [c for c in main_line_comments if c.player == human_player]
    stats = compute_game_stats(human_comments)

    # Flip trajectories to human's perspective when human played White
    if human_player == "W":
        score_trajectory = [-s for s in score_trajectory]
        winrate_trajectory = [100.0 - w for w in winrate_trajectory]

    # --- Step 6: Build result ---
    summary = GameSummary(
        filename=filepath.name,
        date=date,
        board_size=list(board_size),
        komi=komi,
        ruleset=ruleset,
        human_player=human_player,
        human_name=human_name,
        ai_name=ai_name,
        ai_rank=ai_rank if ai_rank else None,
        game_mode=game_mode,
        total_moves=len(main_line_comments),
        sgf_language=sgf_language,
        mean_points_lost=stats["mean_points_lost"],
        max_points_lost=stats["max_points_lost"],
        accuracy=stats["accuracy"],
        best_move_rate=stats["best_move_rate"],
        good_move_rate=stats["good_move_rate"],
        histogram=stats["histogram"],
        undo_count=len(undo_events),
        undo_total_points_lost=sum(u.points_lost for u in undo_events),
        avg_policy_rank=stats["avg_policy_rank"],
        top1_policy_rate=stats["top1_policy_rate"],
    )

    return GameDetail(
        summary=summary,
        score_trajectory=score_trajectory,
        winrate_trajectory=winrate_trajectory,
        move_labels=move_labels,
        move_coords=move_coords,
        undo_details=undo_events,
    )


def detect_human_player(
    pb: str, pw: str, br: str | None = None, wr: str | None = None
) -> str:
    """
    Auto-detect which color the human played.
    Rules (priority order):
    1. Name contains "人类" or "人類" → that side is human
       (if both names match, fall through to rank tiebreaker)
    2. Name starts with "AI" or contains "KataGo" → that side is AI, other is human
    3. Rank tiebreaker: when names are identical, the side with a rank is the AI
    4. Fallback: "B"
    """
    # Rule 1: look for human marker — but only if names differ
    if pb != pw:
        for name, color in [(pb, "B"), (pw, "W")]:
            if "人类" in name or "人類" in name:
                return color

    # Rule 2: look for AI marker in name
    for name, color in [(pb, "B"), (pw, "W")]:
        if name.startswith("AI") or "KataGo" in name:
            return "W" if color == "B" else "B"

    # Rule 3: rank tiebreaker — the side that has a rank entry is the AI
    if br and not wr:
        return "W"  # Black has a rank → Black is AI → human is White
    if wr and not br:
        return "B"  # White has a rank → White is AI → human is Black

    return "B"


def detect_game_mode(human_name: str) -> str:
    """Detect game mode from human player name parenthetical."""
    if "指导棋" in human_name or "指導棋" in human_name:
        return "teaching"
    if "分先" in human_name:
        return "even"
    if "参考段位" in human_name or "參考段位" in human_name:
        return "ranked"
    return "unknown"


def _collect_undo_events(root: SGFNode) -> list[UndoEvent]:
    """
    Walk the full SGF tree to find undo branch nodes.
    Undo nodes are non-first children that contain the auto-undo marker.
    """
    undos = []

    def _walk(node: SGFNode):
        if len(node.children) > 1:
            # Check non-first children for undo markers
            for child in node.children[1:]:
                comment = child.get_property("C", "")
                if comment and any(
                    m in comment
                    for m in ["自动悔棋", "自動悔棋", "automatically undone"]
                ):
                    parsed = parse_comment(comment)
                    undos.append(
                        UndoEvent(
                            move_number=parsed.move_number,
                            player=parsed.player,
                            coordinate=parsed.coordinate,
                            points_lost=parsed.points_lost,
                            best_move_coord=parsed.best_move_coord,
                        )
                    )
        # Continue down main branch
        if node.children:
            _walk(node.children[0])

    _walk(root)
    return undos


def _clean_player_name(name: str | None) -> str:
    """Remove KaTrain's invisible marker characters from player names."""
    if not name:
        return "Unknown"
    return name.replace("\u3164", "").replace("\u200b", "").strip()


def _parse_date(date_str: str) -> datetime:
    """Parse KaTrain's date format: '2026-03-30 09 54 06'."""
    if not date_str:
        return datetime.now()
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d %H %M %S")
    except ValueError:
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except ValueError:
            return datetime.now()
