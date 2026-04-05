# Go Training Dashboard

English | [中文](README.zh.md)

A personal training progress dashboard for [KaTrain](https://github.com/sanderland/katrain) games. It reads SGF files exported by KaTrain, parses the embedded KataGo analysis, and displays your opening-phase progress through an interactive web UI.

| Overview | Game history |
|:---:|:---:|
| ![Overview](https://github.com/user-attachments/assets/68c7398c-5bec-4b50-af28-0ba086695f18) | ![Game history](https://github.com/user-attachments/assets/32a2c925-d8cc-48c6-884c-ccb3bcd71303) |


## Features

- Per-game statistics: average points lost, std-dev consistency band, best move rate, policy rank
- Progress charts over time with ±1σ error bands
- Move quality histogram (KaTrain's 6-bucket evaluation scale)
- Per-game drill-down: interactive Go board, score/winrate trajectory, phase breakdown (opening / midgame / endgame), undo details
- Live updates via WebSocket — drop a new SGF into `training/` and the dashboard refreshes automatically
- Bilingual UI (Chinese / English toggle)
- Info tooltips on every key metric

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac, Windows, or Linux)

That's it. No Python environment or Node.js needed on the host.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/go-training.git
cd go-training
```

### 2. Create the training folder

SGF files are not committed (they are personal). Create the folder the app expects:

```bash
mkdir -p training
```

Copy your KaTrain SGF files into `training/`. The app will pick them up automatically at startup and watch for new ones while running.

### 3. Start the dashboard

```bash
docker compose up --build
```

The first build takes about 30–60 seconds while Docker downloads the Python base image and installs dependencies. Subsequent starts are fast.

Open [http://localhost:4096](http://localhost:4096) in your browser.

## Everyday use

Once set up, starting and stopping is just:

```bash
# Start (in the background)
docker compose up -d

# Stop
docker compose down
```

To add a new game, save it from KaTrain as usual — the app detects new SGF files in `training/` and updates the dashboard within a few seconds without needing a restart.

## Project structure

```
go-training/
├── training/               # Your SGF files (gitignored)
├── docker-compose.yml      # Service definition, resource limits
├── Dockerfile              # Python 3.12 slim image
├── requirements.txt        # FastAPI, uvicorn, watchfiles, pydantic
└── app/
    ├── main.py             # FastAPI app, REST API + WebSocket endpoints
    ├── models.py           # Pydantic response models
    ├── sgf_parser.py       # Vendored SGF parser (from KaTrain)
    ├── comment_parser.py   # Parses KataGo analysis from SGF comments
    ├── stats_engine.py     # Per-game statistics computation
    ├── sgf_service.py      # Orchestrates parsing pipeline
    ├── game_cache.py       # In-memory cache with mtime invalidation
    ├── file_watcher.py     # Async file watcher + WebSocket push
    └── static/
        ├── index.html      # Vue 3 SPA (no build step)
        ├── js/
        │   ├── app.js      # Vue application + Chart.js rendering
        │   └── i18n.js     # Chinese / English translations
        ├── css/
        │   └── style.css
        └── img/            # Board images from KaTrain (MIT licensed, bundled)
```

## Resource usage

The container runs with explicit limits set in `docker-compose.yml`:

| Resource | Limit | Typical usage |
|---|---|---|
| Memory | 128 MB | ~40 MB |
| CPU | 0.5 cores | < 1% at idle |

## API

The backend exposes three JSON endpoints if you want to build your own tooling:

| Endpoint | Description |
|---|---|
| `GET /api/games` | List of all games with summary statistics |
| `GET /api/stats` | Aggregate trends across all games |
| `GET /api/game/{filename}` | Full detail for one game (trajectories, board moves, undos) |
| `WS /ws` | WebSocket — pushes `{"type":"update"}` when SGF files change |

## Notes

- Only KaTrain SGF files with embedded KataGo analysis comments are supported. Plain SGF files without analysis will be parsed but show no statistics.
- The dashboard is designed for opening-phase training (games stopped at move 50). Phase breakdown and policy rank metrics are most meaningful in this context.
- SGF files are gitignored — they are personal data.

## License

MIT © 2026 Yuhuang Hu

This project includes vendored code from [KaTrain](https://github.com/sanderland/katrain) (MIT License, © 2020 Sander Land) in `app/sgf_parser.py`.
