"""
وحدة التحقق من صحة البيانات والملفات للمتاجر الإلكترونية
دوال التحقق من صحة البيانات المدخلة، الملفات المرفوعة، والتكوينات
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
import os
from io import BytesIO
import magic
import chardet

class EcommerceValidators:
    """فئة تحتوي على دوال التحقق من صحة بيانات المتاجر الإلكترونية"""
    
    @staticmethod
    def validate_file_upload(file, max_size_mb=100, allowed_extensions=None):
        """
        التحقق من صحة الملف المرفوع
        
        Args:
            file: ملف Streamlit المرفوع
            max_size_mb: الحد الأقصى لحجم الملف بالميجابايت
            allowed_extensions: القائمة المسموحة من الامتدادات
        
        Returns:
            dict: نتائج التحقق {'valid': bool, 'message': str, 'file_type': str}
        """
        if allowed_extensions is None:
            allowed_extensions = ['.csv', '.xlsx', '.xls', '.json']
        
        if file is None:
            return {'valid': False, 'message': 'لم يتم رفع ملف', 'file_type': None}
        
        # التحقق من حجم الملف
        file_size_mb = len(file.getvalue()) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            return {
                'valid': False, 
                'message': f'حجم الملف كبير جداً ({file_size_mb:.1f} MB). الحد الأقصى {max_size_mb} MB',
                'file_type': None
            }
        
        # التحقق من امتداد الملف
        file_name = file.name.lower()
        file_extension = os.path.sitext(file_name)
        
        if file_extension not in allowed_extensions:
            return {
                'valid': False,
                'message': f'نوع الملف غير مدعوم. المسموح: {", ".join(allowed_extensions)}',
                'file_type': None
            }
        
        # تحديد نوع الملف بدقة
        file_type = None
        if file_extension in ['.csv', '.txt']:
            file_type = 'csv'
        elif file_extension in ['.xlsx', '.xls']:
            file_type = 'excel'
        elif file_extension == '.json':
            file_type = 'json'
        
        return {
            'valid': True,
            'message': 'الملف صالح',
            'file_type': file_type,
            'size_mb': file_size_mb,
            'extension': file_extension
        }
    
    @staticmethod
    def validate_csv_content(file_content, sample_size=1000):
        """
        التحقق من محتوى ملف CSV
        
        Args:
            file_content: محتوى الملف
            sample_size: حجم العينة للتحقق
        
        Returns:
            dict: نتائج التحقق
        """
        try:
            # كشف الترميز
            encoding_result = chardet.detect(file_content[:10000])
            encoding = encoding_result['encoding'] or 'utf-8'
            
            # قراءة أول سطرين لتحديد المحدد
            sample_text = file_content[:1000].decode(encoding, errors='ignore')
            lines = sample_text.split('\n')
            
            # تحديد المحدد
            delimiter = ','
            if len(lines) > 1:
                if ';' in lines[0] and lines[0].count(';') > lines[0].count(','):
                    delimiter = ';'
                elif '\t' in lines[0]:
                    delimiter = '\t'
            
            # قراءة البيانات
            df = pd.read_csv(
                BytesIO(file_content),
                encoding=encoding,
                delimiter=delimiter,
                nrows=100,  # قراءة أول 100 صف فقط للتحقق
                on_bad_lines='skip'
            )
            
            # التحقق من البيانات الأساسية
            if df.empty:
                return {'valid': False, 'message': 'الملف لا يحتوي على بيانات', 'encoding': encoding}
            
            if len(df.columns) < 2:
                return {'valid': False, 'message': 'عدد الأعمدة قليل جداً', 'encoding': encoding}
            
            # التحقق من وجود أعمدة أساسية محتملة
            required_patterns = [
                r'order.*id', r'product.*id', r'customer.*id',
                r'price', r'quantity', r'date'
            ]
            
            found_patterns = 0
            column_names_lower = [str(col).lower() for col in df.columns]
            
            for pattern in required_patterns:
                for col in column_names_lower:
                    if re.search(pattern, col):
                        found_patterns += 1
                        break
            
            # إذا لم يتم العثور على أنماط كافية
            if found_patterns < 2:
                return {
                    'valid': True, 
                    'warning': True,
                    'message': 'لم يتم التعرف على حقول أساسية كافية',
                    'encoding': encoding,
                    'delimiter': delimiter,
                    'columns': list(df.columns),
                    'rows_count': len(df)
                }
            
            return {
                'valid': True,
                'message': 'محتوى CSV صالح',
                'encoding': encoding,
                'delimiter': delimiter,
                'columns': list(df.columns),
                'rows_count': len(df)
            }
            
        except Exception as e:
            return {'valid': False, 'message': f'خطأ في قراءة الملف: {str(e)}', 'encoding': None}
    
    @staticmethod
    def validate_excel_content(file_content, engine='openpyxl'):
        """
        التحقق من محتوى ملف Excel
        
        Args:
            file_content: محتوى الملف
            engine: محرك قراءة Excel
        
        Returns:
            dict: نتائج التحقق
        """
        try:
            # قراءة أسماء الأوراق
            excel_file = BytesIO(file_content)
            xls = pd.ExcelFile(excel_file, engine=engine)
            sheets = xls.sheet_names
            
            if not sheets:
                return {'valid': False, 'message': 'الملف لا يحتوي على أوراق'}
            
            # قراءة أول ورقة
            df = pd.read_excel(excel_file, sheet_name=sheets[0], nrows=100)
            
            if df.empty:
                return {'valid': False, 'message': 'الورقة الأولى لا تحتوي على بيانات'}
            
            if len(df.columns) < 2:
                return {'valid': False, 'message': 'عدد الأعمدة قليل جداً'}
            
            # التحقق من وجود أعمدة أساسية محتملة
            column_names_lower = [str(col).lower() for col in df.columns]
            
            # الأنماط الأساسية
            essential_patterns = [r'order', r'product', r'customer', r'price', r'date']
            found_essential = 0
            
            for pattern in essential_patterns:
                for col in column_names_lower:
                    if re.search(pattern, col):
                        found_essential += 1
                        break
            
            return {
                'valid': True,
                'message': 'محتوى Excel صالح',
                'sheets': sheets,
                'columns': list(df.columns),
                'rows_count': len(df),
                'essential_fields_found': found_essential
            }
            
        except Exception as e:
            return {'valid': False, 'message': f'خطأ في قراءة ملف Excel: {str(e)}'}
    
    @staticmethod
    def validate_dataframe_structure(df):
        """
        التحقق من بنية DataFrame
        
        Args:
            df: DataFrame للتحقق
        
        Returns:
            dict: نتائج التحقق
        """
        validation_results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'statistics': {}
        }
        
        if df is None or df.empty:
            validation_results['valid'] = False
            validation_results['issues'].append('DataFrame فارغ أو غير موجود')
            return validation_results
        
        # جمع الإحصائيات الأساسية
        validation_results['statistics'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': df.select_dtypes(include=[np.number]).shape[1],
            'text_columns': df.select_dtypes(include=['object']).shape[1],
            'date_columns': df.select_dtypes(include=['datetime64']).shape[1]
        }
        
        # التحقق 1: عدد الصفوف
        if len(df) < 10:
            validation_results['warnings'].append('عدد الصفوف قليل جداً (أقل من 10)')
        
        # التحقق 2: عدد الأعمدة
        if len(df.columns) < 3:
            validation_results['warnings'].append('عدد الأعمدة قليل جداً (أقل من 3)')
        
        # التحقق 3: أسماء الأعمدة
        invalid_columns = []
        for col in df.columns:
            col_str = str(col)
            # التحقق من الأسماء الفارغة أو NaN
            if pd.isna(col) or str(col).strip() == '':
                invalid_columns.append(str(col))
            # التحقق من الأسماء الطويلة جداً
            elif len(col_str) > 50:
                validation_results['warnings'].append(f'اسم العمود طويل جداً: {col_str[:30]}...')
        
        if invalid_columns:
            validation_results['issues'].append(f'أعمدة بأسماء غير صالحة: {invalid_columns}')
        
        # التحقق 4: القيم المفقودة
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        high_missing = missing_percentage[missing_percentage > 30].index.tolist()
        
        if high_missing:
            validation_results['warnings'].append(f'أعمدة بها قيم مفقودة >30%: {len(high_missing)} عمود')
        
        # التحقق 5: التكرارات
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            duplicate_percentage = (duplicates / len(df)) * 100
            validation_results['warnings'].append(f'سجلات مكررة: {duplicates} ({duplicate_percentage:.1f}%)')
        
        # التحقق 6: أنواع البيانات
        for col in df.columns:
            col_dtype = str(df[col].dtype)
            
            # إذا كان العمود رقماً، تحقق من القيم السلبية غير المنطقية
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                negative_count = (numeric_col < 0).sum()
                
                # السماح بالأرقام السالبة في بعض الأعمدة فقط
                col_lower = str(col).lower()
                if negative_count > 0:
                    allowed_negative_cols = ['discount', 'refund', 'return', 'profit', 'loss']
                    if not any(keyword in col_lower for keyword in allowed_negative_cols):
                        validation_results['warnings'].append(
                            f'عمود {col}: يحتوي على {negative_count} قيمة سلبية'
                        )
        
        return validation_results
    
    @staticmethod
    def validate_ecommerce_columns(df, required_columns=None, store_type='general'):
        """
        التحقق من أعمدة المتاجر الإلكترونية الأساسية
        
        Args:
            df: DataFrame للتحقق
            required_columns: قائمة الأعمدة المطلوبة
            store_type: نوع المتجر
        
        Returns:
            dict: نتائج التحقق
        """
        if required_columns is None:
            # الأعمدة الأساسية لكل متجر إلكتروني
            required_columns = {
                'general': ['order_id', 'product_id', 'customer_id', 'quantity', 'price', 'date'],
                'fashion': ['size', 'color', 'variant'],
                'electronics': ['model', 'brand', 'warranty'],
                'beauty': ['weight', 'volume', 'ingredients']
            }
        
        # الحصول على الأعمدة المطلوبة حسب نوع المتجر
        columns_to_check = required_columns.get('general', [])
        if store_type in required_columns:
            columns_to_check.extend(required_columns[store_type])
        
        validation_results = {
            'valid': True,
            'missing_essential': [],
            'found_essential': [],
            'suggested_mappings': {},
            'store_type_detected': store_type
        }
        
        # الأنماط للتعرف على الأعمدة
        column_patterns = {
            'order_id': [r'order.*id', r'order.*no', r'transaction.*id'],
            'product_id': [r'product.*id', r'item.*id', r'sku'],
            'customer_id': [r'customer.*id', r'user.*id', r'client.*id'],
            'quantity': [r'quantity', r'qty', r'amount'],
            'price': [r'price', r'cost', r'amount'],
            'date': [r'date', r'time', r'created'],
            'size': [r'size', r'dimension', r'measurement'],
            'color': [r'color', r'colour', r'hue'],
            'model': [r'model', r'type', r'version'],
            'brand': [r'brand', r'make', r'manufacturer']
        }
        
        # التعرف التلقائي على الأعمدة
        column_names_lower = [str(col).lower() for col in df.columns]
        
        for column_type, patterns in column_patterns.items():
            found = False
            for pattern in patterns:
                for idx, col_name in enumerate(column_names_lower):
                    if re.search(pattern, col_name):
                        validation_results['suggested_mappings'][column_type] = df.columns[idx]
                        if column_type in columns_to_check:
                            validation_results['found_essential'].append(column_type)
                        found = True
                        break
                if found:
                    break
        
        # تحديد الأعمدة المفقودة
        for col_type in columns_to_check:
            if col_type not in validation_results['found_essential']:
                validation_results['missing_essential'].append(col_type)
        
        # تحديد ما إذا كانت البيانات صالحة
        if len(validation_results['found_essential']) < 3:
            validation_results['valid'] = False
        
        return validation_results
    
    @staticmethod
    def validate_numeric_column(series, column_name, positive_only=True):
        """
        التحقق من عمود رقمي
        
        Args:
            series: سلسلة البيانات
            column_name: اسم العمود
            positive_only: إذا كان يجب أن تكون القيم موجبة فقط
        
        Returns:
            dict: نتائج التحقق
        """
        results = {
            'valid': True,
            'column_name': column_name,
            'issues': [],
            'statistics': {}
        }
        
        # تحويل إلى رقم
        numeric_series = pd.to_numeric(series, errors='coerce')
        
        # حساب الإحصائيات
        results['statistics'] = {
            'total_values': len(numeric_series),
            'valid_numeric': numeric_series.notna().sum(),
            'invalid_numeric': numeric_series.isna().sum(),
            'min': numeric_series.min() if numeric_series.notna().any() else None,
            'max': numeric_series.max() if numeric_series.notna().any() else None,
            'mean': numeric_series.mean() if numeric_series.notna().any() else None,
            'median': numeric_series.median() if numeric_series.notna().any() else None,
            'std': numeric_series.std() if numeric_series.notna().any() else None
        }
        
        # التحقق من القيم المفقودة
        missing_percentage = (numeric_series.isna().sum() / len(numeric_series)) * 100
        if missing_percentage > 20:
            results['issues'].append(f'نسبة عالية من القيم المفقودة: {missing_percentage:.1f}%')
        
        # التحقق من القيم السلبية (إذا مطلوب)
        if positive_only and numeric_series.notna().any():
            negative_count = (numeric_series < 0).sum()
            if negative_count > 0:
                results['issues'].append(f'يوجد {negative_count} قيمة سلبية')
        
        # التحقق من القيم المتطرفة
        if numeric_series.notna().any():
            q1 = numeric_series.quantile(0.25)
            q3 = numeric_series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = ((numeric_series < lower_bound) | (numeric_series > upper_bound)).sum()
            if outliers > 0:
                outlier_percentage = (outliers / len(numeric_series)) * 100
                results['issues'].append(f'يوجد {outliers} قيمة متطرفة ({outlier_percentage:.1f}%)')
        
        # التحقق من القيم الصفرية
        zero_count = (numeric_series == 0).sum()
        if zero_count > 0:
            results['issues'].append(f'يوجد {zero_count} قيمة صفرية')
        
        # تحديد إذا كان هناك مشاكل
        if results['issues']:
            results['valid'] = False
        
        return results
    
    @staticmethod
    def validate_date_column(series, column_name, future_dates_allowed=False):
        """
        التحقق من عمود التاريخ
        
        Args:
            series: سلسلة البيانات
            column_name: اسم العمود
            future_dates_allowed: السماح بالتواريخ المستقبلية
        
        Returns:
            dict: نتائج التحقق
        """
        results = {
            'valid': True,
            'column_name': column_name,
            'issues': [],
            'statistics': {}
        }
        
        # تحويل إلى تاريخ
        date_series = pd.to_datetime(series, errors='coerce')
        
        # حساب الإحصائيات
        valid_dates = date_series.notna()
        results['statistics'] = {
            'total_values': len(date_series),
            'valid_dates': valid_dates.sum(),
            'invalid_dates': date_series.isna().sum(),
            'date_range_start': date_series.min() if valid_dates.any() else None,
            'date_range_end': date_series.max() if valid_dates.any() else None,
            'date_format_success_rate': (valid_dates.sum() / len(date_series)) * 100
        }
        
        # التحقق 1: نسبة صحة التواريخ
        success_rate = results['statistics']['date_format_success_rate']
        if success_rate < 70:
            results['issues'].append(f'نسبة تحويل التواريخ منخفضة: {success_rate:.1f}%')
            results['valid'] = False
        
        # التحقق 2: تواريخ مستقبلية
        if not future_dates_allowed and valid_dates.any():
            now = pd.Timestamp.now()
            future_dates = date_series[date_series > now]
            if len(future_dates) > 0:
                results['issues'].append(f'يوجد {len(future_dates)} تاريخ مستقبلي')
        
        # التحقق 3: تواريخ قديمة جداً
        if valid_dates.any():
            min_date = date_series.min()
            if min_date < pd.Timestamp('2000-01-01'):
                results['issues'].append(f'يوجد تواريخ قديمة جداً: {min_date.date()}')
        
        # التحقق 4: نطاق التواريخ
        if valid_dates.any():
            date_range = date_series.max() - date_series.min()
            if date_range.days < 1:
                results['issues'].append('نطاق التواريخ أقل من يوم واحد')
            elif date_range.days > 365 * 10:
                results['issues'].append('نطاق التواريخ كبير جداً (أكثر من 10 سنوات)')
        
        return results
    
    @staticmethod
    def validate_text_column(series, column_name, max_unique_ratio=0.5, min_length=1):
        """
        التحقق من عمود النص
        
        Args:
            series: سلسلة البيانات
            column_name: اسم العمود
            max_unique_ratio: النسبة القصوى للقيم الفريدة
            min_length: الحد الأدنى لطول النص
        
        Returns:
            dict: نتائج التحقق
        """
        results = {
            'valid': True,
            'column_name': column_name,
            'issues': [],
            'statistics': {}
        }
        
        # تحويل إلى نص
        text_series = series.astype(str)
        
        # حساب الإحصائيات
        results['statistics'] = {
            'total_values': len(text_series),
            'unique_values': text_series.nunique(),
            'missing_values': text_series.isna().sum(),
            'empty_strings': (text_series == '').sum(),
            'avg_length': text_series.str.len().mean() if len(text_series) > 0 else 0,
            'max_length': text_series.str.len().max() if len(text_series) > 0 else 0
        }
        
        # التحقق 1: القيم الفريدة
        unique_ratio = results['statistics']['unique_values'] / results['statistics']['total_values']
        if unique_ratio > max_unique_ratio:
            results['issues'].append(f'نسبة القيم الفريدة عالية: {unique_ratio:.1%}')
        
        # التحقق 2: سلاسل فارغة
        empty_count = results['statistics']['empty_strings']
        if empty_count > 0:
            empty_percentage = (empty_count / len(text_series)) * 100
            results['issues'].append(f'يوجد {empty_count} سلسلة فارغة ({empty_percentage:.1f}%)')
        
        # التحقق 3: طول النص
        if results['statistics']['avg_length'] < min_length:
            results['issues'].append(f'متوسط طول النص قصير: {results["statistics"]["avg_length"]:.1f}')
        
        # التحقق 4: نمط البريد الإلكتروني (إذا كان العمود بريداً)
        col_lower = column_name.lower()
        if 'email' in col_lower or 'mail' in col_lower:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            valid_emails = text_series.str.match(email_pattern).sum()
            if valid_emails / len(text_series) < 0.7:
                results['issues'].append('نسبة صحة عناوين البريد الإلكتروني منخفضة')
        
        return results
    
    @staticmethod
    def validate_store_config(config_dict):
        """
        التحقق من تكوين المتجر
        
        Args:
            config_dict: قاموس التكوين
        
        Returns:
            dict: نتائج التحقق
        """
        results = {
            'valid': True,
            'issues': [],
            'missing_fields': []
        }
        
        # الحقول المطلوبة
        required_fields = ['store_name', 'store_type', 'currency', 'timezone']
        
        # التحقق من الحقول المطلوبة
        for field in required_fields:
            if field not in config_dict or not config_dict[field]:
                results['missing_fields'].append(field)
                results['valid'] = False
        
        # التحقق من نوع المتجر
        valid_store_types = [
            'fashion', 'electronics', 'home_garden', 'beauty',
            'digital', 'subscription', 'handmade', 'food', 'general'
        ]
        
        store_type = config_dict.get('store_type', '')
        if store_type and store_type not in valid_store_types:
            results['issues'].append(f'نوع المتجر غير صالح: {store_type}')
            results['valid'] = False
        
        # التحقق من العملة
        valid_currencies = ['SAR', 'USD', 'EUR', 'GBP', 'AED', 'QAR', 'KWD', 'BHD', 'OMR']
        currency = config_dict.get('currency', '')
        if currency and currency not in valid_currencies:
            results['issues'].append(f'العملة غير مدعومة: {currency}')
        
        # التحقق من المنطقة الزمنية
        timezone = config_dict.get('timezone', '')
        if timezone and not re.match(r'^[A-Za-z/_-]+$', timezone):
            results['issues'].append(f'تنسيق المنطقة الزمنية غير صالح: {timezone}')
        
        # التحقق من البريد الإلكتروني (إذا كان موجوداً)
        email = config_dict.get('contact_email', '')
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                results['issues'].append('البريد الإلكتروني غير صالح')
        
        return results
    
    @staticmethod
    def validate_mapping_config(mapping_dict, df_columns):
        """
        التحقق من تكوين تعيين الأعمدة
        
        Args:
            mapping_dict: قاموس التعيين
            df_columns: قائمة أعمدة DataFrame
        
        Returns:
            dict: نتائج التحقق
        """
        results = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'mapped_columns': 0,
            'total_mappings': len(mapping_dict)
        }
        
        if not mapping_dict:
            results['valid'] = False
            results['issues'].append('لا يوجد تعيين للأعمدة')
            return results
        
        for field, column in mapping_dict.items():
            if column == '❌ غير متوفر':
                continue
            
            # التحقق مما إذا كان العمود موجوداً في البيانات
            if column not in df_columns:
                results['issues'].append(f'العمود {column} غير موجود في البيانات')
                results['valid'] = False
            else:
                results['mapped_columns'] += 1
        
        # التحقق من التعيينات الأساسية
        essential_fields = ['order_id', 'product_id', 'quantity', 'price', 'date']
        missing_essential = []
        
        for field in essential_fields:
            if field not in mapping_dict or mapping_dict[field] == '❌ غير متوفر':
                missing_essential.append(field)
        
        if missing_essential:
            results['warnings'].append(f'حقول أساسية غير معينة: {missing_essential}')
            if len(missing_essential) > 2:
                results['valid'] = False
        
        return results
    
    @staticmethod
    def detect_data_quality_issues(df, sample_size=1000):
        """
        اكتشاف مشاكل جودة البيانات
        
        Args:
            df: DataFrame للفحص
            sample_size: حجم العينة للتحليل
        
        Returns:
            dict: مشاكل جودة البيانات المكتشفة
        """
        issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'summary': {
                'total_issues': 0,
                'critical_count': 0,
                'high_count': 0,
                'medium_count': 0,
                'low_count': 0
            }
        }
        
        if df is None or df.empty:
            issues['critical'].append('DataFrame فارغ أو غير موجود')
            return issues
        
        # أخذ عينة إذا كانت البيانات كبيرة
        df_sample = df.sample(min(sample_size, len(df))) if len(df) > sample_size else df
        
        # 1. القيم المفقودة
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        for col, percentage in missing_percentage.items():
            if percentage > 50:
                issues['critical'].append(f'العمود {col}: {percentage:.1f}% قيم مفقودة')
            elif percentage > 30:
                issues['high'].append(f'العمود {col}: {percentage:.1f}% قيم مفقودة')
            elif percentage > 10:
                issues['medium'].append(f'العمود {col}: {percentage:.1f}% قيم مفقودة')
        
        # 2. التكرارات
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            duplicate_percentage = (duplicates / len(df)) * 100
            if duplicate_percentage > 10:
                issues['critical'].append(f'{duplicate_percentage:.1f}% سجلات مكررة')
            elif duplicate_percentage > 5:
                issues['high'].append(f'{duplicate_percentage:.1f}% سجلات مكررة')
            elif duplicate_percentage > 1:
                issues['medium'].append(f'{duplicate_percentage:.1f}% سجلات مكررة')
        
        # 3. قيم متطرفة
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            try:
                series = pd.to_numeric(df[col], errors='coerce')
                if series.notna().any():
                    q1 = series.quantile(0.25)
                    q3 = series.quantile(0.75)
                    iqr = q3 - q1
                    
                    if iqr > 0:
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        
                        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
                        if outliers > 0:
                            outlier_percentage = (outliers / len(series)) * 100
                            if outlier_percentage > 5:
                                issues['high'].append(f'العمود {col}: {outlier_percentage:.1f}% قيم متطرفة')
            except:
                continue
        
        # 4. تناسق البيانات
        for col in df.columns:
            # الكشف عن قيم غير متوقعة
            if df[col].dtype == 'object':
                unique_values = df[col].dropna().unique()
                if len(unique_values) == 1:
                    issues['low'].append(f'العمود {col}: يحتوي على قيمة واحدة فقط')
        
        # 5. تواريخ غير منطقية
        date_cols = df.select_dtypes(include=['datetime64']).columns
        for col in date_cols:
            future_dates = df[col][df[col] > pd.Timestamp.now()]
            if len(future_dates) > 0:
                issues['medium'].append(f'العمود {col}: يحتوي على تواريخ مستقبلية')
        
        # تحديث الملخص
        issues['summary'] = {
            'total_issues': len(issues['critical']) + len(issues['high']) + 
                           len(issues['medium']) + len(issues['low']),
            'critical_count': len(issues['critical']),
            'high_count': len(issues['high']),
            'medium_count': len(issues['medium']),
            'low_count': len(issues['low'])
        }
        
        return issues
    
    @staticmethod
    def get_data_quality_score(df):
        """
        حساب درجة جودة البيانات
        
        Args:
            df: DataFrame للتحليل
        
        Returns:
            dict: درجة جودة البيانات وتفاصيلها
        """
        if df is None or df.empty:
            return {
                'score': 0,
                'grade': 'F',
                'details': 'لا توجد بيانات',
                'recommendations': ['رفع ملف بيانات صالح']
            }
        
        max_score = 100
        score = max_score
        
        # 1. القيم المفقودة (30%)
        missing_penalty = 0
        missing_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percentage > 50:
            missing_penalty = 30
        elif missing_percentage > 30:
            missing_penalty = 20
        elif missing_percentage > 10:
            missing_penalty = 10
        elif missing_percentage > 5:
            missing_penalty = 5
        
        score -= missing_penalty
        
        # 2. التكرارات (20%)
        duplicate_penalty = 0
        duplicates = df.duplicated().sum()
        duplicate_percentage = (duplicates / len(df)) * 100
        if duplicate_percentage > 10:
            duplicate_penalty = 20
        elif duplicate_percentage > 5:
            duplicate_penalty = 10
        elif duplicate_percentage > 1:
            duplicate_penalty = 5
        
        score -= duplicate_penalty
        
        # 3. التناسق (20%)
        consistency_penalty = 0
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:5]:  # التحقق من أول 5 أعمدة رقمية فقط
            try:
                series = pd.to_numeric(df[col], errors='coerce')
                if series.notna().any():
                    # الكشف عن قيم غير منطقية
                    negative_ratio = (series < 0).sum() / len(series) if len(series) > 0 else 0
                    if negative_ratio > 0.1:
                        consistency_penalty += 2
            except:
                consistency_penalty += 2
        
        score -= min(consistency_penalty, 20)
        
        # 4. الكمالية (30%)
        completeness_penalty = 0
        essential_patterns = [r'order', r'product', r'customer', r'price', r'date']
        column_names_lower = [str(col).lower() for col in df.columns]
        
        found_patterns = 0
        for pattern in essential_patterns:
            for col in column_names_lower:
                if re.search(pattern, col):
                    found_patterns += 1
                    break
        
        completeness_penalty = (5 - found_patterns) * 6 if found_patterns < 5 else 0
        score -= completeness_penalty
        
        # تحديد الدرجة
        if score >= 90:
            grade = 'A'
            color = 'green'
        elif score >= 80:
            grade = 'B'
            color = 'blue'
        elif score >= 70:
            grade = 'C'
            color = 'yellow'
        elif score >= 60:
            grade = 'D'
            color = 'orange'
        else:
            grade = 'F'
            color = 'red'
        
        # التوصيات
        recommendations = []
        if missing_percentage > 10:
            recommendations.append('معالجة القيم المفقودة')
        if duplicate_percentage > 5:
            recommendations.append('إزالة السجلات المكررة')
        if found_patterns < 3:
            recommendations.append('إضافة حقول أساسية للمتجر الإلكتروني')
        
        return {
            'score': round(score, 1),
            'grade': grade,
            'color': color,
            'details': {
                'missing_percentage': round(missing_percentage, 1),
                'duplicate_percentage': round(duplicate_percentage, 1),
                'essential_fields_found': found_patterns,
                'penalties': {
                    'missing': missing_penalty,
                    'duplicate': duplicate_penalty,
                    'consistency': consistency_penalty,
                    'completeness': completeness_penalty
                }
            },
            'recommendations': recommendations if recommendations else ['جودة البيانات جيدة']
        }

# ==================== دوال المساعدة ====================

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone, country_code='+966'):
    """التحقق من صحة رقم الهاتف"""
    # إزالة المسافات والأحرف الخاصة
    phone = re.sub(r'[^\d+]', '', phone)
    
    # التحقق من الأرقام السعودية (مثال)
    if country_code == '+966':
        saudi_pattern = r'^(009665|9665|\+9665|05|5)[0-9]{8}$'
        return bool(re.match(saudi_pattern, phone))
    
    # نمط عام للأرقام الدولية
    international_pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(international_pattern, phone))

def validate_url(url):
    """التحقق من صحة الرابط"""
    pattern = r'^(https?://)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(/.*)?$'
    return bool(re.match(pattern, url))

def validate_currency(currency_code):
    """التحقق من صحة رمز العملة"""
    valid_currencies = ['SAR', 'USD', 'EUR', 'GBP', 'AED', 'QAR', 'KWD', 'BHD', 'OMR']
    return currency_code in valid_currencies

def validate_date_format(date_string, format='%Y-%m-%d'):
    """التحقق من صحة تنسيق التاريخ"""
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False

# ==================== فئة لرسائل التحقق ====================

class ValidationMessages:
    """رسائل التحقق المترجمة"""
    
    MESSAGES = {
        'ar': {
            'file_valid': 'الملف صالح',
            'file_invalid': 'الملف غير صالح',
            'file_too_large': 'حجم الملف كبير جداً',
            'file_type_unsupported': 'نوع الملف غير مدعوم',
            'data_empty': 'البيانات فارغة',
            'data_valid': 'البيانات صالحة',
            'missing_columns': 'أعمدة مفقودة',
            'duplicate_data': 'بيانات مكررة',
            'invalid_dates': 'تواريخ غير صالحة',
            'future_dates': 'تواريخ مستقبلية',
            'negative_values': 'قيم سلبية غير مسموحة',
            'email_invalid': 'البريد الإلكتروني غير صالح',
            'phone_invalid': 'رقم الهاتف غير صالح',
            'url_invalid': 'الرابط غير صالح',
            'currency_invalid': 'العملة غير صالحة',
            'config_incomplete': 'التكوين غير مكتمل'
        },
        'en': {
            'file_valid': 'File is valid',
            'file_invalid': 'File is invalid',
            'file_too_large': 'File is too large',
            'file_type_unsupported': 'File type is not supported',
            'data_empty': 'Data is empty',
            'data_valid': 'Data is valid',
            'missing_columns': 'Missing columns',
            'duplicate_data': 'Duplicate data',
            'invalid_dates': 'Invalid dates',
            'future_dates': 'Future dates',
            'negative_values': 'Negative values not allowed',
            'email_invalid': 'Invalid email address',
            'phone_invalid': 'Invalid phone number',
            'url_invalid': 'Invalid URL',
            'currency_invalid': 'Invalid currency',
            'config_incomplete': 'Configuration is incomplete'
        }
    }
    
    @staticmethod
    def get_message(key, lang='ar'):
        """الحصول على رسالة التحقق"""
        return ValidationMessages.MESSAGES.get(lang, {}).get(key, key)

# ==================== وظائف الاختبار ====================

if __name__ == "__main__":
    # اختبار الدوال الأساسية
    print("اختبار وحدة التحقق من الصحة...")
    
    # اختبار تحقق البريد الإلكتروني
    test_emails = ["test@example.com", "invalid-email", "user@domain"]
    for email in test_emails:
        print(f"البريد {email}: {'صالح' if validate_email(email) else 'غير صالح'}")
    
    # اختبار تحقق رقم الهاتف
    test_phones = ["+966501234567", "0501234567", "invalid"]
    for phone in test_phones:
        print(f"الهاتف {phone}: {'صالح' if validate_phone(phone) else 'غير صالح'}")
    
    print("تم اختبار وحدة التحقق من الصحة بنجاح!")