"""
نظام الترجمة متعدد اللغات
"""

from typing import Dict, Any


class TranslationSystem:
    """نظام الترجمة للواجهة والتقارير"""
    
    TRANSLATIONS = {
        'ar': {
            # واجهة المستخدم
            'app_title': '🛍️ نظام تحليل المتاجر الإلكترونية',
            'app_description': 'تحليل متكامل لمتاجر Shopify, WooCommerce, Amazon, Etsy والمزيد',
            
            # خطوات التحليل
            'step_upload': '📤 رفع البيانات',
            'step_mapping': '🎯 تعيين الأعمدة',
            'step_analysis': '📊 التحليل',
            'step_report': '📄 التقرير',
            
            # أنواع المتاجر
            'store_types': {
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
            
            # رسائل
            'upload_success': '✅ تم تحميل الملف بنجاح',
            'analysis_start': '🔍 جاري تحليل البيانات...',
            'analysis_complete': '✅ تم التحليل بنجاح',
            'report_generated': '📄 تم إنشاء التقرير',
            
            # أزرار
            'btn_upload': 'رفع ملف',
            'btn_analyze': 'بدء التحليل',
            'btn_download': 'تحميل التقرير',
            'btn_reset': 'بدء من جديد',
            
            # نصائح
            'tip_upload': 'يمكنك رفع ملفات Excel (.xlsx, .xls) أو CSV',
            'tip_mapping': 'سيساعدك النظام في التعرف على الأعمدة تلقائياً'
        },
        'en': {
            # User Interface
            'app_title': '🛍️ E-commerce Analytics Platform',
            'app_description': 'Comprehensive analysis for Shopify, WooCommerce, Amazon, Etsy and more',
            
            # Analysis Steps
            'step_upload': '📤 Upload Data',
            'step_mapping': '🎯 Map Columns',
            'step_analysis': '📊 Analysis',
            'step_report': '📄 Report',
            
            # Store Types
            'store_types': {
                'fashion': '👗 Fashion Stores',
                'electronics': '📱 Electronics Stores',
                'beauty': '💄 Beauty Stores',
                'home_garden': '🏠 Home & Garden Stores',
                'digital': '💻 Digital Products',
                'subscription': '🔄 Subscription Stores',
                'handmade': '🎨 Handmade Products',
                'food': '🍎 Food Stores',
                'general': '🛒 General Store'
            },
            
            # Messages
            'upload_success': '✅ File uploaded successfully',
            'analysis_start': '🔍 Analyzing data...',
            'analysis_complete': '✅ Analysis completed',
            'report_generated': '📄 Report generated',
            
            # Buttons
            'btn_upload': 'Upload File',
            'btn_analyze': 'Start Analysis',
            'btn_download': 'Download Report',
            'btn_reset': 'Start Over',
            
            # Tips
            'tip_upload': 'You can upload Excel (.xlsx, .xls) or CSV files',
            'tip_mapping': 'The system will help you automatically identify columns'
        }
    }
    
    @classmethod
    def t(cls, key: str, language: str = 'ar', **kwargs) -> str:
        """
        ترجمة النص
        
        Args:
            key: مفتاح الترجمة
            language: اللغة ('ar' أو 'en')
            **kwargs: معلمات للنص
            
        Returns:
            str: النص المترجم
        """
        translation_dict = cls.TRANSLATIONS.get(language, cls.TRANSLATIONS['ar'])
        
        # البحث في المستويات المتعددة
        keys = key.split('.')
        value = translation_dict
        
        try:
            for k in keys:
                value = value[k]
            
            if isinstance(value, str) and kwargs:
                return value.format(**kwargs)
            
            return value
        except (KeyError, TypeError):
            # إذا لم توجد الترجمة، إرجاع المفتاح
            return key
    
    @classmethod
    def get_store_type_name(cls, store_type: str, language: str = 'ar') -> str:
        """الحصول على اسم نوع المتجر"""
        store_types = cls.t('store_types', language)
        return store_types.get(store_type, store_type)
    
    @classmethod
    def get_available_languages(cls) -> Dict[str, str]:
        """الحصول على اللغات المتاحة"""
        return {
            'ar': 'العربية',
            'en': 'English'
        }
    
    @classmethod
    def get_direction(cls, language: str) -> str:
        """الحصول على اتجاه النص للغة"""
        return 'rtl' if language == 'ar' else 'ltr'