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
        bestMoveRate: "最佳着手率",

        // Chart titles
        progressOverTime: "训练进度",
        matchRates: "着手匹配率",
        moveQuality: "着手质量分布",
        undoTrend: "悔棋趋势",

        // Match rate chart labels
        bestMoveMatch: "最佳着手匹配率",
        top5PolicyMatch: "Top-5 直觉匹配率",

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

        // Move quality chart series labels
        goodMovesPct: "好棋% (每局)",
        goodMovesAvg: "好棋% (滚动均值)",
        badMovesPct: "坏棋% (每局)",
        badMovesAvg: "坏棋% (滚动均值)",

        // Undo chart series labels
        undoAvg: "悔棋 (滚动均值)",

        // Move quality histogram legend
        moveQualityLegend: "着手质量",
        humanMoves: "你的着手",

        // Phase breakdown
        phaseBreakdown: "阶段分析",
        phaseOpening: "布局",
        phaseMidgame: "中盘",
        phaseEndgame: "官子",
        phaseAvgPtsLost: "平均目损",
        openingPolicyRank: "布局直觉排名",
        phaseTooFewMoves: "\u2014",

        // Tooltips
        tooltips: {
            avgPointsLost: "每手棋与 KataGo 最优解之间的平均目数差距，越低越好。0 = 完美；~1 = 稳健；~2 以上 = 频繁出错。",
            progressChart: "实线为每局平均目损。指标下降说明你在随着时间推移减少了失误并能更好地寻找最优解。",
            avgPolicyRank: "你的着手与 KataGo 直觉（策略网络）的吻合程度。排名第 1 表示你的选点与 AI 第一直觉完全一致。平均排名越低，说明你的棋感与强力 AI 越接近。注意：排名第 1 不代表没有目损。",
            bestMoveRate: "你的着手与 KataGo 唯一最优解完全一致的比例。即使是高段棋手也很少超过 50%，此指标最适合用来追踪自身的纵向进步。",
            phaseBreakdown: "按对局阶段分别统计的平均目损，采用 KataGo 在 19 路棋盘上的划分标准：布局 = 第 1\u201350 手，中盘 = 第 51\u2013144 手，官子 = 第 145 手以后。若某阶段你的着手不足 5 手，则显示\u201c\u2014\u201d。",
            openingPolicyRank: "仅统计布局阶段（第 1\u201350 手）的平均直觉排名。与全局排名对比，可判断你的布局棋感是强于还是弱于整体水平。",
            histogram: "按 KataGo 目损阈值划分的着手质量：优秀 < 0.5，良好 < 1.5，不准确 < 3，失误 < 6，大失误 < 12，严重失误 \u2265 12。每段色条对应落入该区间的手数。",
            undoTrend: "KataGo 指导棋模式会自动悔棋超过阈值的着手，让你重新落子。此图显示每局触发悔棋的次数。随时间减少，说明你在 KataGo 介入前已能自我纠错。",
        },
    },
    en: {
        title: "Go Training Dashboard",
        liveConnected: "Live updates connected",
        liveDisconnected: "Live updates disconnected",
        loading: "Loading...",

        totalGames: "Total Games",
        avgPointsLost: "Avg Points Lost",
        bestMoveRate: "Best Move Rate",

        progressOverTime: "Progress Over Time",
        matchRates: "Move Match Rates",
        moveQuality: "Move Quality Distribution",
        undoTrend: "Undo Trend",

        // Match rate chart labels
        bestMoveMatch: "AI Best Move Match %",
        top5PolicyMatch: "Top-5 Policy Match %",

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

        // Move quality chart series labels
        goodMovesPct: "Good moves % (per game)",
        goodMovesAvg: "Good moves % (rolling avg)",
        badMovesPct: "Bad moves % (per game)",
        badMovesAvg: "Bad moves % (rolling avg)",

        // Undo chart series labels
        undoAvg: "Undos (rolling avg)",

        // Move quality histogram legend
        moveQualityLegend: "Move Quality",
        humanMoves: "Your moves",

        // Phase breakdown
        phaseBreakdown: "Phase Breakdown",
        phaseOpening: "Opening",
        phaseMidgame: "Midgame",
        phaseEndgame: "Endgame",
        phaseAvgPtsLost: "Avg pts lost",
        openingPolicyRank: "Opening Policy Rank",
        phaseTooFewMoves: "\u2014",

        // Tooltips
        tooltips: {
            avgPointsLost: "Average territory lost per move compared to KataGo's top suggestion. Lower is better. 0 = perfect play; ~1 = solid; ~2+ = frequent mistakes.",
            progressChart: "The solid line is your average points lost per game. A downward trend indicates you are making fewer costly mistakes over time.",
            avgPolicyRank: "How closely your moves match KataGo's intuition (policy network). Rank #1 means your move was the AI's first instinct. Lower average = your moves align more naturally with strong AI intuition. Note: rank #1 doesn't guarantee zero points lost.",
            bestMoveRate: "Percentage of your moves that exactly matched KataGo's single best suggestion. Even strong players score below 50% — best used for tracking your own trend over time.",
            phaseBreakdown: "Average points lost broken down by game phase, using KataGo's boundaries on a 19\u00d719 board: Opening = moves 1\u201350, Midgame = moves 51\u2013144, Endgame = moves 145+. Shows '\u2014' if fewer than 5 of your moves fell in that phase.",
            openingPolicyRank: "Your average policy rank restricted to opening-phase moves only (moves 1\u201350). Compare to your whole-game average to see whether your opening intuition is stronger or weaker than your overall play.",
            histogram: "Move quality buckets based on KataGo point-loss thresholds: Excellent < 0.5, Good < 1.5, Inaccuracy < 3, Mistake < 6, Blunder < 12, Critical \u2265 12. Each colour segment shows how many of your moves fell into that category.",
            undoTrend: "KataGo's teaching mode can auto-undo moves that lose more than a set threshold of points, letting you retry them. This chart shows how many times per game that happened. Fewer undos over time means you are self-correcting before KataGo needs to intervene.",
        },
    }
};
