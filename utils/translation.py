# utils/translation.py
class Translator:
    # بسيط: يدعم إنجليزي/عربي لعبارات قليلة
    MESSAGES = {
        'Language': {'ar':'اللغة','en':'Language'},
        'Controls': {'ar':'التحكم','en':'Controls'},
        'Upload CSV / Excel': {'ar':'ارفع CSV أو Excel','en':'Upload CSV / Excel'},
        'File loaded successfully': {'ar':'تم تحميل الملف','en':'File loaded successfully'},
        'Preview': {'ar':'معاينة','en':'Preview'},
        'Detected store type:': {'ar':'نوع المتجر المكتشف:','en':'Detected store type:'},
        'Auto column mapping': {'ar':'تعيين الأعمدة تلقائياً','en':'Auto column mapping'},
        'Analysis Results': {'ar':'نتائج التحليل','en':'Analysis Results'},
        'Controls': {'ar':'التحكم','en':'Controls'},
        'Upload a dataset (CSV/Excel) to start analysis.': {'ar':'ارفع ملف بيانات للبدء في التحليل.','en':'Upload a dataset (CSV/Excel) to start analysis.'},
        'Upload a CSV/Excel file with orders. Columns like order_id/order_date/total_amount help automatic mapping.': {
            'ar':'ارفع ملف CSV أو Excel يحوي بيانات الطلبات. أعمدة مثل order_id/order_date/total_amount تسهل التعرف التلقائي.',
            'en':'Upload a CSV/Excel file with orders. Columns like order_id/order_date/total_amount help automatic mapping.'
        }
    }

    def translate(self, en_text: str, ar_text: str, lang='ar'):
        # usage: translate(en, ar) -> will return based on st.session_state.language if available
        import streamlit as st
        lang = st.session_state.get('language','ar')
        key = en_text if en_text in self.MESSAGES else ar_text
        if key in self.MESSAGES:
            return self.MESSAGES[key].get(lang, key)
        return ar_text if lang=='ar' else en_text

class LanguageManager:
    pass