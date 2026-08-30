"""
Visualization & Chart Engine Connector for Agent 03.
Generates ASCII & Markdown visual charts and statistical aggregations.
"""

from typing import Any, Dict, List, Optional


class ChartEngineConnector:
    """
    Generates text/markdown formatted visual charts and statistical aggregations.
    """

    def generate_bar_chart(self, title: str, data_points: List[Dict[str, Any]], label_key: str, value_key: str, unit: str = "$") -> str:
        """Generate a visual horizontal bar chart in markdown format."""
        if not data_points:
            return "No data points to render."

        max_val = max(float(p.get(value_key, 0)) for p in data_points) or 1.0
        bar_max_len = 25

        chart_lines = [f"### 📊 {title}", "```text"]
        for p in data_points:
            label = str(p.get(label_key, "Item"))[:20].ljust(20)
            val = float(p.get(value_key, 0))
            bar_len = int((val / max_val) * bar_max_len)
            bar = "█" * bar_len + "░" * (bar_max_len - bar_len)
            chart_lines.append(f"{label} | {bar} | {unit}{val:,.2f}")
        chart_lines.append("```")

        return "\n".join(chart_lines)
