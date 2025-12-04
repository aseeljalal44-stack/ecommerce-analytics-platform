"""
دوال وأدوات مساعدة
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import streamlit as st


def format_currency(amount: float, currency: str = 'SAR') -> str:
    """تنسيق العملة"""
    if currency == 'SAR':
        return f"{amount:,.0f} ريال"
    elif currency == 'USD':
        return f"${amount:,.0f}"
    else:
        return f"{amount:,.0f} {currency}"


def format_percentage(value: float) -> str:
    """تنسيق النسبة المئوية"""
    return f"{value:.1f}%"


def format_date(date_obj, format_str: str = '%Y-%m-%d') -> str:
    """تنسيق التاريخ"""
    if pd.isna(date_obj):
        return "غير محدد"
    
    if isinstance(date_obj, str):
        try:
            date_obj = pd.to_datetime(date_obj)
        except:
            return date_obj
    
    return date_obj.strftime(format_str)


def calculate_date_range(dataframe: pd.DataFrame, date_column: str) -> Dict:
    """حساب نطاق التاريخ"""
    if date_column not in dataframe.columns:
        return {}
    
    dates = pd.to_datetime(dataframe[date_column], errors='coerce')
    dates = dates.dropna()
    
    if len(dates) == 0:
        return {}
    
    return {
        'start': dates.min(),
        'end': dates.max(),
        'days': (dates.max() - dates.min()).days,
        'count': len(dates)
    }


def detect_anomalies(dataframe: pd.DataFrame, column: str, 
                    threshold: float = 3.0) -> pd.DataFrame:
    """كشف القيم الشاذة باستخدام Z-score"""
    if column not in dataframe.columns:
        return pd.DataFrame()
    
    data = pd.to_numeric(dataframe[column], errors='coerce')
    data = data.dropna()
    
    if len(data) < 2:
        return pd.DataFrame()
    
    mean = data.mean()
    std = data.std()
    
    if std == 0:
        return pd.DataFrame()
    
    z_scores = np.abs((data - mean) / std)
    anomalies = dataframe.loc[data.index[z_scores > threshold]]
    
    return anomalies


def create_summary_stats(dataframe: pd.DataFrame, numeric_columns: List[str]) -> Dict:
    """إنشاء إحصائيات موجزة"""
    stats = {}
    
    for col in numeric_columns:
        if col in dataframe.columns:
            data = pd.to_numeric(dataframe[col], errors='coerce').dropna()
            
            if len(data) > 0:
                stats[col] = {
                    'count': len(data),
                    'mean': float(data.mean()),
                    'std': float(data.std()),
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'median': float(data.median())
                }
    
    return stats


def save_session_state(key: str, value: Any):
    """حفظ حالة الجلسة"""
    st.session_state[key] = value


def load_session_state(key: str, default: Any = None) -> Any:
    """تحميل حالة الجلسة"""
    return st.session_state.get(key, default)


def clear_session_state():
    """مسح حالة الجلسة"""
    keys_to_keep = ['language', 'theme']
    keys_to_delete = [key for key in st.session_state.keys() 
                     if key not in keys_to_keep]
    
    for key in keys_to_delete:
        del st.session_state[key]


def validate_file_upload(uploaded_file) -> Dict:
    """التحقق من صحة الملف المرفوع"""
    result = {
        'valid': False,
        'error': None,
        'dataframe': None
    }
    
    if uploaded_file is None:
        result['error'] = 'لم يتم رفع أي ملف'
        return result
    
    # التحقق من نوع الملف
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_name = uploaded_file.name.lower()
    
    if not any(file_name.endswith(ext) for ext in allowed_extensions):
        result['error'] = f'نوع الملف غير مدعوم. المسموح: {", ".join(allowed_extensions)}'
        return result
    
    try:
        # قراءة الملف
        if file_name.endswith('.csv'):
            dataframe = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            dataframe = pd.read_excel(uploaded_file)
        
        # التحقق من وجود البيانات
        if len(dataframe) == 0:
            result['error'] = 'الملف فارغ'
            return result
        
        if len(dataframe.columns) < 2:
            result['error'] = 'الملف لا يحتوي على أعمدة كافية'
            return result
        
        result['valid'] = True
        result['dataframe'] = dataframe
        
    except Exception as e:
        result['error'] = f'خطأ في قراءة الملف: {str(e)}'
    
    return result


def prepare_dataframe_display(dataframe: pd.DataFrame, 
                            max_rows: int = 100) -> pd.DataFrame:
    """تجهيز DataFrame للعرض"""
    display_df = dataframe.copy()
    
    # اقتطاع عدد الصفوف
    if len(display_df) > max_rows:
        display_df = display_df.head(max_rows)
    
    # تقليم الأعمدة النصية الطويلة
    for col in display_df.columns:
        if display_df[col].dtype == 'object':
            display_df[col] = display_df[col].astype(str).str[:50]
    
    return display_df