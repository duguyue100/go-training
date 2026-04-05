# 围棋训练仪表盘

[English](README.md) | 中文

一个基于 [KaTrain](https://github.com/sanderland/katrain) 对局文件的个人训练进度仪表盘。它读取 KaTrain 导出的 SGF 文件，解析嵌入其中的 KataGo 分析数据，并通过交互式 Web UI 展示你的布局阶段进步情况。

| 总览 | 对局历史 |
|:---:|:---:|
| ![总览](https://github.com/user-attachments/assets/68c7398c-5bec-4b50-af28-0ba086695f18) | ![对局历史](https://github.com/user-attachments/assets/32a2c925-d8cc-48c6-884c-ccb3bcd71303) |

## 功能特性

- 每局统计：平均失分、一致性标准差区间、最佳手比例、策略排名
- 带 ±1σ 误差区间的时间序列进步图表
- 手质量直方图（KaTrain 的六档评分体系）
- 每局详情展开：交互式棋盘、分差/胜率走势、布局/中盘/残局阶段分析、悔棋详情
- WebSocket 实时更新——将新 SGF 文件放入 `training/` 后仪表盘自动刷新，无需重启
- 中英文双语界面切换
- 每项关键指标均提供信息提示（鼠标悬停或点击）

## 依赖要求

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（支持 Mac、Windows、Linux）

无需在宿主机上安装 Python 或 Node.js。

## 安装配置

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/go-training.git
cd go-training
```

### 2. 创建训练对局文件夹

SGF 文件不提交到仓库（属于个人数据）。请创建应用所需的文件夹：

```bash
mkdir -p training
```

将你的 KaTrain SGF 文件复制到 `training/` 目录。应用启动时会自动加载这些文件，运行期间也会监测新增文件。

### 3. 启动仪表盘

```bash
docker compose up --build
```

首次构建需要约 30–60 秒（Docker 下载 Python 基础镜像并安装依赖）。之后启动会很快。

在浏览器中打开 [http://localhost:4096](http://localhost:4096)。

## 日常使用

配置完成后，启动和停止只需：

```bash
# 后台启动
docker compose up -d

# 停止
docker compose down
```

完成一局对局后，像往常一样从 KaTrain 保存即可——应用会检测到 `training/` 中的新 SGF 文件，并在几秒内自动更新仪表盘，无需重启。

## 项目结构

```
go-training/
├── training/               # 你的 SGF 文件（已 gitignore）
├── docker-compose.yml      # 服务定义，包含资源限制
├── Dockerfile              # Python 3.12 slim 镜像
├── requirements.txt        # FastAPI、uvicorn、watchfiles、pydantic
└── app/
    ├── main.py             # FastAPI 应用，REST API + WebSocket 端点
    ├── models.py           # Pydantic 响应模型
    ├── sgf_parser.py       # 来自 KaTrain 的 SGF 解析器（vendored）
    ├── comment_parser.py   # 解析 SGF 注释中的 KataGo 分析数据
    ├── stats_engine.py     # 每局统计计算
    ├── sgf_service.py      # 协调解析流程
    ├── game_cache.py       # 带 mtime 失效的内存缓存
    ├── file_watcher.py     # 异步文件监测 + WebSocket 推送
    └── static/
        ├── index.html      # Vue 3 单页应用（无需构建步骤）
        ├── js/
        │   ├── app.js      # Vue 应用 + Chart.js 图表渲染
        │   └── i18n.js     # 中英文翻译
        ├── css/
        │   └── style.css
        └── img/            # 来自 KaTrain 的棋盘图片（MIT 许可，已随仓库分发）
```

## 资源占用

容器在 `docker-compose.yml` 中设置了明确的资源限制：

| 资源 | 限制 | 典型用量 |
|---|---|---|
| 内存 | 128 MB | 约 40 MB |
| CPU | 0.5 核 | 空闲时 < 1% |

## API 接口

后端提供三个 JSON 接口，便于自行构建工具：

| 接口 | 说明 |
|---|---|
| `GET /api/games` | 所有对局的列表及摘要统计 |
| `GET /api/stats` | 所有对局的聚合趋势数据 |
| `GET /api/game/{filename}` | 单局完整详情（走势、棋盘落子、悔棋记录） |
| `WS /ws` | WebSocket——SGF 文件变动时推送 `{"type":"update"}` |

## 说明

- 仅支持嵌入了 KataGo 分析注释的 KaTrain SGF 文件。不含分析数据的普通 SGF 文件可以解析，但不会显示统计信息。
- 仪表盘专为布局阶段训练设计（对局在第 50 手停止）。阶段分析和策略排名指标在此场景下最有意义。
- SGF 文件已 gitignore——属于个人数据，不纳入版本管理。

## 参与贡献

本项目为全程 vibe-coded，作为个人工具维护。不接受社区的 Pull Request。如果你希望扩展或修改本项目，欢迎 Fork 仓库，在此基础上自由开发。

## 许可证

MIT © 2025 Yuhuang Hu

本项目包含来自 [KaTrain](https://github.com/sanderland/katrain)（MIT 许可，© 2020 Sander Land）的部分代码（`app/sgf_parser.py`）。
