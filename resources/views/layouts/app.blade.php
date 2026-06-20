<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'THALAI - Thalassemia Risk Screening')</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    @stack('styles')
    <style>
        :root {
            --bg: #07090e;
            --surface: rgba(18, 24, 38, 0.6);
            --border: rgba(255, 255, 255, 0.06);
            --text: #f1f5f9;
            --muted: #94a3b8;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.15);
            --teal: #06b6d4;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --font-heading: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
            --font-body: 'Inter', system-ui, -apple-system, sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-body);
            background: radial-gradient(circle at top right, #0f1526, #07090e);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1.5rem 0;
        }

        .container {
            width: 100%;
            max-width: 680px;
            margin: 0 auto;
            padding: 0 1.25rem;
        }

        h1, h2, h3, h4 {
            font-family: var(--font-heading);
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        h1 {
            font-size: 1.85rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #a5b4fc, #6366f1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }

        h2 {
            font-size: 1.2rem;
            margin-bottom: 0.75rem;
            color: #ffffff;
            font-weight: 500;
        }

        .muted {
            color: var(--muted);
            font-size: 0.9rem;
            font-weight: 300;
        }

        .disclaimer {
            background: rgba(245, 158, 11, 0.06);
            border: 1px solid rgba(245, 158, 11, 0.15);
            border-radius: 8px;
            padding: 0.65rem 0.85rem;
            margin-top: 1rem;
            font-size: 0.82rem;
            color: #fbbf24;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .card {
            background: var(--surface);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
        }

        label {
            display: block;
            margin-bottom: 0.35rem;
            font-weight: 500;
            font-size: 0.82rem;
            color: var(--muted);
            font-family: var(--font-heading);
        }

        input[type="number"], input[type="text"], select {
            width: 100%;
            padding: 0.6rem 0.85rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(8, 12, 21, 0.8);
            color: #ffffff;
            font-size: 0.92rem;
            font-family: var(--font-body);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        input[type="number"]:focus, input[type="text"]:focus, select:focus {
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
            background: rgba(12, 18, 32, 0.9);
            outline: none;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .btn {
            display: inline-block;
            padding: 0.65rem 1.5rem;
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 0.92rem;
            font-weight: 600;
            font-family: var(--font-heading);
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
            text-align: center;
        }

        .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(99, 102, 241, 0.35);
            filter: brightness(1.05);
        }

        .btn:active {
            transform: translateY(0);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text);
            border: 1px solid var(--border);
            box-shadow: none;
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.08);
            box-shadow: none;
            transform: none;
        }

        ul.contributions {
            margin: 0;
            padding-left: 1.25rem;
            font-size: 0.88rem;
            font-weight: 300;
            color: var(--muted);
        }

        ul.contributions li {
            margin-bottom: 0.35rem;
        }

        ul.contributions strong {
            color: var(--text);
            font-weight: 500;
        }

        table.probs {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
            margin: 0.75rem 0;
        }

        table.probs th, table.probs td {
            padding: 0.6rem 0.85rem;
            text-align: left;
        }

        table.probs th {
            font-family: var(--font-heading);
            color: var(--muted);
            border-bottom: 1.5px solid var(--border);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
        }

        table.probs td {
            border-bottom: 1px solid var(--border);
            font-weight: 300;
        }

        table.probs .highest {
            background: rgba(99, 102, 241, 0.08);
            color: #ffffff;
            font-weight: 600;
        }

        table.probs .highest td {
            border-bottom: 1px solid rgba(99, 102, 241, 0.3);
        }

        .result-category {
            font-family: var(--font-heading);
            font-size: 1.45rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0.35rem 0;
            letter-spacing: -0.01em;
        }

        .back-link {
            margin-top: 0.25rem;
        }

        .back-link a {
            color: var(--muted);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
            transition: color 0.2s ease;
        }

        .back-link a:hover {
            color: var(--text);
        }

        .error-list {
            color: var(--danger);
            margin: 0.5rem 0 1rem;
            padding-left: 1.25rem;
            font-size: 0.88rem;
        }

        /* XAI Styling Overhaul */
        .tabs-container {
            margin-top: 1.25rem;
        }

        .tabs-nav {
            display: flex;
            gap: 0.25rem;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border);
            padding: 0.25rem;
            border-radius: 8px;
            margin-bottom: 1.25rem;
        }

        .tab-btn {
            flex: 1;
            background: none;
            border: none;
            color: var(--muted);
            padding: 0.45rem 0.5rem;
            font-size: 0.8rem;
            font-weight: 500;
            font-family: var(--font-heading);
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
            white-space: nowrap;
            text-align: center;
        }

        .tab-btn:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.03);
        }

        .tab-btn.active {
            color: #ffffff;
            background: var(--accent);
            box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .xai-image-container {
            background: #ffffff;
            border-radius: 8px;
            padding: 0.5rem;
            border: 1px solid var(--border);
            text-align: center;
            margin-top: 0.5rem;
        }

        .xai-image {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            display: block;
            margin: 0 auto;
        }

        .shap-bars {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            margin: 1rem 0 1.25rem;
            background: rgba(0, 0, 0, 0.15);
            padding: 1rem 1.25rem;
            border-radius: 10px;
            border: 1px solid var(--border);
        }

        .shap-bar-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.85rem;
        }

        .shap-bar-label {
            width: 125px;
            font-weight: 500;
            font-size: 0.8rem;
            color: var(--text);
            text-align: right;
            text-overflow: ellipsis;
            overflow: hidden;
            white-space: nowrap;
        }

        .shap-bar-track {
            flex-grow: 1;
            height: 12px;
            display: flex;
            position: relative;
            align-items: center;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 3px;
        }

        .shap-bar-fill-left-container {
            width: 50%;
            height: 100%;
            display: flex;
            justify-content: flex-end;
        }

        .shap-bar-fill-right-container {
            width: 50%;
            height: 100%;
            display: flex;
            justify-content: flex-start;
        }

        .shap-bar-center-divider {
            width: 1.5px;
            height: 100%;
            background: var(--muted);
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            z-index: 2;
            opacity: 0.35;
        }

        .shap-bar-fill {
            height: 100%;
            border-radius: 2px;
            transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .shap-bar-fill.positive {
            background: linear-gradient(90deg, #f87171, #ef4444);
        }

        .shap-bar-fill.negative {
            background: linear-gradient(270deg, #60a5fa, #3b82f6);
        }

        .shap-bar-value {
            width: 65px;
            text-align: left;
            font-family: monospace;
            font-size: 0.8rem;
            font-weight: 600;
            padding-left: 0.25rem;
        }

        .shap-bar-value.pos {
            color: #fb7185;
        }

        .shap-bar-value.neg {
            color: #60a5fa;
        }

        .shap-performance-badge {
            display: inline-block;
            padding: 0.15rem 0.45rem;
            font-size: 0.72rem;
            border-radius: 4px;
            font-weight: 600;
            background: rgba(16, 185, 129, 0.08);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.2);
            margin-left: 0.5rem;
            vertical-align: middle;
            font-family: var(--font-heading);
        }

        .shap-performance-badge.slow {
            background: rgba(245, 158, 11, 0.08);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        @yield('content')
    </div>
</body>
</html>
