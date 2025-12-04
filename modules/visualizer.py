# modules/visualizer.py
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dataclasses import dataclass
from typing import Dict

@dataclass
class ChartConfig:
    theme: str = 'plotly_white'
    color_scale: str = 'Viridis'
    width: int = 900
    height: int = 420
    language: str = 'ar'

class EcommerceVisualizer:
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()

    def create_kpi_dashboard(self, kpi_data: Dict):
        fig = go.Figure()
        labels = list(kpi_data.keys())
        values = [kpi_data[k] or 0 for k in labels]
        # use bar of 1 row: simple numeric cards via indicators
        for i,(k,v) in enumerate(kpi_data.items()):
            fig.add_trace(go.Indicator(
                mode="number+delta" if i==0 else "number",
                value=v,
                title={'text':k},
                domain={'row':0,'column':i}
            ))
        fig.update_layout(grid={'rows':1,'columns':len(kpi_data)}, height=self.config.height, template=self.config.theme)
        return fig

    def create_sales_trend_chart(self, df: pd.DataFrame, date_col: str, amount_col: str):
        df2 = df.copy()
        df2[date_col] = pd.to_datetime(df2[date_col], errors='coerce')
        df2 = df2.dropna(subset=[date_col])
        daily = df2.groupby(pd.Grouper(key=date_col, freq='D'))[amount_col].sum().reset_index()
        fig = px.line(daily, x=date_col, y=amount_col, title="Sales Trend")
        fig.update_layout(height=self.config.height, template=self.config.theme)
        return fig