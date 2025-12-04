"""
وحدة إنشاء التقارير
"""

from datetime import datetime
from typing import Dict, Any
import json


class ReportGenerator:
    """مولد التقارير التحليلية"""
    
    def __init__(self, language: str = 'ar'):
        self.language = language
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """تحميل قوالب التقارير"""
        return {
            'ar': {
                'title': 'تقرير تحليل المتجر الإلكتروني',
                'sections': {
                    'executive_summary': 'الملخص التنفيذي',
                    'performance_analysis': 'تحليل الأداء',
                    'customer_analysis': 'تحليل العملاء',
                    'product_analysis': 'تحليل المنتجات',
                    'financial_analysis': 'التحليل المالي',
                    'recommendations': 'التوصيات',
                    'appendix': 'الملاحق'
                },
                'metrics': {
                    'total_revenue': 'إجمالي الإيرادات',
                    'average_order_value': 'متوسط قيمة الطلب',
                    'total_customers': 'إجمالي العملاء',
                    'repeat_rate': 'معدل التكرار',
                    'gross_margin': 'هامش الربح الإجمالي'
                }
            },
            'en': {
                'title': 'E-commerce Store Analysis Report',
                'sections': {
                    'executive_summary': 'Executive Summary',
                    'performance_analysis': 'Performance Analysis',
                    'customer_analysis': 'Customer Analysis',
                    'product_analysis': 'Product Analysis',
                    'financial_analysis': 'Financial Analysis',
                    'recommendations': 'Recommendations',
                    'appendix': 'Appendix'
                },
                'metrics': {
                    'total_revenue': 'Total Revenue',
                    'average_order_value': 'Average Order Value',
                    'total_customers': 'Total Customers',
                    'repeat_rate': 'Repeat Rate',
                    'gross_margin': 'Gross Margin'
                }
            }
        }
    
    def generate_report(self, analysis_results: Dict, store_type: str) -> str:
        """
        إنشاء تقرير تحليلي كامل
        
        Args:
            analysis_results: نتائج التحليل
            store_type: نوع المتجر
            
        Returns:
            str: التقرير النصي
        """
        template = self.templates.get(self.language, self.templates['ar'])
        
        report_lines = []
        
        # رأس التقرير
        report_lines.append('=' * 80)
        report_lines.append(template['title'])
        report_lines.append('=' * 80)
        report_lines.append(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report_lines.append(f"نوع المتجر: {store_type}")
        report_lines.append('-' * 80)
        
        # الملخص التنفيذي
        report_lines.append(f"\n{template['sections']['executive_summary']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_executive_summary(analysis_results))
        
        # تحليل الأداء
        report_lines.append(f"\n{template['sections']['performance_analysis']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_performance_analysis(analysis_results))
        
        # تحليل العملاء
        report_lines.append(f"\n{template['sections']['customer_analysis']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_customer_analysis(analysis_results))
        
        # تحليل المنتجات
        report_lines.append(f"\n{template['sections']['product_analysis']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_product_analysis(analysis_results))
        
        # التحليل المالي
        report_lines.append(f"\n{template['sections']['financial_analysis']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_financial_analysis(analysis_results))
        
        # التوصيات
        report_lines.append(f"\n{template['sections']['recommendations']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_recommendations(analysis_results))
        
        # الملاحق
        report_lines.append(f"\n{template['sections']['appendix']}")
        report_lines.append('=' * 40)
        report_lines.append(self._generate_appendix(analysis_results))
        
        # تذييل التقرير
        report_lines.append('\n' + '=' * 80)
        report_lines.append("نهاية التقرير")
        report_lines.append('=' * 80)
        
        return '\n'.join(report_lines)
    
    def _generate_executive_summary(self, analysis: Dict) -> str:
        """إنشاء الملخص التنفيذي"""
        profile = analysis.get('store_profile', {})
        performance = analysis.get('sales_performance', {})
        customers = analysis.get('customer_analysis', {})
        
        summary = []
        
        summary.append(f"📊 **ملخص الأداء:**")
        summary.append(f"• إجمالي الطلبات: {profile.get('total_orders', 0):,}")
        summary.append(f"• إجمالي الإيرادات: {performance.get('total_revenue', 0):,.0f} ريال")
        summary.append(f"• عدد العملاء: {customers.get('total_customers', 0):,}")
        
        if 'date_range' in profile:
            date_range = profile['date_range']
            summary.append(f"• فترة التحليل: {date_range.get('start')} إلى {date_range.get('end')}")
        
        summary.append(f"\n🎯 **النقاط الرئيسية:**")
        
        if performance.get('average_order_value', 0) > 0:
            summary.append(f"• متوسط قيمة الطلب: {performance.get('average_order_value', 0):,.0f} ريال")
        
        if customers.get('repeat_rate', 0) > 0:
            summary.append(f"• معدل تكرار الشراء: {customers.get('repeat_rate', 0):.1f}%")
        
        quality = analysis.get('data_quality', {})
        if quality.get('overall_score', 0) > 0:
            summary.append(f"• جودة البيانات: {quality.get('overall_score', 0)}/100")
        
        return '\n'.join(summary)
    
    def _generate_performance_analysis(self, analysis: Dict) -> str:
        """إنشاء تحليل الأداء"""
        performance = analysis.get('sales_performance', {})
        seasonal = analysis.get('seasonal_analysis', {})
        
        report = []
        
        report.append("📈 **مؤشرات الأداء:**")
        report.append(f"• إجمالي الإيرادات: {performance.get('total_revenue', 0):,.0f} ريال")
        report.append(f"• متوسط قيمة الطلب: {performance.get('average_order_value', 0):,.0f} ريال")
        report.append(f"• الطلبات اليومية: {performance.get('orders_per_day', 0):.1f}")
        report.append(f"• الإيرادات اليومية: {performance.get('revenue_per_day', 0):,.0f} ريال")
        
        if seasonal.get('peak_periods'):
            report.append(f"\n📅 **فترات الذروة:**")
            for period in seasonal['peak_periods'][:3]:
                report.append(f"• الشهر {period}")
        
        return '\n'.join(report)
    
    def _generate_customer_analysis(self, analysis: Dict) -> str:
        """إنشاء تحليل العملاء"""
        customers = analysis.get('customer_analysis', {})
        
        report = []
        
        report.append("👥 **تحليل العملاء:**")
        report.append(f"• إجمالي العملاء: {customers.get('total_customers', 0):,}")
        report.append(f"• العملاء المتكررين: {customers.get('repeat_customers', 0):,}")
        report.append(f"• معدل التكرار: {customers.get('repeat_rate', 0):.1f}%")
        
        segments = customers.get('customer_segments', {})
        if segments:
            report.append(f"\n📊 **شرائح العملاء:**")
            report.append(f"• العملاء VIP: {segments.get('vip', 0):,}")
            report.append(f"• العملاء عالي القيمة: {segments.get('high_value', 0):,}")
            report.append(f"• العملاء متوسطي القيمة: {segments.get('medium_value', 0):,}")
            report.append(f"• العملاء منخفضي القيمة: {segments.get('low_value', 0):,}")
        
        return '\n'.join(report)
    
    def _generate_product_analysis(self, analysis: Dict) -> str:
        """إنشاء تحليل المنتجات"""
        products = analysis.get('product_analysis', {})
        
        report = []
        
        report.append("📦 **تحليل المنتجات:**")
        report.append(f"• إجمالي المنتجات: {products.get('total_products', 0):,}")
        
        top_products = products.get('top_products', [])
        if top_products:
            report.append(f"\n🏆 **أفضل المنتجات مبيعاً:**")
            for i, product in enumerate(top_products[:5], 1):
                report.append(f"{i}. {product.get('product', '')}: {product.get('quantity', 0):,} وحدة")
        
        categories = products.get('category_distribution', {})
        if categories:
            report.append(f"\n🏷️ **أفضل الفئات أداءً:**")
            for i, (category, count) in enumerate(list(categories.items())[:3], 1):
                report.append(f"{i}. {category}: {count:,} عملية بيع")
        
        recommendations = products.get('product_recommendations', [])
        if recommendations:
            report.append(f"\n💡 **توصيات المنتجات:**")
            for rec in recommendations[:3]:
                report.append(f"• {rec}")
        
        return '\n'.join(report)
    
    def _generate_financial_analysis(self, analysis: Dict) -> str:
        """إنشاء التحليل المالي"""
        financials = analysis.get('financial_analysis', {})
        profitability = financials.get('profitability', {})
        
        report = []
        
        report.append("💰 **التحليل المالي:**")
        
        if profitability:
            report.append(f"• الإيرادات: {profitability.get('total_revenue', 0):,.0f} ريال")
            report.append(f"• تكلفة البضاعة المباعة (تقديري): {profitability.get('estimated_cogs', 0):,.0f} ريال")
            report.append(f"• الربح الإجمالي: {profitability.get('gross_profit', 0):,.0f} ريال")
            report.append(f"• هامش الربح: {profitability.get('gross_margin', 0):.1f}%")
            report.append(f"• صافي الربح (تقديري): {profitability.get('net_profit_estimate', 0):,.0f} ريال")
        
        benchmarks = analysis.get('benchmarks', {})
        if benchmarks:
            report.append(f"\n📊 **مقارنة مع معايير الصناعة:**")
            report.append(f"• متوسط قيمة الطلب (متجرك): {profitability.get('total_revenue', 0) / analysis.get('store_profile', {}).get('total_orders', 1) if analysis.get('store_profile', {}).get('total_orders', 0) > 0 else 0:,.0f} ريال")
            report.append(f"• متوسط قيمة الطلب (الصناعة): {benchmarks.get('aov', 0):,.0f} ريال")
        
        return '\n'.join(report)
    
    def _generate_recommendations(self, analysis: Dict) -> str:
        """إنشاء التوصيات"""
        recommendations = analysis.get('recommendations', {})
        
        report = []
        
        report.append("🚀 **إجراءات فورية (الأسبوع القادم):**")
        for rec in recommendations.get('immediate', [])[:3]:
            report.append(f"• {rec}")
        
        report.append(f"\n🎯 **أهداف قصيرة المدى (1-3 أشهر):**")
        for rec in recommendations.get('short_term', [])[:3]:
            report.append(f"• {rec}")
        
        report.append(f"\n📅 **استراتيجيات طويلة المدى (3-12 شهر):**")
        for rec in recommendations.get('long_term', [])[:3]:
            report.append(f"• {rec}")
        
        return '\n'.join(report)
    
    def _generate_appendix(self, analysis: Dict) -> str:
        """إنشاء الملاحق"""
        quality = analysis.get('data_quality', {})
        profile = analysis.get('store_profile', {})
        
        report = []
        
        report.append("📋 **معلومات إضافية:**")
        report.append(f"• درجة اكتمال البيانات: {quality.get('completeness_score', 0)}/100")
        report.append(f"• الأيام النشطة: {profile.get('active_days', 0)} يوم")
        
        if 'date_range' in profile:
            report.append(f"• مدة التحليل: {profile['date_range'].get('days', 0)} يوم")
        
        if quality.get('issues'):
            report.append(f"\n⚠️ **مشاكل البيانات المكتشفة:**")
            for issue in quality['issues'][:3]:
                report.append(f"• {issue}")
        
        return '\n'.join(report)
    
    def export_report(self, report_text: str, format: str = 'txt') -> bytes:
        """
        تصدير التقرير بتنسيقات مختلفة
        
        Args:
            report_text: نص التقرير
            format: تنسيق التصدير (txt, json, html)
            
        Returns:
            bytes: التقرير بالمطلوب
        """
        if format == 'json':
            report_data = {
                'generated_at': datetime.now().isoformat(),
                'language': self.language,
                'content': report_text
            }
            return json.dumps(report_data, ensure_ascii=False, indent=2).encode('utf-8')
        
        elif format == 'html':
            html_template = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>تقرير تحليل المتجر الإلكتروني</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    h1 {{ color: #333; border-bottom: 2px solid #4CAF50; }}
                    h2 {{ color: #555; border-bottom: 1px solid #ddd; }}
                    .metric {{ background: #f4f4f4; padding: 10px; margin: 5px 0; }}
                    .recommendation {{ background: #e8f4fd; padding: 10px; margin: 5px 0; }}
                </style>
            </head>
            <body>
                <pre>{report_text}</pre>
            </body>
            </html>
            """
            return html_template.encode('utf-8')
        
        else:  # txt
            return report_text.encode('utf-8')