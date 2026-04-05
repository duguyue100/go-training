"""
In-memory cache of parsed SGF game data with file mtime invalidation.
"""

from pathlib import Path

from app.sgf_service import parse_sgf_file
from app.models import GameDetail


class GameCache:
    def __init__(self, training_dir: Path):
        self._training_dir = training_dir
        self._games: dict[str, GameDetail] = {}
        self._mtimes: dict[str, float] = {}

    def refresh_all(self) -> None:
        """Full scan of training directory."""
        if not self._training_dir.exists():
            return
        current_files = set(self._training_dir.glob("*.sgf"))
        current_names = {f.name for f in current_files}

        # Remove deleted files
        for name in list(self._games.keys()):
            if name not in current_names:
                del self._games[name]
                del self._mtimes[name]

        # Parse new or modified files
        for sgf_file in current_files:
            mtime = sgf_file.stat().st_mtime
            if sgf_file.name not in self._mtimes or self._mtimes[sgf_file.name] < mtime:
                try:
                    self._games[sgf_file.name] = parse_sgf_file(sgf_file)
                    self._mtimes[sgf_file.name] = mtime
                except Exception as e:
                    print(f"Error parsing {sgf_file.name}: {e}")

    def refresh_file(self, filename: str) -> None:
        """Re-parse a single file."""
        sgf_file = self._training_dir / filename
        if sgf_file.exists():
            try:
                self._games[filename] = parse_sgf_file(sgf_file)
                self._mtimes[filename] = sgf_file.stat().st_mtime
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
        else:
            self._games.pop(filename, None)
            self._mtimes.pop(filename, None)

    def get_all_games(self) -> list[GameDetail]:
        """Return all games sorted by date (ascending)."""
        return sorted(self._games.values(), key=lambda g: g.summary.date)

    def get_game(self, filename: str) -> GameDetail | None:
        return self._games.get(filename)
