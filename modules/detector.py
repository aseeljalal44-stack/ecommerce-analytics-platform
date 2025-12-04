"""
وحدة الكشف عن نوع المتجر الإلكتروني
"""

import re
import pandas as pd
from typing import Dict, List, Tuple

class StoreTypeDetector:
"""كشف نوع المتجر من خلال تحليل أسماء الأعمدة وعينات البيانات"""

# أنماط للكشف عن أنواع المتاجر  
STORE_PATTERNS = {  
    'fashion': {  
        'column_keywords': ['size', 'color', 'variant', 'dress', 'shirt', 'pants', 'fashion', 'clothing'],  
        'value_patterns': [r'XS|S|M|L|XL|XXL', r'red|blue|green|black|white'],  
        'category_keywords': ['clothing', 'apparel', 'wear', 'fashion']  
    },  
    'electronics': {  
        'column_keywords': ['model', 'spec', 'warranty', 'tech', 'gadget', 'device'],  
        'value_patterns': [r'\d+GB', r'\d+MP', r'\d+"', r'\d+GHz'],  
        'category_keywords': ['electronics', 'tech', 'gadgets', 'devices']  
    },  
    'beauty': {  
        'column_keywords': ['skin', 'type', 'ml', 'oz', 'ingredient', 'beauty', 'cosmetic'],  
        'value_patterns': [r'\d+ml', r'\d+oz', r'dry|oily|normal|combination'],  
        'category_keywords': ['beauty', 'cosmetics', 'skincare', 'makeup']  
    },  
    'home_garden': {  
        'column_keywords': ['room', 'size', 'material', 'dimension', 'home', 'garden'],  
        'value_patterns': [r'\d+x\d+x\d+', r'wood|metal|plastic|fabric'],  
        'category_keywords': ['home', 'garden', 'furniture', 'decor']  
    },  
    'digital': {  
        'column_keywords': ['license', 'download', 'digital', 'file', 'format'],  
        'value_patterns': [r'PDF|MP3|MP4|ZIP', r'\d+\.\d+MB', r'\d+\.\d+GB'],  
        'category_keywords': ['digital', 'download', 'software', 'ebook']  
    },  
    'subscription': {  
        'column_keywords': ['subscription', 'renewal', 'plan', 'monthly', 'yearly'],  
        'value_patterns': [r'monthly|yearly|quarterly', r'plan A|plan B|plan C'],  
        'category_keywords': ['subscription', 'membership', 'plan']  
    },  
    'handmade': {  
        'column_keywords': ['handmade', 'craft', 'artisan', 'material', 'unique'],  
        'value_patterns': [r'handmade|handcrafted', r'limited edition'],  
        'category_keywords': ['handmade', 'craft', 'artisan', 'unique']  
    },  
    'food': {  
        'column_keywords': ['expiry', 'ingredient', 'weight', 'nutrition', 'food'],  
        'value_patterns': [r'\d+g', r'\d+kg', r'\d+calories', r'organic|gluten-free'],  
        'category_keywords': ['food', 'beverage', 'snack', 'grocery']  
    }  
}  
  
def detect(self, dataframe: pd.DataFrame) -> Tuple[str, Dict]:  
    """  
    كشف نوع المتجر من البيانات  
      
    Args:  
        dataframe: DataFrame يحتوي على بيانات المتجر  
          
    Returns:  
        tuple: (نوع المتجر, درجة الثقة لكل نوع)  
    """  
    column_names = [str(col).lower() for col in dataframe.columns]  
      
    # حساب درجة لكل نوع متجر  
    scores = {store_type: 0 for store_type in self.STORE_PATTERNS}  
      
    # الكشف بناءً على أسماء الأعمدة  
    for store_type, patterns in self.STORE_PATTERNS.items():  
        for keyword in patterns['column_keywords']:  
            if any(keyword in col_name for col_name in column_names):  
                scores[store_type] += 2  
      
    # الكشف بناءً على قيم العينة  
    sample_data = dataframe.head(20)  
      
    for store_type, patterns in self.STORE_PATTERNS.items():  
        for column in dataframe.columns:  
            if dataframe[column].dtype == 'object':  
                column_values = sample_data[column].astype(str).str.lower()  
                  
                for pattern in patterns['value_patterns']:  
                    matches = column_values.str.contains(pattern, na=False).sum()  
                    if matches > 0:  
                        scores[store_type] += matches * 0.5  
      
    # الكشف بناءً على عمود الفئة إذا وجد  
    category_columns = [col for col in column_names if 'categor' in col or 'type' in col]  
      
    for cat_col in category_columns[:1]:  # أول عمود فئة فقط  
        if cat_col in dataframe.columns:  
            categories = dataframe[cat_col].dropna().astype(str).str.lower().unique()  
              
            for store_type, patterns in self.STORE_PATTERNS.items():  
                for keyword in patterns['category_keywords']:  
                    if any(keyword in str(cat) for cat in categories):  
                        scores[store_type] += 3  
      
    # تحديد النوع بأعلى درجة  
    if not any(scores.values()):  
        return 'general', scores  
      
    detected_type = max(scores.items(), key=lambda x: x[1])  
      
    # تطبيع الدرجات  
    total_score = sum(scores.values())  
    confidence_scores = {k: (v / total_score * 100) if total_score > 0 else 0   
                       for k, v in scores.items()}  
      
    return detected_type[0], confidence_scores  
  
def get_store_type_display_name(self, store_type: str, language: str = 'ar') -> str:  
    """الحصول على اسم العرض لنوع المتجر"""  
    display_names = {  
        'ar': {  
            'fashion': '👗 متاجر الأزياء',  
            'electronics': '📱 متاجر الإلكترونيات',  
            'beauty': '💄 متاجر التجميل',  
            'home_garden': '🏠 متاجر المنزل والحديقة',  
            'digital': '💻 متاجر المنتجات الرقمية',  
            'subscription': '🔄 متاجر الاشتراكات',  
            'handmade': '🎨 متاجر المنتجات اليدوية',  
            'food': '🍎 متاجر الأطعمة',  
            'general': '🛒 متجر عام'  
        },  
        'en': {  
            'fashion': '👗 Fashion Stores',  
            'electronics': '📱 Electronics Stores',  
            'beauty': '💄 Beauty Stores',  
            'home_garden': '🏠 Home & Garden Stores',  
            'digital': '💻 Digital Products Stores',  
            'subscription': '🔄 Subscription Stores',  
            'handmade': '🎨 Handmade Products Stores',  
            'food': '🍎 Food Stores',  
            'general': '🛒 General Store'  
        }  
    }  
      
    return display_names.get(language, {}).get(store_type, store_type)