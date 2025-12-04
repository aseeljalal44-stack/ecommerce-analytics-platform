"""
وحدة التعرف التلقائي على أعمدة بيانات المتاجر الإلكترونية
"""

import re
import pandas as pd
from typing import Dict, List, Optional


class EcommerceColumnMapper:
    """التعرف الذكي على أعمدة بيانات المتاجر الإلكترونية"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict:
        """تهيئة أنماط التعرف على الأعمدة"""
        return {
            # معاملات المبيعات
            'transaction_id': {
                'patterns': [r'order.?id', r'transaction.?id', r'invoice.?no', r'رقم.?الطلب', r'معرف.?المعاملة'],
                'keywords': ['order', 'transaction', 'invoice', 'رقم طلب', 'id'],
                'priority': 10
            },
            'order_date': {
                'patterns': [r'order.?date', r'purchase.?date', r'created.?at', r'تاريخ.?الطلب', r'تاريخ.?الشراء'],
                'keywords': ['date', 'created', 'تاريخ', 'وقت', 'time'],
                'priority': 9
            },
            
            # معلومات العميل
            'customer_id': {
                'patterns': [r'customer.?id', r'user.?id', r'client.?id', r'رقم.?العميل', r'معرف.?المستخدم'],
                'keywords': ['customer', 'user', 'client', 'عميل', 'مستخدم'],
                'priority': 8
            },
            'customer_email': {
                'patterns': [r'email', r'customer.?email', r'user.?email', r'بريد.?إلكتروني', r'إيميل'],
                'keywords': ['email', 'بريد', 'إيميل'],
                'priority': 7
            },
            
            # معلومات المنتج
            'product_id': {
                'patterns': [r'product.?id', r'item.?id', r'sku', r'variant.?id', r'معرف.?المنتج'],
                'keywords': ['product', 'item', 'sku', 'variant', 'منتج', 'سلعة'],
                'priority': 8
            },
            'product_name': {
                'patterns': [r'product.?name', r'item.?name', r'title', r'اسم.?المنتج', r'عنوان'],
                'keywords': ['product', 'item', 'title', 'name', 'اسم', 'عنوان'],
                'priority': 7
            },
            
            # معلومات مالية
            'quantity': {
                'patterns': [r'quantity', r'qty', r'count', r'الكمية', r'عدد'],
                'keywords': ['quantity', 'qty', 'count', 'كمية', 'عدد'],
                'priority': 6
            },
            'unit_price': {
                'patterns': [r'unit.?price', r'price', r'cost', r'سعر', r'السعر', r'التكلفة'],
                'keywords': ['price', 'cost', 'سعر', 'تكلفة'],
                'priority': 6
            },
            'total_amount': {
                'patterns': [r'total', r'amount', r'revenue', r'المبلغ', r'الإجمالي'],
                'keywords': ['total', 'amount', 'revenue', 'إجمالي', 'مبلغ'],
                'priority': 9
            },
            
            # معلومات إضافية
            'payment_method': {
                'patterns': [r'payment.?method', r'payment.?type', r'طريقة.?الدفع', r'نوع.?الدفع'],
                'keywords': ['payment', 'دفع', 'method', 'طريقة'],
                'priority': 5
            },
            'shipping_address': {
                'patterns': [r'shipping.?address', r'delivery.?address', r'عنوان.?الشحن', r'عنوان.?التوصيل'],
                'keywords': ['shipping', 'delivery', 'address', 'عنوان', 'شحن'],
                'priority': 4
            }
        }
    
    def auto_detect(self, dataframe: pd.DataFrame) -> Dict[str, str]:
        """
        التعرف التلقائي على أعمدة البيانات
        
        Args:
            dataframe: DataFrame يحتوي على بيانات المتجر
            
        Returns:
            dict: تعيين الأعمدة المقترحة
        """
        suggestions = {}
        columns = dataframe.columns.tolist()
        
        # إنشاء سجل المطابقات لكل عمود
        matches = []
        
        for column in columns:
            column_lower = str(column).lower()
            
            for field_type, pattern_info in self.patterns.items():
                score = 0
                
                # التحقق من الأنماط
                for pattern in pattern_info['patterns']:
                    if re.search(pattern, column_lower, re.IGNORECASE):
                        score += 3
                        break
                
                # التحقق من الكلمات المفتاحية
                for keyword in pattern_info['keywords']:
                    if keyword in column_lower:
                        score += 2
                
                # إضافة الأولوية
                if score > 0:
                    score += pattern_info['priority']
                    matches.append({
                        'column': column,
                        'field_type': field_type,
                        'score': score
                    })
        
        # فرز المطابقات حسب النتيجة
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # تعيين الأعمدة مع تجنب التكرار
        assigned_columns = set()
        assigned_fields = set()
        
        for match in matches:
            if (match['column'] not in assigned_columns and 
                match['field_type'] not in assigned_fields):
                suggestions[match['field_type']] = match['column']
                assigned_columns.add(match['column'])
                assigned_fields.add(match['field_type'])
        
        # الكشف عن الأعمدة التاريخية
        date_columns = self._detect_date_columns(dataframe)
        for col in date_columns:
            if 'order_date' not in suggestions:
                suggestions['order_date'] = col
                break
        
        return suggestions
    
    def _detect_date_columns(self, dataframe: pd.DataFrame) -> List[str]:
        """الكشف عن الأعمدة التي تحتوي على تواريخ"""
        date_columns = []
        
        for column in dataframe.columns:
            # التحقق إذا كان العمود من نوع تاريخ
            if pd.api.types.is_datetime64_any_dtype(dataframe[column]):
                date_columns.append(column)
                continue
            
            # محاولة التحويل إلى تاريخ
            try:
                sample = dataframe[column].dropna().head(10)
                if len(sample) > 0:
                    test_dates = pd.to_datetime(sample, errors='coerce')
                    success_rate = test_dates.notna().sum() / len(sample)
                    
                    if success_rate > 0.7:
                        date_columns.append(column)
            except:
                continue
        
        return date_columns
    
    def validate_mapping(self, dataframe: pd.DataFrame, mapping: Dict[str, str]) -> Dict:
        """
        التحقق من صحة تعيين الأعمدة
        
        Args:
            dataframe: DataFrame يحتوي على البيانات
            mapping: تعيين الأعمدة
            
        Returns:
            dict: نتائج التحقق
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': []
        }
        
        # الأعمدة المطلوبة
        required_fields = ['transaction_id', 'order_date', 'total_amount']
        
        # التحقق من الأعمدة المطلوبة
        for field in required_fields:
            if field not in mapping:
                validation_results['missing_required'].append(field)
                validation_results['valid'] = False
        
        # التحقق من وجود الأعمدة في DataFrame
        for field, column in mapping.items():
            if column not in dataframe.columns:
                validation_results['errors'].append(f"العمود '{column}' غير موجود في البيانات")
                validation_results['valid'] = False
        
        # التحقق من أنواع البيانات
        if 'total_amount' in mapping:
            amount_col = mapping['total_amount']
            if amount_col in dataframe.columns:
                try:
                    pd.to_numeric(dataframe[amount_col], errors='raise')
                except:
                    validation_results['warnings'].append(f"العمود '{amount_col}' قد لا يحتوي على قيم رقمية")
        
        return validation_results