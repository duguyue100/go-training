// Go Training Dashboard - Vue.js 3 Application
const { createApp, ref, computed, onMounted, watch, nextTick } = Vue;

// ---- Go Board Renderer ----
const BoardImages = (() => {
    let boardImg = null, blackImg = null, whiteImg = null, innerImg = null;
    let loaded = 0;
    const total = 4;
    const callbacks = [];

    function loadAll(cb) {
        if (loaded === total) { cb(); return; }
        callbacks.push(cb);
        if (loaded > 0) return; // already loading

        function onLoad() {
            loaded++;
            if (loaded === total) { callbacks.forEach(f => { f(); }); }
        }
        boardImg  = new Image(); boardImg.onload  = onLoad; boardImg.src  = '/static/img/board.png';
        blackImg  = new Image(); blackImg.onload  = onLoad; blackImg.src  = '/static/img/B_stone.png';
        whiteImg  = new Image(); whiteImg.onload  = onLoad; whiteImg.src  = '/static/img/W_stone.png';
        innerImg  = new Image(); innerImg.onload  = onLoad; innerImg.src  = '/static/img/inner.png';
    }
    return { loadAll, get board() { return boardImg; }, get black() { return blackImg; },
             get white() { return whiteImg; }, get inner() { return innerImg; } };
})();

// Standard 19x19 star points (0-indexed)
const HOSHI = [
    [3,3],[3,9],[3,15],[9,3],[9,9],[9,15],[15,3],[15,9],[15,15]
];

// GTP column labels (skip I)
const GTP_COLS = 'ABCDEFGHJKLMNOPQRST';

/**
 * Build final board state at `upToMove` (1-based, 0 = empty board).
 * Returns { board: Map<key, 'B'|'W'>, lastCol, lastRow } where key = `${col},${row}`.
 */
function buildBoardState(moveCoords, upToMove) {
    const board = new Map();  // key -> 'B' | 'W'

    let lastCol = -1, lastRow = -1;
    const limit = Math.min(upToMove, moveCoords.length);

    for (let i = 0; i < limit; i++) {
        const { player, col, row, is_pass } = moveCoords[i];
        if (is_pass) continue;

        board.set(`${col},${row}`, player);
        lastCol = col; lastRow = row;

        // Remove captured opponent groups
        const opp = player === 'B' ? 'W' : 'B';
        const neighbors = [[col-1,row],[col+1,row],[col,row-1],[col,row+1]];
        for (const [nc, nr] of neighbors) {
            const nk = `${nc},${nr}`;
            if (board.get(nk) === opp) {
                const group = getGroup(board, nc, nr);
                if (!hasLiberty(board, group)) {
                    for (const k of group) board.delete(k);
                }
            }
        }

        // Remove own group if it has no liberties (suicide — rare but handle)
        const ownGroup = getGroup(board, col, row);
        if (!hasLiberty(board, ownGroup)) {
            for (const k of ownGroup) board.delete(k);
            lastCol = -1; lastRow = -1;
        }
    }
    return { board, lastCol, lastRow };
}

function getGroup(board, startCol, startRow) {
    const color = board.get(`${startCol},${startRow}`);
    if (!color) return new Set();
    const group = new Set();
    const stack = [[startCol, startRow]];
    while (stack.length) {
        const [c, r] = stack.pop();
        const k = `${c},${r}`;
        if (group.has(k)) continue;
        if (board.get(k) !== color) continue;
        group.add(k);
        stack.push([c-1,r],[c+1,r],[c,r-1],[c,r+1]);
    }
    return group;
}

function hasLiberty(board, group) {
    for (const k of group) {
        const [c, r] = k.split(',').map(Number);
        for (const [nc, nr] of [[c-1,r],[c+1,r],[c,r-1],[c,r+1]]) {
            if (nc < 0 || nr < 0 || nc >= 19 || nr >= 19) continue;
            if (!board.has(`${nc},${nr}`)) return true;
        }
    }
    return false;
}

/**
 * Draw the Go board onto `canvas` up to move `upToMove`.
 */
