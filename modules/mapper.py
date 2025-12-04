# modules/mapper.py
import re
import pandas as pd
from typing import Dict

class EcommerceColumnMapper:
    """تعيين أعمدة ذكي بسيط"""
    DEFAULT_PATTERNS = {
        'order_id': [r'order[_\s]?id', r'orderid', r'طلب'],
        'order_date': [r'order[_\s]?date', r'date', r'created_at', r'تاريخ'],
        'customer_id': [r'customer[_\s]?id', r'user[_\s]?id', r'client'],
        'customer_email': [r'email', r'بريد'],
        'product_id': [r'product[_\s]?id', r'sku', r'item[_\s]?id'],
        'product_name': [r'product[_\s]?name', r'name', r'title'],
        'quantity': [r'quantity', r'qty', r'count', r'عدد', r'كمية'],
        'unit_price': [r'unit[_\s]?price', r'price', r'سعر', r'cost'],
        'total_amount': [r'total', r'total[_\s]?amount', r'amount', r'revenue', r'المبلغ', r'إجمالي']
    }

    def __init__(self, patterns: Dict = None):
        self.patterns = patterns or self.DEFAULT_PATTERNS

    def auto_map(self, df: pd.DataFrame) -> Dict[str,str]:
        cols = [str(c) for c in df.columns]
        cols_lower = [c.lower() for c in cols]
        mapping = {}

        for logical, pats in self.patterns.items():
            for i,c in enumerate(cols_lower):
                for p in pats:
                    if re.search(p, c, flags=re.IGNORECASE):
                        mapping[logical] = cols[i]
                        break
                if logical in mapping:
                    break
        # إذا لم يعثر على 'total_amount' حاول حسابه
        if 'total_amount' not in mapping:
            # حاول العثور على price و quantity لعمل combo لاحقاً
            if 'unit_price' in mapping and 'quantity' in mapping:
                mapping['total_amount'] = mapping['unit_price']  # ستتعامل analyzer مع الحساب
        return mapping

# Alias للتوافق مع استيراد سابق اسمه ColumnMapper
class ColumnMapper(EcommerceColumnMapper):
    pass