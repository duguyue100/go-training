"""
FastAPI application: REST API + WebSocket + static file serving.
"""

import os
import asyncio
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.game_cache import GameCache
from app.file_watcher import start_file_watcher

# Configuration
TRAINING_DIR = Path(os.environ.get("TRAINING_DIR", "training"))

# Global state
cache = GameCache(TRAINING_DIR)
ws_connections: set[WebSocket] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: load cache, start file watcher."""
    cache.refresh_all()
    watcher_task = asyncio.create_task(
        start_file_watcher(TRAINING_DIR, cache, ws_connections)
    )
    yield
    watcher_task.cancel()
    try:
        await watcher_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Go Training Dashboard", lifespan=lifespan)

# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/games")
async def get_games():
    """List all games with summary statistics."""
    games = cache.get_all_games()
    return [g.summary.model_dump(mode="json") for g in games]


@app.get("/api/stats")
async def get_stats():
    """Aggregate trend statistics across all games."""
    games = cache.get_all_games()
    if not games:
        return {"total_games": 0, "date_range": [], "trends": {}, "overall": {}}

    summaries = [g.summary for g in games]
    dates = [s.date.strftime("%Y-%m-%d") for s in summaries]

    return {
        "total_games": len(summaries),
        "date_range": [dates[0], dates[-1]] if dates else [],
        "trends": {
            "dates": dates,
            "mean_points_lost": [s.mean_points_lost for s in summaries],
            "stddev_points_lost": [s.stddev_points_lost for s in summaries],
            "best_move_rate": [round(s.best_move_rate * 100, 1) for s in summaries],
            "top5_policy_rate": [
                round(s.top5_policy_rate * 100, 1)
                if s.top5_policy_rate is not None
                else None
                for s in summaries
            ],
            "undo_count": [s.undo_count for s in summaries],
            "avg_policy_rank": [s.avg_policy_rank for s in summaries],
        },
        "overall": {
            "avg_mean_points_lost": round(
                sum(s.mean_points_lost for s in summaries) / len(summaries), 2
            ),
            "avg_policy_rank": round(
                sum(
                    s.avg_policy_rank
                    for s in summaries
                    if s.avg_policy_rank is not None
                )
                / max(1, sum(1 for s in summaries if s.avg_policy_rank is not None)),
                1,
            )
            if any(s.avg_policy_rank is not None for s in summaries)
            else None,
            "avg_best_move_rate": round(
                sum(s.best_move_rate for s in summaries) / len(summaries), 3
            ),
            "total_undos": sum(s.undo_count for s in summaries),
        },
    }


@app.get("/api/game/{filename:path}")
async def get_game_detail(filename: str):
    """Per-game detail with trajectories and undo details."""
    detail = cache.get_game(filename)
    if detail is None:
        return {"error": "Game not found"}
    return detail.model_dump(mode="json")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        ws_connections.discard(websocket)
    except Exception:
        ws_connections.discard(websocket)
