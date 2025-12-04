"""
الوحدة الرئيسية لتحليل بيانات المتاجر الإلكترونية
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AnalysisConfig:
    """تكوين تحليل البيانات"""
    store_type: str = 'general'
    currency: str = 'SAR'
    language: str = 'ar'
    date_format: str = '%Y-%m-%d'
    include_benchmarks: bool = True
    min_data_points: int = 10


class EcommerceAnalyzer:
    """المحلل الرئيسي لبيانات المتاجر الإلكترونية"""
    
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.dataframe = None
        self.mapping = None
        self.results = {}
    
    def analyze(self, dataframe: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        إجراء التحليل الشامل
        
        Args:
            dataframe: بيانات المتجر
            mapping: تعيين الأعمدة
            
        Returns:
            dict: نتائج التحليل
        """
        self.dataframe = dataframe.copy()
        self.mapping = mapping
        
        # تنظيف البيانات
        self._clean_data()
        
        # إجراء التحليلات
        self.results = {
            'store_profile': self._analyze_store_profile(),
            'sales_performance': self._analyze_sales_performance(),
            'customer_analysis': self._analyze_customers(),
            'product_analysis': self._analyze_products(),
            'financial_analysis': self._analyze_financials(),
            'marketing_analysis': self._analyze_marketing(),
            'inventory_analysis': self._analyze_inventory(),
            'seasonal_analysis': self._analyze_seasonality(),
            'benchmarks': self._get_benchmarks(),
            'recommendations': self._generate_recommendations(),
            'data_quality': self._assess_data_quality()
        }
        
        return self.results
    
    def _clean_data(self):
        """تنظيف البيانات الأولية"""
        # تحويل التواريخ
        if 'order_date' in self.mapping:
            date_col = self.mapping['order_date']
            self.dataframe[date_col] = pd.to_datetime(
                self.dataframe[date_col], errors='coerce'
            )
        
        # تحويل القيم الرقمية
        numeric_fields = ['quantity', 'unit_price', 'total_amount', 'discount_amount']
        
        for field in numeric_fields:
            if field in self.mapping:
                col = self.mapping[field]
                self.dataframe[col] = pd.to_numeric(self.dataframe[col], errors='coerce')
    
    def _analyze_store_profile(self) -> Dict:
        """تحليل ملف المتجر"""
        profile = {
            'store_type': self.config.store_type,
            'analysis_date': datetime.now().strftime(self.config.date_format),
            'total_orders': len(self.dataframe),
            'date_range': {},
            'active_days': 0
        }
        
        # نطاق التاريخ
        if 'order_date' in self.mapping:
            date_col = self.mapping['order_date']
            dates = self.dataframe[date_col].dropna()
            
            if len(dates) > 0:
                min_date = dates.min()
                max_date = dates.max()
                
                profile['date_range'] = {
                    'start': min_date.strftime(self.config.date_format),
                    'end': max_date.strftime(self.config.date_format),
                    'days': (max_date - min_date).days
                }
                
                # حساب الأيام النشطة
                active_days = dates.dt.normalize().nunique()
                profile['active_days'] = int(active_days)
        
        # حساب عدد العملاء الفريدين
        if 'customer_id' in self.mapping:
            customer_col = self.mapping['customer_id']
            unique_customers = self.dataframe[customer_col].nunique()
            profile['unique_customers'] = int(unique_customers)
        
        # حساب عدد المنتجات الفريدة
        if 'product_id' in self.mapping:
            product_col = self.mapping['product_id']
            unique_products = self.dataframe[product_col].nunique()
            profile['unique_products'] = int(unique_products)
        
        return profile
    
    def _analyze_sales_performance(self) -> Dict:
        """تحليل أداء المبيعات"""
        performance = {
            'total_revenue': 0,
            'average_order_value': 0,
            'orders_per_day': 0,
            'revenue_per_day': 0
        }
        
        if 'total_amount' in self.mapping:
            amount_col = self.mapping['total_amount']
            revenue = self.dataframe[amount_col].sum()
            performance['total_revenue'] = float(revenue)
            
            # متوسط قيمة الطلب
            if len(self.dataframe) > 0:
                performance['average_order_value'] = float(revenue / len(self.dataframe))
        
        # المبيعات اليومية
        if 'order_date' in self.mapping and performance['total_revenue'] > 0:
            date_col = self.mapping['order_date']
            active_days = self.results['store_profile']['active_days']
            
            if active_days > 0:
                performance['orders_per_day'] = len(self.dataframe) / active_days
                performance['revenue_per_day'] = performance['total_revenue'] / active_days
        
        return performance
    
    def _analyze_customers(self) -> Dict:
        """تحليل العملاء"""
        customers = {
            'total_customers': 0,
            'repeat_customers': 0,
            'repeat_rate': 0,
            'customer_segments': {}
        }
        
        if 'customer_id' in self.mapping:
            customer_col = self.mapping['customer_id']
            total_customers = self.dataframe[customer_col].nunique()
            customers['total_customers'] = int(total_customers)
            
            # العملاء المتكررين
            customer_counts = self.dataframe[customer_col].value_counts()
            repeat_customers = (customer_counts > 1).sum()
            customers['repeat_customers'] = int(repeat_customers)
            
            if total_customers > 0:
                customers['repeat_rate'] = float(repeat_customers / total_customers * 100)
            
            # تحليل شرائح العملاء (إذا توفرت بيانات المبيعات)
            if 'total_amount' in self.mapping:
                amount_col = self.mapping['total_amount']
                customer_revenue = self.dataframe.groupby(customer_col)[amount_col].sum()
                
                # تقسيم العملاء حسب الإنفاق
                segments = {
                    'vip': customer_revenue[customer_revenue >= customer_revenue.quantile(0.9)].count(),
                    'high_value': customer_revenue[(customer_revenue >= customer_revenue.quantile(0.7)) & 
                                                  (customer_revenue < customer_revenue.quantile(0.9))].count(),
                    'medium_value': customer_revenue[(customer_revenue >= customer_revenue.quantile(0.4)) & 
                                                    (customer_revenue < customer_revenue.quantile(0.7))].count(),
                    'low_value': customer_revenue[customer_revenue < customer_revenue.quantile(0.4)].count()
                }
                
                customers['customer_segments'] = segments
        
        return customers
    
    def _analyze_products(self) -> Dict:
        """تحليل المنتجات"""
        products = {
            'total_products': 0,
            'top_products': [],
            'category_distribution': {},
            'product_recommendations': []
        }
        
        if 'product_id' in self.mapping:
            product_col = self.mapping['product_id']
            products['total_products'] = self.dataframe[product_col].nunique()
        
        # أفضل المنتجات مبيعاً
        if 'product_name' in self.mapping and 'quantity' in self.mapping:
            product_name_col = self.mapping['product_name']
            quantity_col = self.mapping['quantity']
            
            product_sales = self.dataframe.groupby(product_name_col)[quantity_col].sum()
            top_products = product_sales.sort_values(ascending=False).head(10)
            
            for product, quantity in top_products.items():
                products['top_products'].append({
                    'product': str(product),
                    'quantity': int(quantity)
                })
        
        # توزيع الفئات
        if 'product_category' in self.mapping:
            category_col = self.mapping['product_category']
            category_dist = self.dataframe[category_col].value_counts().head(10)
            products['category_distribution'] = category_dist.to_dict()
        
        # توصيات المنتجات حسب نوع المتجر
        products['product_recommendations'] = self._get_product_recommendations()
        
        return products
    
    def _get_product_recommendations(self) -> List[str]:
        """الحصول على توصيات المنتجات حسب نوع المتجر"""
        recommendations = {
            'fashion': [
                "إضافة مجموعات متكاملة (Outfits)",
                "عرض المنتجات المتطابقة",
                "تحسين صور المنتجات بزوايا متعددة",
                "إضافة دليل المقاسات"
            ],
            'electronics': [
                "إضافة مقارنة بين المنتجات",
                "عرض الملحقات الموصى بها",
                "تقديم دليل المستخدم الرقمي",
                "عرض المنتجات المتوافقة"
            ],
            'beauty': [
                "إضافة دليل اختيار المنتجات حسب نوع البشرة",
                "عرض المنتجات المستخدمة معاً",
                "تقديم عينات تجريبية",
                "إضافة فيديو توضيحي للاستخدام"
            ],
            'general': [
                "تحسين توصيف المنتجات",
                "إضافة مراجعات العملاء",
                "تحسين صور المنتجات",
                "إضافة أسئلة وأجوبة عن المنتجات"
            ]
        }
        
        return recommendations.get(self.config.store_type, recommendations['general'])
    
    def _analyze_financials(self) -> Dict:
        """تحليل البيانات المالية"""
        financials = {
            'revenue_breakdown': {},
            'estimated_costs': {},
            'profitability': {},
            'financial_health': {}
        }
        
        if 'total_amount' in self.mapping:
            amount_col = self.mapping['total_amount']
            total_revenue = self.dataframe[amount_col].sum()
            
            # تقدير التكاليف بناءً على نوع المتجر
            cost_ratios = {
                'fashion': 0.35,
                'electronics': 0.65,
                'beauty': 0.30,
                'digital': 0.10,
                'subscription': 0.40,
                'handmade': 0.45,
                'food': 0.55,
                'general': 0.50
            }
            
            cost_ratio = cost_ratios.get(self.config.store_type, 0.50)
            estimated_cogs = total_revenue * cost_ratio
            gross_profit = total_revenue - estimated_cogs
            gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            financials['profitability'] = {
                'total_revenue': float(total_revenue),
                'estimated_cogs': float(estimated_cogs),
                'gross_profit': float(gross_profit),
                'gross_margin': float(gross_margin),
                'net_profit_estimate': float(gross_profit * 0.7)  # افتراض مصاريف تشغيلية 30%
            }
        
        return financials
    
    def _analyze_marketing(self) -> Dict:
        """تحليل قنوات التسويق"""
        marketing = {
            'channels': {},
            'conversion_metrics': {},
            'marketing_recommendations': []
        }
        
        # تحليل القنوات إذا توفرت البيانات
        if 'traffic_source' in self.mapping:
            source_col = self.mapping['traffic_source']
            if source_col in self.dataframe.columns:
                channel_dist = self.dataframe[source_col].value_counts().head(5)
                marketing['channels'] = channel_dist.to_dict()
        
        # توصيات التسويق
        marketing_recommendations = {
            'fashion': [
                "استخدام Instagram Shopping",
                "تشغيل حملات Lookalike Audiences",
                "إنشاء محتوى فيديو للمنتجات",
                "التعاون مع المؤثرين في المجال"
            ],
            'electronics': [
                "إنشاء محتوى تعليمي (Tutorials)",
                "استخدام Google Shopping Ads",
                "تقديم عروض الحزم (Bundles)",
                "إنشاء مقارنات بين المنتجات"
            ],
            'general': [
                "تحسين SEO للمنتجات",
                "استخدام التسويق عبر البريد الإلكتروني",
                "تقديم عروض ترحيبية",
                "تحسين تجربة الموبايل"
            ]
        }
        
        marketing['marketing_recommendations'] = marketing_recommendations.get(
            self.config.store_type, marketing_recommendations['general']
        )
        
        return marketing
    
    def _analyze_inventory(self) -> Dict:
        """تحليل المخزون"""
        inventory = {
            'stock_status': {},
            'turnover_estimate': 0,
            'inventory_recommendations': []
        }
        
        # تقدير معدل دوران المخزون (بناءً على معايير الصناعة)
        turnover_rates = {
            'fashion': 4.5,
            'electronics': 6.2,
            'beauty': 3.8,
            'food': 12.0,
            'general': 5.0
        }
        
        inventory['turnover_estimate'] = turnover_rates.get(self.config.store_type, 5.0)
        
        # توصيات إدارة المخزون
        inventory_recommendations = [
            "تنفيذ نظام إدارة المخزون الآلي",
            "ضبط مستويات إعادة الطلب",
            "تحليل المنتجات بطيئة الحركة",
            "تنفيذ عروض التخليص للمخزون القديم"
        ]
        
        inventory['inventory_recommendations'] = inventory_recommendations
        
        return inventory
    
    def _analyze_seasonality(self) -> Dict:
        """تحليل الموسمية"""
        seasonality = {
            'monthly_trends': {},
            'weekly_patterns': {},
            'peak_periods': []
        }
        
        if 'order_date' in self.mapping and 'total_amount' in self.mapping:
            date_col = self.mapping['order_date']
            amount_col = self.mapping['total_amount']
            
            # تحليل الاتجاهات الشهرية
            self.dataframe['month'] = self.dataframe[date_col].dt.month
            monthly_sales = self.dataframe.groupby('month')[amount_col].sum()
            seasonality['monthly_trends'] = monthly_sales.to_dict()
            
            # تحليل الأنماط الأسبوعية
            self.dataframe['day_of_week'] = self.dataframe[date_col].dt.day_name()
            weekly_patterns = self.dataframe.groupby('day_of_week')[amount_col].sum()
            seasonality['weekly_patterns'] = weekly_patterns.to_dict()
            
            # تحديد فترات الذروة
            if len(monthly_sales) > 0:
                peak_months = monthly_sales.nlargest(3).index.tolist()
                seasonality['peak_periods'] = peak_months
        
        return seasonality
    
    def _get_benchmarks(self) -> Dict:
        """الحصول على معايير الصناعة"""
        benchmarks = {
            'fashion': {
                'aov': 85.20,
                'conversion_rate': 1.8,
                'repeat_rate': 28.5,
                'cart_abandonment': 68.8
            },
            'electronics': {
                'aov': 120.50,
                'conversion_rate': 1.5,
                'repeat_rate': 22.3,
                'cart_abandonment': 71.3
            },
            'beauty': {
                'aov': 45.80,
                'conversion_rate': 2.1,
                'repeat_rate': 35.2,
                'cart_abandonment': 67.4
            },
            'general': {
                'aov': 75.00,
                'conversion_rate': 1.8,
                'repeat_rate': 25.0,
                'cart_abandonment': 69.6
            }
        }
        
        return benchmarks.get(self.config.store_type, benchmarks['general'])
    
    def _generate_recommendations(self) -> Dict[str, List[str]]:
        """إنشاء توصيات مخصصة"""
        recommendations = {
            'immediate': [
                "تحسين صفحة المنتج",
                "تحسين عملية الدفع",
                "إضافة مراجعات العملاء",
                "تحسين سرعة الموقع"
            ],
            'short_term': [
                "زيادة معدل التحويل بنسبة 10%",
                "خفض معدل هجر عربة التسوق",
                "زيادة قيمة الطلب المتوسطة",
                "تحسين تجربة العملاء على الموبايل"
            ],
            'long_term': [
                "بناء برنامج ولاء للعملاء",
                "التوسع في قنوات بيع جديدة",
                "تنويع مصادر الإيرادات",
                "بناء علامة تجارية قوية"
            ]
        }
        
        return recommendations
    
    def _assess_data_quality(self) -> Dict:
        """تقييم جودة البيانات"""
        quality = {
            'completeness_score': 0,
            'accuracy_score': 0,
            'consistency_score': 0,
            'overall_score': 0,
            'issues': []
        }
        
        # حساب اكتمال البيانات
        total_cells = self.dataframe.size
        missing_cells = self.dataframe.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        quality['completeness_score'] = int(completeness * 100)
        
        # التحقق من دقة البيانات
        if 'total_amount' in self.mapping:
            amount_col = self.mapping['total_amount']
            negative_amounts = (self.dataframe[amount_col] < 0).sum()
            if negative_amounts > 0:
                quality['issues'].append(f"يوجد {negative_amounts} معاملة بمبلغ سالب")
        
        # حساب الدرجة العامة
        quality['overall_score'] = int(quality['completeness_score'] * 0.7)
        
        return quality