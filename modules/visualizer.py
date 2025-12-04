"""
وحدة إنشاء الرسوم البيانية والتصورات
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ChartConfig:
    """تكوين الرسوم البيانية"""
    theme: str = 'plotly_white'
    color_scale: str = 'Viridis'
    width: int = 800
    height: int = 400
    language: str = 'ar'


class EcommerceVisualizer:
    """إنشاء تصورات بيانات المتاجر الإلكترونية"""
    
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
    
    def create_kpi_dashboard(self, kpi_data: Dict) -> go.Figure:
        """إنشاء لوحة مؤشرات الأداء"""
        fig = go.Figure()
        
        # مؤشرات الأداء الرئيسية
        indicators = []
        
        if 'total_revenue' in kpi_data:
            indicators.append(('💰 الإيرادات', kpi_data['total_revenue'], 'SAR'))
        
        if 'average_order_value' in kpi_data:
            indicators.append(('📊 متوسط الطلب', kpi_data['average_order_value'], 'SAR'))
        
        if 'total_customers' in kpi_data:
            indicators.append(('👥 العملاء', kpi_data['total_customers'], ''))
        
        if 'total_products' in kpi_data:
            indicators.append(('📦 المنتجات', kpi_data['total_products'], ''))
        
        # إنشاء مؤشرات
        for i, (title, value, suffix) in enumerate(indicators):
            fig.add_trace(go.Indicator(
                mode="number",
                value=value,
                title={'text': title, 'font': {'size': 18}},
                number={'valueformat': f',.0f{suffix}', 'font': {'size': 36}},
                domain={'row': i // 2, 'column': i % 2}
            ))
        
        fig.update_layout(
            grid={'rows': 2, 'columns': 2, 'pattern': "independent"},
            title="📊 مؤشرات الأداء الرئيسية",
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig
    
    def create_sales_trend_chart(self, sales_data: pd.DataFrame, 
                                date_col: str, amount_col: str) -> go.Figure:
        """إنشاء مخطط اتجاه المبيعات"""
        # تجميع المبيعات حسب التاريخ
        sales_data['date'] = pd.to_datetime(sales_data[date_col])
        daily_sales = sales_data.groupby(pd.Grouper(key='date', freq='D'))[amount_col].sum().reset_index()
        
        fig = px.line(
            daily_sales,
            x='date',
            y=amount_col,
            title='📈 اتجاه المبيعات اليومية',
            labels={'date': 'التاريخ', amount_col: 'المبيعات (SAR)'}
        )
        
        fig.update_traces(mode='lines+markers', line=dict(width=3))
        fig.update_layout(
            height=self.config.height,
            template=self.config.theme,
            hovermode='x unified'
        )
        
        return fig
    
    def create_top_products_chart(self, products_data: pd.DataFrame,
                                 product_col: str, quantity_col: str) -> go.Figure:
        """إنشاء مخطط أفضل المنتجات مبيعاً"""
        # تجميع مبيعات المنتجات
        product_sales = products_data.groupby(product_col)[quantity_col].sum().reset_index()
        top_products = product_sales.nlargest(10, quantity_col)
        
        fig = px.bar(
            top_products,
            x=quantity_col,
            y=product_col,
            orientation='h',
            color=quantity_col,
            color_continuous_scale=self.config.color_scale,
            title='🏆 أفضل 10 منتجات مبيعاً'
        )
        
        fig.update_layout(
            xaxis_title='الكمية المباعة',
            yaxis_title='المنتج',
            height=self.config.height,
            template=self.config.theme,
            coloraxis_showscale=False
        )
        
        return fig
    
    def create_customer_segments_chart(self, segments: Dict) -> go.Figure:
        """إنشاء مخطط شرائح العملاء"""
        labels = ['VIP', 'عالية القيمة', 'متوسطة القيمة', 'منخفضة القيمة']
        values = [
            segments.get('vip', 0),
            segments.get('high_value', 0),
            segments.get('medium_value', 0),
            segments.get('low_value', 0)
        ]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker=dict(colors=colors),
            textinfo='percent+label'
        )])
        
        fig.update_layout(
            title='👥 توزيع شرائح العملاء',
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig
    
    def create_category_distribution_chart(self, categories: Dict) -> go.Figure:
        """إنشاء مخطط توزيع الفئات"""
        if not categories:
            return None
        
        # تحويل القاموس إلى DataFrame
        df = pd.DataFrame(list(categories.items()), columns=['category', 'count'])
        df = df.nlargest(8, 'count')
        
        fig = px.bar(
            df,
            x='category',
            y='count',
            color='count',
            color_continuous_scale='Blues',
            title='🏷️ توزيع المبيعات حسب الفئة'
        )
        
        fig.update_layout(
            xaxis_title='الفئة',
            yaxis_title='عدد المبيعات',
            height=self.config.height,
            template=self.config.theme,
            coloraxis_showscale=False
        )
        
        return fig
    
    def create_seasonality_chart(self, monthly_trends: Dict) -> go.Figure:
        """إنشاء مخطط الموسمية"""
        if not monthly_trends:
            return None
        
        months_arabic = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        
        # ترتيب البيانات حسب الشهر
        months = list(range(1, 13))
        sales = [monthly_trends.get(m, 0) for m in months]
        
        fig = px.line(
            x=months_arabic,
            y=sales,
            markers=True,
            title='📅 الأنماط الموسمية للمبيعات'
        )
        
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            xaxis_title='الشهر',
            yaxis_title='المبيعات',
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig
    
    def create_benchmark_comparison_chart(self, store_kpis: Dict, benchmarks: Dict) -> go.Figure:
        """إنشاء مخطط مقارنة مع معايير الصناعة"""
        metrics = ['متوسط قيمة الطلب', 'معدل التحويل', 'معدل التكرار']
        
        store_values = [
            store_kpis.get('aov', 0),
            store_kpis.get('conversion_rate', 0),
            store_kpis.get('repeat_rate', 0)
        ]
        
        benchmark_values = [
            benchmarks.get('aov', 0),
            benchmarks.get('conversion_rate', 0),
            benchmarks.get('repeat_rate', 0)
        ]
        
        fig = go.Figure(data=[
            go.Bar(name='متجرك', x=metrics, y=store_values, marker_color='indianred'),
            go.Bar(name='متوسط الصناعة', x=metrics, y=benchmark_values, marker_color='lightseagreen')
        ])
        
        fig.update_layout(
            barmode='group',
            title='📊 مقارنة مع معايير الصناعة',
            yaxis_title='القيمة',
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig
    
    def create_data_quality_gauge(self, quality_score: int) -> go.Figure:
        """إنشاء مقياس جودة البيانات"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=quality_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "جودة البيانات", 'font': {'size': 24}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "red"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': quality_score
                }
            }
        ))
        
        fig.update_layout(
            height=self.config.height,
            template=self.config.theme
        )
        
        return fig