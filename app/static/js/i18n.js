// i18n translation dictionaries for Chinese and English UI
const messages = {
    zh: {
        // Header
        title: "围棋训练仪表盘",
        liveConnected: "实时更新已连接",
        liveDisconnected: "实时更新未连接",
        loading: "正在加载...",

        // Summary cards
        totalGames: "总对局数",
        avgPointsLost: "平均目数损失",
        accuracy: "准确率",
        bestMoveRate: "最佳着手率",
        approxLabel: "(近似)",

        // Chart titles
        progressOverTime: "训练进度",
        moveQuality: "着手质量分布",
        undoTrend: "悔棋趋势",

        // Move quality buckets (index 0=excellent, 5=critical)
        excellent: "优秀",
        good: "良好",
        inaccuracy: "不准确",
        mistake: "失误",
        blunder: "大失误",
        critical: "严重失误",

        // Game table
        gameHistory: "对局历史",
        date: "日期",
        color: "执子",
        black: "黑",
        white: "白",
        mode: "模式",
        opponent: "对手",
        moves: "手数",
        undoCount: "悔棋次数",

        // Game modes
        teaching: "指导棋",
        even: "分先对局",
        ranked: "参考段位",
        unknown: "未知",

        // Detail panel
        scoreCurve: "形势判断",
        winrateCurve: "胜率曲线",
        showScore: "形势",
        showWinrate: "胜率",
        undoDetails: "悔棋详情",
        moveLabel: "第",
        pointsLostLabel: "目数损失",
        bestMoveLabel: "最佳着手",
        goodMoveRate: "良好着手率",
        avgPolicyRank: "平均直觉排名",
        noGames: "暂无对局数据，请将 SGF 文件放入 training/ 目录",
        clickToExpand: "点击查看详情",

        // Game settings
        gameSettings: "对局设置",
        ruleset: "规则",
        komi: "贴目",
        boardSize: "棋盘大小",
        chinese: "中国规则",
        japanese: "日本规则",
        korean: "韩国规则",
        aga: "AGA规则",
        nz: "新西兰规则",

        // Move quality histogram legend
        moveQualityLegend: "着手质量",
        humanMoves: "你的着手",
    },
    en: {
        title: "Go Training Dashboard",
        liveConnected: "Live updates connected",
        liveDisconnected: "Live updates disconnected",
        loading: "Loading...",

        totalGames: "Total Games",
        avgPointsLost: "Avg Points Lost",
        accuracy: "Accuracy",
        bestMoveRate: "Best Move Rate",
        approxLabel: "(approx)",

        progressOverTime: "Progress Over Time",
        moveQuality: "Move Quality Distribution",
        undoTrend: "Undo Trend",

        excellent: "Excellent",
        good: "Good",
        inaccuracy: "Inaccuracy",
        mistake: "Mistake",
        blunder: "Blunder",
        critical: "Critical",

        gameHistory: "Game History",
        date: "Date",
        color: "Color",
        black: "Black",
        white: "White",
        mode: "Mode",
        opponent: "Opponent",
        moves: "Moves",
        undoCount: "Undos",

        teaching: "Teaching",
        even: "Even Game",
        ranked: "Ranked",
        unknown: "Unknown",

        scoreCurve: "Score",
        winrateCurve: "Win Rate",
        showScore: "Score",
        showWinrate: "Win Rate",
        undoDetails: "Undo Details",
        moveLabel: "Move",
        pointsLostLabel: "Points Lost",
        bestMoveLabel: "Best Move",
        goodMoveRate: "Good Move Rate",
        avgPolicyRank: "Avg Policy Rank",
        noGames: "No games found. Add SGF files to the training/ folder.",
        clickToExpand: "Click to expand",

        // Game settings
        gameSettings: "Game Settings",
        ruleset: "Rules",
        komi: "Komi",
        boardSize: "Board",
        chinese: "Chinese",
        japanese: "Japanese",
        korean: "Korean",
        aga: "AGA",
        nz: "New Zealand",

        // Move quality histogram legend
        moveQualityLegend: "Move Quality",
        humanMoves: "Your moves",
    }
};
