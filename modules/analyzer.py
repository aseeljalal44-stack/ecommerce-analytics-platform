# modules/analyzer.py
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AnalysisConfig:
    store_type: str = 'general'
    currency: str = 'SAR'
    language: str = 'ar'
    date_format: str = '%Y-%m-%d'
    min_data_points: int = 5

class EcommerceAnalyzer:
    def __init__(self, config: AnalysisConfig = None):
        self.config = config or AnalysisConfig()
        self.dataframe = None
        self.mapping = {}

    def analyze(self, df: pd.DataFrame, mapping: Dict[str,str]) -> Dict[str,Any]:
        self.dataframe = df.copy()
        self.mapping = mapping
        self._clean_data()
        results = {
            'store_profile': self._profile(),
            'sales_performance': self._sales_performance(),
            'customer_analysis': self._customers(),
            'data_quality': self._data_quality()
        }
        return results

    def _clean_data(self):
        # تحويل التاريخ إذا وُجد
        if 'order_date' in self.mapping:
            col = self.mapping['order_date']
            try:
                self.dataframe[col] = pd.to_datetime(self.dataframe[col], errors='coerce')
            except:
                pass
        # تحويل رقمي
        for logical in ['quantity','unit_price','total_amount']:
            if logical in self.mapping:
                col = self.mapping[logical]
                self.dataframe[col] = pd.to_numeric(self.dataframe[col], errors='coerce')

        # إذا لم يوجد total_amount وحضر unit_price و quantity، احسبه
        if 'total_amount' not in self.mapping and 'unit_price' in self.mapping and 'quantity' in self.mapping:
            up = self.mapping['unit_price']; q = self.mapping['quantity']
            self.dataframe['__calc_total'] = self.dataframe[up].fillna(0) * self.dataframe[q].fillna(0)
            self.mapping['total_amount'] = '__calc_total'

    def _profile(self):
        df = self.dataframe
        profile = {
            'store_type': self.config.store_type,
            'total_orders': int(len(df)),
            'unique_customers': 0,
            'unique_products': 0,
            'date_range': {}
        }
        if 'customer_id' in self.mapping:
            profile['unique_customers'] = int(df[self.mapping['customer_id']].nunique())
        if 'product_id' in self.mapping:
            profile['unique_products'] = int(df[self.mapping['product_id']].nunique())
        if 'order_date' in self.mapping:
            s = df[self.mapping['order_date']]
            s = pd.to_datetime(s, errors='coerce')
            s = s.dropna()
            if not s.empty:
                profile['date_range'] = {'start': str(s.min().date()), 'end': str(s.max().date())}
        return profile

    def _sales_performance(self):
        df = self.dataframe
        result = {'total_revenue':0.0, 'average_order_value':0.0, 'orders_count': len(df)}
        if 'total_amount' in self.mapping:
            total = df[self.mapping['total_amount']].fillna(0).sum()
            result['total_revenue'] = float(total)
            if len(df)>0:
                result['average_order_value'] = float(total / len(df))
        return result

    def _customers(self):
        df = self.dataframe
        res = {}
        if 'customer_id' in self.mapping:
            cust = df[self.mapping['customer_id']].dropna()
            res['unique_customers'] = int(cust.nunique())
            # معدلات تكرار طلبات
            orders_per_customer = cust.value_counts().describe().to_dict()
            res['orders_per_customer_summary'] = {k:str(v) for k,v in orders_per_customer.items()}
        return res

    def _data_quality(self):
        df = self.dataframe
        missing = df.isna().mean().to_dict()
        return {'missing_rate_per_column': {k: float(v) for k,v in missing.items()}}