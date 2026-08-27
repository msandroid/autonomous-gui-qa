"""
Visual QA & Exploration HTML / Markdown Report Generator.
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from .annotator import VisualAnnotator

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ suite_name }} - Visual QA Report</title>
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --text-heading: #f0f6fc;
            --pass: #238636;
            --fail: #da3633;
            --badge-crit: #f85149;
            --badge-high: #db61a2;
            --badge-med: #d29922;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 24px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header {
            border-bottom: 1px solid var(--border);
            padding-bottom: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        h1 { color: var(--text-heading); margin: 0 0 8px 0; font-size: 24px; }
        .timestamp { color: #8b949e; font-size: 13px; }
        .summary-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }
        .card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .card .num { font-size: 32px; font-weight: bold; margin-bottom: 4px; }
        .pass-card .num { color: #3fb950; }
        .fail-card .num { color: #f85149; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 24px;
        }
        .screen-card {
            background-color: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .screen-card.failed { border-color: var(--fail); }
        .screen-header {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-pass { background-color: rgba(35, 134, 54, 0.2); color: #3fb950; }
        .badge-fail { background-color: rgba(218, 54, 51, 0.2); color: #f85149; }
        .img-container {
            background-color: #010409;
            padding: 16px;
            text-align: center;
        }
        .img-container img {
            max-width: 100%;
            max-height: 480px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        .defects-section { padding: 16px; font-size: 13px; }
        .defect-item {
            background: rgba(248, 81, 73, 0.1);
            border-left: 3px solid var(--badge-crit);
            padding: 8px 12px;
            margin-bottom: 8px;
            border-radius: 0 4px 4px 0;
        }
        .rec { color: #8b949e; margin-top: 4px; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>{{ suite_name }}</h1>
                <div class="timestamp">Generated on {{ timestamp }} • Autonomous VLM Inspection Engine</div>
            </div>
            <div class="badge {% if pass_rate == 100.0 %}badge-pass{% else %}badge-fail{% endif %}" style="font-size: 16px; padding: 8px 16px;">
                Pass Rate: {{ pass_rate }}%
            </div>
        </header>

        <div class="summary-cards">
            <div class="card"><div>Total Screens</div><div class="num">{{ total_screens }}</div></div>
            <div class="card pass-card"><div>Passed</div><div class="num">{{ passed_screens }}</div></div>
            <div class="card fail-card"><div>Failed</div><div class="num">{{ failed_screens }}</div></div>
            <div class="card"><div>Total Defects</div><div class="num">{{ total_defects }}</div></div>
        </div>

        <div class="grid">
            {% for item in results %}
            <div class="screen-card {% if not item.is_passed %}failed{% endif %}">
                <div class="screen-header">
                    <strong>{{ item.screen_name }}</strong>
                    <span class="badge {% if item.is_passed %}badge-pass{% else %}badge-fail{% endif %}">
                        {% if item.is_passed %}PASS{% else %}FAIL{% endif %}
                    </span>
                </div>
                <div class="img-container">
                    <img src="{{ item.annotated_image_path or item.image_path }}" alt="{{ item.screen_name }}">
                </div>
                <div class="defects-section">
                    <p><strong>Summary:</strong> {{ item.summary }}</p>
                    {% if item.defects %}
                    <h4>Detected Defects ({{ item.defects|length }})</h4>
                    {% for d in item.defects %}
                    <div class="defect-item">
                        <strong>[{{ d.severity }}] {{ d.category }}</strong>: {{ d.element_description }}<br>
                        <div>{{ d.detail }}</div>
                        <div class="rec">💡 Fix: {{ d.recommendation }}</div>
                    </div>
                    {% endfor %}
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

class QAReporter:
    """Generates HTML & Markdown reports with visual annotations."""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.annotated_dir = os.path.join(output_dir, "annotated_images")
        self.annotator = VisualAnnotator(self.annotated_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self, results: List[Dict[str, Any]], suite_name: str = "Autonomous Visual QA") -> Dict[str, str]:
        # 1. Annotate images
        for r in results:
            if r.get("defects"):
                ann_path = self.annotator.annotate(r["image_path"], r["defects"], r.get("step_name", "step"))
                r["annotated_image_path"] = os.path.relpath(ann_path, self.output_dir)

        total = len(results)
        passed = sum(1 for r in results if r.get("is_passed", False))
        failed = total - passed
        pass_rate = round((passed / total * 100.0), 1) if total > 0 else 0.0
        total_defects = sum(len(r.get("defects", [])) for r in results)

        from jinja2 import Template
        template = Template(HTML_TEMPLATE)
        html_content = template.render(
            suite_name=suite_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_screens=total,
            passed_screens=passed,
            failed_screens=failed,
            pass_rate=pass_rate,
            total_defects=total_defects,
            results=results
        )

        html_file = os.path.join(self.output_dir, "visual_qa_report.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Markdown summary
        pass_icon = "🟢 PASS" if pass_rate == 100.0 else "🔴 FAIL"
        md_lines = [
            f"## {pass_icon} {suite_name}",
            f"**Total Screens:** {total} | **Passed:** {passed} | **Failed:** {failed} | **Pass Rate:** {pass_rate}% | **Defects:** {total_defects}\n",
            "| Screen | Result | Defects | Summary |",
            "| :--- | :--- | :--- | :--- |"
        ]
        for r in results:
            status = "🟢 PASS" if r.get("is_passed") else "🔴 FAIL"
            def_cnt = len(r.get("defects", []))
            md_lines.append(f"| **{r.get(screen_name, Screen)}** | {status} | {def_cnt} | {r.get(summary, )} |")

        md_file = os.path.join(self.output_dir, "summary.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return {
            "html": html_file,
            "markdown": md_file
        }