function drawBoard(canvas, moveCoords, upToMove) {
    const SIZE = 19;
    const PADDING = 32;      // pixels for coordinate labels
    const W = canvas.width;
    const H = canvas.height;
    const boardW = W - 2 * PADDING;
    const boardH = H - 2 * PADDING;
    const cellW = boardW / (SIZE - 1);
    const cellH = boardH / (SIZE - 1);
    const cell = Math.min(cellW, cellH);

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, W, H);

    // --- Background: tile board.png ---
    if (BoardImages.board) {
        const pat = ctx.createPattern(BoardImages.board, 'repeat');
        ctx.fillStyle = pat || '#dcb468';
    } else {
        ctx.fillStyle = '#dcb468';
    }
    ctx.fillRect(0, 0, W, H);

    // --- Grid lines ---
    ctx.strokeStyle = '#5a3a0a';
    ctx.lineWidth = 0.8;
    for (let i = 0; i < SIZE; i++) {
        const x = PADDING + i * cell;
        const y = PADDING + i * cell;
        // Vertical
        ctx.beginPath();
        ctx.moveTo(x, PADDING);
        ctx.lineTo(x, PADDING + (SIZE-1) * cell);
        ctx.stroke();
        // Horizontal
        ctx.beginPath();
        ctx.moveTo(PADDING, y);
        ctx.lineTo(PADDING + (SIZE-1) * cell, y);
        ctx.stroke();
    }

    // --- Star points (hoshi) ---
    ctx.fillStyle = '#5a3a0a';
    for (const [hc, hr] of HOSHI) {
        const x = PADDING + hc * cell;
        const y = PADDING + (SIZE - 1 - hr) * cell;  // row 0 = bottom → y is large
        ctx.beginPath();
        ctx.arc(x, y, Math.max(2.5, cell * 0.09), 0, Math.PI * 2);
        ctx.fill();
    }

    // --- Coordinate labels ---
    const labelSize = Math.max(9, Math.min(12, PADDING * 0.5));
    ctx.fillStyle = '#3a2000';
    ctx.font = `${labelSize}px monospace`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < SIZE; i++) {
        const colLabel = GTP_COLS[i];
        const rowLabel = String(i + 1);
        const x = PADDING + i * cell;
        const y = PADDING + (SIZE - 1 - i) * cell;
        // Top column labels
        ctx.fillText(colLabel, x, PADDING / 2);
        // Bottom column labels
        ctx.fillText(colLabel, x, H - PADDING / 2);
        // Left row labels
        ctx.fillText(rowLabel, PADDING / 2, y);
        // Right row labels
        ctx.fillText(rowLabel, W - PADDING / 2, y);
    }

    // --- Stones ---
    const { board, lastCol, lastRow } = buildBoardState(moveCoords, upToMove);
    const stoneR = cell * 0.505 / 2;  // KaTrain's STONE_SIZE = 0.505

    for (const [key, color] of board) {
        const [c, r] = key.split(',').map(Number);
        const x = PADDING + c * cell;
        const y = PADDING + (SIZE - 1 - r) * cell;
        const img = color === 'B' ? BoardImages.black : BoardImages.white;
        if (img) {
            // Image has ~200px transparent border; the stone fills center ~66%
            // We draw the full image oversized so the actual stone hits stoneR
            const drawR = stoneR / 0.66 * 2;
            ctx.drawImage(img, x - drawR/2, y - drawR/2, drawR, drawR);
        } else {
            // Fallback solid circle
            ctx.beginPath();
            ctx.arc(x, y, stoneR, 0, Math.PI * 2);
            ctx.fillStyle = color === 'B' ? '#111' : '#eee';
            ctx.fill();
            ctx.strokeStyle = '#555';
            ctx.lineWidth = 0.5;
            ctx.stroke();
        }
    }

    // --- Last-move indicator ---
    if (lastCol >= 0 && lastRow >= 0) {
        const x = PADDING + lastCol * cell;
        const y = PADDING + (SIZE - 1 - lastRow) * cell;
        if (BoardImages.inner) {
            const drawR = stoneR / 0.66 * 2;
            ctx.drawImage(BoardImages.inner, x - drawR/2, y - drawR/2, drawR, drawR);
        } else {
            const lastColor = board.get(`${lastCol},${lastRow}`);
            ctx.beginPath();
            ctx.arc(x, y, stoneR * 0.45, 0, Math.PI * 2);
            ctx.strokeStyle = lastColor === 'B' ? '#eee' : '#333';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
    }
}

// KaTrain evaluation colors (index 0=excellent, 5=critical)
const EVAL_COLORS = ['#1E9600', '#ABE618', '#F2F200', '#E6661A', '#CC0000', '#72216B'];

