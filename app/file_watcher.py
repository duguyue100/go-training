"""
Async file watcher for the training directory.
Watches for SGF file changes and pushes notifications via WebSocket.
"""

from pathlib import Path

from fastapi import WebSocket
from watchfiles import awatch


async def start_file_watcher(
    training_dir: Path,
    cache,  # GameCache
    connections: set[WebSocket],
):
    """Watch training directory for SGF file changes."""
    if not training_dir.exists():
        return

    async for changes in awatch(str(training_dir)):
        for change_type, file_path in changes:
            if file_path.endswith(".sgf"):
                filename = Path(file_path).name
                cache.refresh_file(filename)

                # Notify all connected WebSocket clients
                dead = set()
                for ws in connections:
                    try:
                        await ws.send_json(
                            {
                                "type": "new_game",
                                "filename": filename,
                            }
                        )
                    except Exception:
                        dead.add(ws)
                connections -= dead
