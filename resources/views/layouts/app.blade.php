<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'THALAI - Thalassemia Risk Screening')</title>
    @stack('styles')
    <style>
        :root {
            --bg: #0f1419;
            --surface: #1a2332;
            --border: #2d3a4d;
            --text: #e6edf3;
            --muted: #8b949e;
            --accent: #58a6ff;
            --success: #3fb950;
            --warning: #d29922;
            --danger: #f85149;
        }
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            margin: 0;
            min-height: 100vh;
        }
        .container { max-width: 720px; margin: 0 auto; padding: 2rem 1rem; }
        h1 { font-size: 1.75rem; margin: 0 0 0.5rem; letter-spacing: 0.02em; }
        h2 { font-size: 1.25rem; margin: 1.5rem 0 0.75rem; color: var(--accent); }
        .muted { color: var(--muted); font-size: 0.95rem; }
        .disclaimer {
            background: rgba(210, 153, 34, 0.12);
            border: 1px solid var(--warning);
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 1rem 0;
            font-size: 0.9rem;
            color: #e6c76b;
        }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        label { display: block; margin-bottom: 0.35rem; font-weight: 500; }
        input[type="number"], input[type="text"], select {
            width: 100%;
            padding: 0.5rem 0.75rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: var(--bg);
            color: var(--text);
            font-size: 1rem;
        }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
        .form-group { margin-bottom: 1rem; }
        .btn {
            display: inline-block;
            padding: 0.65rem 1.5rem;
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
        }
        .btn:hover { filter: brightness(1.1); }
        .btn-secondary { background: var(--border); }
        ul.contributions { margin: 0; padding-left: 1.25rem; }
        ul.contributions li { margin-bottom: 0.35rem; }
        table.probs { width: 100%; border-collapse: collapse; }
        table.probs th, table.probs td { padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }
        table.probs .highest { background: rgba(88, 166, 255, 0.15); font-weight: 600; }
        .result-category { font-size: 1.25rem; font-weight: 700; color: var(--accent); margin: 0.5rem 0; }
        .risk-score { font-size: 1.5rem; font-weight: 700; color: var(--warning); }
        .back-link { margin-top: 1rem; }
        .back-link a { color: var(--accent); text-decoration: none; }
        .back-link a:hover { text-decoration: underline; }
        .error-list { color: var(--danger); margin: 0.5rem 0; padding-left: 1.25rem; }
    </style>
</head>
<body>
    <div class="container">
        @yield('content')
    </div>
</body>
</html>
