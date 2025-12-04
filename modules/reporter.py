# modules/reporter.py
from datetime import datetime
from typing import Dict

class ReportGenerator:
    def __init__(self, language: str = 'ar'):
        self.language = language

    def generate_report(self, analysis_results: Dict, store_type: str) -> str:
        title = "E-commerce Analysis Report" if self.language=='en' else "تقرير تحليل المتجر الإلكتروني"
        lines = [("="*60), title, "="*60]
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append(f"Store type: {store_type}")
        lines.append("\n-- Profile --")
        for k,v in analysis_results.get('store_profile',{}).items():
            lines.append(f"{k}: {v}")
        lines.append("\n-- Sales --")
        for k,v in analysis_results.get('sales_performance',{}).items():
            lines.append(f"{k}: {v}")
        lines.append("\n-- Data quality --")
        dq = analysis_results.get('data_quality',{})
        lines.append(str(dq))
        lines.append("\nEnd of report")
        return "\n".join(lines)