const app = createApp({
    setup() {
        // --- State ---
        const locale = ref(localStorage.getItem('locale') || 'zh');
        const games = ref([]);
        const stats = ref({});
        const loading = ref(true);
        const expandedGame = ref(null);
        const gameDetail = ref(null);
        const detailLoading = ref(false);
        const wsConnected = ref(false);

        // Chart instances (for cleanup / re-render)
        let progressChart = null;
        let qualityChart = null;
        let undoChart = null;
        let detailChart = null;   // combined score + winrate chart

        // --- Board slider state ---
        const boardMove = ref(0);   // current slider position (0 = empty, N = after move N)

        // --- Detail chart toggle state ---
        const showScore = ref(true);
        const showWinrate = ref(true);

        // Histogram colors + labels for detail row
        const histColors = EVAL_COLORS;
        const histLabels = computed(() => [
            t('excellent'), t('good'), t('inaccuracy'), t('mistake'), t('blunder'), t('critical')
        ]);

        // Reversed games for table (newest first)
        const gamesReversed = computed(() => [...games.value].reverse());

        // --- i18n ---
        const t = (key) => messages[locale.value]?.[key] ?? messages['en']?.[key] ?? key;

        const toggleLang = () => {
            locale.value = locale.value === 'zh' ? 'en' : 'zh';
            localStorage.setItem('locale', locale.value);
        };

        // --- Helpers ---
        const formatNum = (val) => val != null ? Number(val).toFixed(2) : '—';
        const formatPct = (val) => val != null ? Number(val).toFixed(1) + '%' : '—';
        const formatPct100 = (val) => val != null ? (Number(val) * 100).toFixed(1) + '%' : '—';
        const formatDate = (dateStr) => {
            const d = new Date(dateStr);
            return d.toLocaleDateString(locale.value === 'zh' ? 'zh-CN' : 'en-US', {
                year: 'numeric', month: 'short', day: 'numeric'
            });
        };
        const ptlossClass = (val) => {
            if (val == null) return '';
            if (val < 2) return 'ptloss-good';
            if (val < 4) return 'ptloss-ok';
            return 'ptloss-bad';
        };

        const formatRuleset = (rs) => {
            const key = (rs || '').toLowerCase();
            const map = { chinese: t('chinese'), japanese: t('japanese'), korean: t('korean'), aga: t('aga'), nz: t('nz') };
            return map[key] ?? rs ?? '—';
        };

        // --- Chart helpers ---
        function destroyChart(chartRef) {
            if (chartRef) {
                chartRef.destroy();
            }
            return null;
        }

        function safeCanvas(id) {
            return document.getElementById(id);
        }

        // --- Data Fetching ---
        async function fetchGames() {
            const res = await fetch('/api/games');
            games.value = await res.json();
        }

        async function fetchStats() {
            const res = await fetch('/api/stats');
            stats.value = await res.json();
        }

        async function fetchGameDetail(filename) {
            detailLoading.value = true;
            try {
                const res = await fetch(`/api/game/${encodeURIComponent(filename)}`);
                gameDetail.value = await res.json();
            } finally {
                detailLoading.value = false;
            }
        }

        // --- Chart Rendering ---

        function renderProgressChart() {
            const canvas = safeCanvas('progressChart');
            if (!canvas) return;
            if (!stats.value.trends?.dates?.length) return;

            progressChart = destroyChart(progressChart);

            const trends = stats.value.trends;
            progressChart = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: trends.dates,
                    datasets: [
                        {
                            label: t('avgPointsLost'),
                            data: trends.mean_points_lost,
                            borderColor: '#2563eb',
                            backgroundColor: 'rgba(37, 99, 235, 0.08)',
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4,
                            yAxisID: 'y-loss',
                        },
                        {
                            label: t('accuracy') + ' ' + t('approxLabel'),
                            data: trends.accuracy,
                            borderColor: '#16a34a',
                            backgroundColor: 'rgba(22, 163, 74, 0.08)',
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4,
                            yAxisID: 'y-accuracy',
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const label = ctx.dataset.label || '';
                                    const value = Number(ctx.parsed.y).toFixed(2);
                                    return `${label}: ${value}`;
                                }
                            }
                        }
                    },
                    scales: {
                        'y-loss': {
                            type: 'linear',
                            position: 'left',
                            title: { display: true, text: t('avgPointsLost') },
                            reverse: true,
                        },
                        'y-accuracy': {
                            type: 'linear',
                            position: 'right',
                            title: { display: true, text: t('accuracy') + ' %' },
                            min: 0,
                            max: 100,
                            grid: { drawOnChartArea: false },
                        }
                    }
                }
            });
        }

        function renderQualityChart() {
            const canvas = safeCanvas('qualityChart');
            if (!canvas) return;
            if (!games.value.length) return;

            qualityChart = destroyChart(qualityChart);

            const dates = games.value.map(g => formatDate(g.date));
            const bucketLabels = [
                t('excellent'), t('good'), t('inaccuracy'), t('mistake'), t('blunder'), t('critical')
            ];

            // Build percentage datasets for each bucket
            const datasets = bucketLabels.map((label, i) => ({
                label,
                data: games.value.map(g => {
                    const total = g.histogram.reduce((a, b) => a + b, 0);
                    return total > 0 ? Number((g.histogram[i] / total * 100).toFixed(1)) : 0;
                }),
                backgroundColor: EVAL_COLORS[i],
            }));

            qualityChart = new Chart(canvas, {
                type: 'bar',
                data: { labels: dates, datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}%`
                            }
                        }
                    },
                    scales: {
                        x: { stacked: true },
                        y: {
                            stacked: true,
                            max: 100,
                            title: { display: true, text: '%' }
                        }
                    }
                }
            });
        }

        function renderUndoChart() {
            const canvas = safeCanvas('undoChart');
            if (!canvas) return;
            if (!stats.value.trends?.dates?.length) return;

            undoChart = destroyChart(undoChart);

            const trends = stats.value.trends;
            undoChart = new Chart(canvas, {
                type: 'bar',
                data: {
                    labels: trends.dates,
                    datasets: [{
                        label: t('undoCount'),
                        data: trends.undo_count,
                        backgroundColor: '#E6661A',
                        borderRadius: 4,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1 }
                        }
                    }
                }
            });
        }

        /**
         * Combined score + win-rate chart with dual Y-axes.
         * Each dataset can be independently hidden via showScore / showWinrate toggles.
         */
        function renderDetailChart(canvasId, scoreTrajectory, winrateTrajectory, labels) {
            const canvas = safeCanvas(canvasId);
            if (!canvas) return;

            detailChart = destroyChart(detailChart);

            const maxLen = Math.max(scoreTrajectory.length, winrateTrajectory.length);
            if (maxLen === 0) return;
            const chartLabels = labels.slice(0, maxLen);

            // Build a midpoint fraction for gradient zero-line positioning
            function midGradient(ctx, chartArea, minVal, maxVal) {
                const c = ctx.chart.ctx;
                if (!chartArea) return 'rgba(37,99,235,0.12)';
                const range = maxVal - minVal || 1;
                const zeroFrac = Math.max(0, Math.min(1, (maxVal) / range));
                const g = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                g.addColorStop(0,        'rgba(22, 163, 74, 0.30)');
                g.addColorStop(Math.max(0, zeroFrac - 0.01), 'rgba(22, 163, 74, 0.08)');
                g.addColorStop(Math.min(1, zeroFrac + 0.01), 'rgba(220, 38, 38, 0.08)');
                g.addColorStop(1,        'rgba(220, 38, 38, 0.30)');
                return g;
            }

            const scoreMin = scoreTrajectory.length ? Math.min(...scoreTrajectory) : -10;
            const scoreMax = scoreTrajectory.length ? Math.max(...scoreTrajectory) : 10;

            detailChart = new Chart(canvas, {
                type: 'line',
                data: {
                    labels: chartLabels,
                    datasets: [
                        {
                            label: t('showScore'),
                            data: scoreTrajectory,
                            yAxisID: 'y-score',
                            borderColor: '#2563eb',
                            backgroundColor: (ctx) => {
                                const { chartArea } = ctx.chart;
                                return midGradient(ctx, chartArea, scoreMin, scoreMax);
                            },
                            fill: true,
                            tension: 0.35,
                            pointRadius: 2,
                            borderWidth: 2,
                            hidden: !showScore.value,
                        },
                        {
                            label: t('showWinrate'),
                            data: winrateTrajectory,
                            yAxisID: 'y-wr',
                            borderColor: '#9333ea',
                            backgroundColor: (ctx) => {
                                const { chartArea } = ctx.chart;
                                if (!chartArea) return 'rgba(147,51,234,0.08)';
                                const c = ctx.chart.ctx;
                                const g = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                                g.addColorStop(0,    'rgba(22, 163, 74, 0.22)');
                                g.addColorStop(0.48, 'rgba(200,200,200,0.04)');
                                g.addColorStop(0.52, 'rgba(200,200,200,0.04)');
                                g.addColorStop(1,    'rgba(220, 38, 38, 0.22)');
                                return g;
                            },
                            fill: true,
                            tension: 0.35,
                            pointRadius: 2,
                            borderWidth: 2,
                            borderDash: [4, 2],
                            hidden: !showWinrate.value,
                        },
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    plugins: {
                        legend: { display: false },  // we render our own toggle buttons
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const v = Number(ctx.parsed.y).toFixed(1);
                                    if (ctx.datasetIndex === 0) return `${t('showScore')}: ${v > 0 ? '+' : ''}${v}`;
                                    return `${t('showWinrate')}: ${v}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        x: { display: false },
                        'y-score': {
                            type: 'linear',
                            position: 'left',
                            title: { display: true, text: t('showScore'), color: '#2563eb', font: { size: 11 } },
                            grid: { color: 'rgba(0,0,0,0.06)' },
                            ticks: { color: '#2563eb', font: { size: 10 } },
                            display: showScore.value,
                        },
                        'y-wr': {
                            type: 'linear',
                            position: 'right',
                            min: 0,
                            max: 100,
                            title: { display: true, text: t('showWinrate') + ' %', color: '#9333ea', font: { size: 11 } },
                            grid: { drawOnChartArea: false },
                            ticks: { color: '#9333ea', font: { size: 10 } },
                            display: showWinrate.value,
                        }
                    }
                }
            });
        }

        function toggleDetailSeries(which) {
            if (which === 'score') showScore.value = !showScore.value;
            else showWinrate.value = !showWinrate.value;
            if (!detailChart) return;
            const idx = which === 'score' ? 0 : 1;
            const meta = detailChart.getDatasetMeta(idx);
            meta.hidden = !meta.hidden;
            detailChart.options.scales['y-score'].display = showScore.value;
            detailChart.options.scales['y-wr'].display = showWinrate.value;
            detailChart.update();
        }

        // --- Board rendering ---
        function renderBoard() {
            if (!gameDetail.value) return;
            const canvas = document.getElementById('boardCanvas');
            if (!canvas) return;
            drawBoard(canvas, gameDetail.value.move_coords, boardMove.value);
        }

        function setBoardMove(n) {
            if (!gameDetail.value) return;
            const max = gameDetail.value.move_coords.length;
            boardMove.value = Math.max(0, Math.min(max, n));
            renderBoard();
        }

        // --- Row Expand/Collapse ---
        async function toggleExpand(filename) {
            if (expandedGame.value === filename) {
                expandedGame.value = null;
                gameDetail.value = null;
                boardMove.value = 0;
                detailChart = destroyChart(detailChart);
                return;
            }
            expandedGame.value = filename;
            gameDetail.value = null;
            boardMove.value = 0;
            await fetchGameDetail(filename);

            // Wait for DOM update, then render detail charts + board
            await nextTick();
            if (gameDetail.value) {
                renderDetailChart(
                    `detail-chart-${filename}`,
                    gameDetail.value.score_trajectory,
                    gameDetail.value.winrate_trajectory,
                    gameDetail.value.move_labels
                );
                // Set slider to last move and draw board
                boardMove.value = gameDetail.value.move_coords.length;
                BoardImages.loadAll(() => {
                    nextTick().then(() => renderBoard());
                });
            }
        }

        // Re-render all charts
        function renderAllCharts() {
            renderProgressChart();
            renderQualityChart();
            renderUndoChart();
        }

        // --- WebSocket ---
        function connectWebSocket() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${location.host}/ws`);
            ws.onopen = () => { wsConnected.value = true; };
            ws.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'new_game') {
                    await fetchGames();
                    await fetchStats();
                    renderAllCharts();
                }
            };
            ws.onclose = () => {
                wsConnected.value = false;
                // Reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };
            ws.onerror = () => {
                wsConnected.value = false;
            };
        }

        // --- Lifecycle ---
        onMounted(async () => {
            try {
                await Promise.all([fetchGames(), fetchStats()]);
            } finally {
                loading.value = false;
            }
            await nextTick();
            renderAllCharts();
            connectWebSocket();
        });

        // Re-render charts when language changes (for translated axis labels)
        watch(locale, async () => {
            await nextTick();
            renderAllCharts();
        });

        return {
            locale, games, gamesReversed, stats, loading,
            expandedGame, gameDetail, detailLoading, wsConnected,
            histColors, histLabels,
            boardMove, setBoardMove,
            showScore, showWinrate, toggleDetailSeries,
            t, toggleLang, toggleExpand,
            formatNum, formatPct, formatPct100, formatDate, ptlossClass, formatRuleset,
        };
    }
});

app.mount('#app');
