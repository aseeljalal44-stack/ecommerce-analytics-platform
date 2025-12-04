"""
اختبار وحدة كشف نوع المتجر
"""

import pytest
import pandas as pd
import numpy as np
from modules.detector import StoreTypeDetector


class TestStoreTypeDetector:
    """اختبار كاشف نوع المتجر"""
    
    def setup_method(self):
        """تهيئة قبل كل اختبار"""
        self.detector = StoreTypeDetector()
    
    def test_detect_fashion_store(self):
        """اختبار كشف متجر الأزياء"""
        # إنشاء بيانات تجريبية لمتجر أزياء
        data = {
            'product_name': ['قميص قطني', 'بنطلون جينز', 'فستان صيفي'],
            'size': ['M', 'L', 'S'],
            'color': ['أزرق', 'أسود', 'أحمر'],
            'price': [50, 70, 120]
        }
        
        df = pd.DataFrame(data)
        store_type, confidence = self.detector.detect(df)
        
        assert store_type == 'fashion'
        assert confidence['fashion'] > confidence.get('electronics', 0)
    
    def test_detect_electronics_store(self):
        """اختبار كشف متجر الإلكترونيات"""
        # إنشاء بيانات تجريبية لمتجر إلكترونيات
        data = {
            'product_name': ['هاتف ذكي', 'لابتوب', 'كاميرا'],
            'model': ['iPhone 13', 'MacBook Pro', 'Canon EOS'],
            'specifications': ['128GB', '16GB RAM', '24MP'],
            'warranty': ['1 سنة', '2 سنة', '3 سنوات']
        }
        
        df = pd.DataFrame(data)
        store_type, confidence = self.detector.detect(df)
        
        assert store_type == 'electronics'
        assert confidence['electronics'] > confidence.get('fashion', 0)
    
    def test_detect_general_store(self):
        """اختبار كشف المتجر العام"""
        # إنشاء بيانات عامة
        data = {
            'item': ['منتج 1', 'منتج 2', 'منتج 3'],
            'price': [100, 200, 300],
            'quantity': [1, 2, 3]
        }
        
        df = pd.DataFrame(data)
        store_type, confidence = self.detector.detect(df)
        
        # يجب أن يكون النوع العام هو الافتراضي
        assert store_type == 'general'
    
    def test_get_display_name_arabic(self):
        """اختبار الحصول على اسم العرض بالعربية"""
        display_name = self.detector.get_store_type_display_name('fashion', 'ar')
        assert display_name == '👗 متاجر الأزياء'
    
    def test_get_display_name_english(self):
        """اختبار الحصول على اسم العرض بالإنجليزية"""
        display_name = self.detector.get_store_type_display_name('fashion', 'en')
        assert display_name == '👗 Fashion Stores'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])