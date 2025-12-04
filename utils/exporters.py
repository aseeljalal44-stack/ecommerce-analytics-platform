"""
وحدة تصدير البيانات والتقارير للمتاجر الإلكترونية
تصدير البيانات، التقارير، الرسوم البيانية، والتحليلات بتنسيقات مختلفة
"""

import pandas as pd
import numpy as np
import json
import os
import io
import base64
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import plotly.graph_objects as go
import plotly.express as px

try:
    import pdfkit
    HAS_PDFKIT = True
except ImportError:
    HAS_PDFKIT = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

class EcommerceExporters:
    """فئة تصدير البيانات والتقارير للمتاجر الإلكترونية"""
    
    def __init__(self, output_dir: str = "exports"):
        """
        تهيئة مصدر التصدير
        
        Args:
            output_dir: مجلد التصدير الافتراضي
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    # ==================== تصدير البيانات ====================
    
    def export_dataframe(
        self, 
        df: pd.DataFrame, 
        filename: str, 
        format: str = 'excel',
        include_index: bool = False,
        encoding: str = 'utf-8'
    ) -> Dict[str, Any]:
        """
        تصدير DataFrame بتنسيقات مختلفة
        
        Args:
            df: DataFrame للتصدير
            filename: اسم الملف (بدون الامتداد)
            format: تنسيق التصدير ('excel', 'csv', 'json', 'parquet')
            include_index: تضمين الفهرس
            encoding: ترميز الملف
            
        Returns:
            dict: معلومات عن الملف المصدر
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename}_{timestamp}"
        
        export_info = {
            'success': False,
            'message': '',
            'file_path': '',
            'file_size': 0,
            'download_link': ''
        }
        
        try:
            if format.lower() == 'excel':
                file_path = self._export_to_excel(df, base_filename, include_index)
                export_info['message'] = 'تم تصدير البيانات إلى Excel بنجاح'
                
            elif format.lower() == 'csv':
                file_path = self._export_to_csv(df, base_filename, encoding, include_index)
                export_info['message'] = 'تم تصدير البيانات إلى CSV بنجاح'
                
            elif format.lower() == 'json':
                file_path = self._export_to_json(df, base_filename)
                export_info['message'] = 'تم تصدير البيانات إلى JSON بنجاح'
                
            elif format.lower() == 'parquet':
                file_path = self._export_to_parquet(df, base_filename)
                export_info['message'] = 'تم تصدير البيانات إلى Parquet بنجاح'
                
            elif format.lower() == 'html':
                file_path = self._export_to_html(df, base_filename)
                export_info['message'] = 'تم تصدير البيانات إلى HTML بنجاح'
                
            else:
                export_info['message'] = f'تنسيق التصدير غير مدعوم: {format}'
                return export_info
            
            # جمع معلومات الملف
            if os.path.exists(file_path):
                export_info.update({
                    'success': True,
                    'file_path': str(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_name': os.path.basename(file_path),
                    'format': format,
                    'timestamp': timestamp
                })
                
        except Exception as e:
            export_info['message'] = f'خطأ في تصدير البيانات: {str(e)}'
            
        return export_info
    
    def _export_to_excel(
        self, 
        df: pd.DataFrame, 
        filename: str, 
        include_index: bool
    ) -> str:
        """تصدير إلى Excel مع أوراق متعددة"""
        file_path = self.output_dir / f"{filename}.xlsx"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # البيانات الرئيسية
            df.to_excel(writer, sheet_name='البيانات', index=include_index)
            
            # إحصائيات البيانات
            stats_df = self._create_data_stats(df)
            stats_df.to_excel(writer, sheet_name='الإحصائيات', index=True)
            
            # الأنواع الفريدة
            unique_df = self._create_unique_values(df)
            if not unique_df.empty:
                unique_df.to_excel(writer, sheet_name='القيم الفريدة', index=False)
            
            # المعلومات الأساسية
            info_df = self._create_dataframe_info(df)
            info_df.to_excel(writer, sheet_name='معلومات البيانات', index=False)
        
        return str(file_path)
    
    def _export_to_csv(
        self, 
        df: pd.DataFrame, 
        filename: str, 
        encoding: str, 
        include_index: bool
    ) -> str:
        """تصدير إلى CSV"""
        file_path = self.output_dir / f"{filename}.csv"
        
        df.to_csv(file_path, index=include_index, encoding=encoding)
        return str(file_path)
    
    def _export_to_json(
        self, 
        df: pd.DataFrame, 
        filename: str
    ) -> str:
        """تصدير إلى JSON"""
        file_path = self.output_dir / f"{filename}.json"
        
        # تصدير بالصيغة الجميلة
        df.to_json(file_path, orient='records', force_ascii=False, indent=2)
        return str(file_path)
    
    def _export_to_parquet(
        self, 
        df: pd.DataFrame, 
        filename: str
    ) -> str:
        """تصدير إلى Parquet"""
        file_path = self.output_dir / f"{filename}.parquet"
        
        df.to_parquet(file_path, engine='pyarrow')
        return str(file_path)
    
    def _export_to_html(
        self, 
        df: pd.DataFrame, 
        filename: str
    ) -> str:
        """تصدير إلى HTML"""
        file_path = self.output_dir / f"{filename}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تصدير بيانات المتجر الإلكتروني</title>
            <style>
                body {{ font-family: 'Arial', sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
                th {{ background-color: #4CAF50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .header {{ background-color: #333; color: white; padding: 20px; text-align: center; }}
                .footer {{ background-color: #333; color: white; padding: 10px; text-align: center; margin-top: 20px; }}
                .stats {{ margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>تصدير بيانات المتجر الإلكتروني</h1>
                <p>تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <div class="stats">
                <h3>معلومات البيانات:</h3>
                <p>عدد السجلات: {len(df):,}</p>
                <p>عدد الأعمدة: {len(df.columns)}</p>
            </div>
            
            {df.to_html(index=False, classes='data-table')}
            
            <div class="footer">
                <p>تم إنشاء هذا التقرير تلقائياً بواسطة نظام تحليل المتاجر الإلكترونية</p>
            </div>
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(file_path)
    
    def _create_data_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """إنشاء إحصائيات البيانات"""
        stats_data = []
        
        for col in df.columns:
            col_stats = {
                'العمود': col,
                'النوع': str(df[col].dtype),
                'القيم الفريدة': df[col].nunique(),
                'القيم المفقودة': df[col].isnull().sum(),
                '% المفقود': (df[col].isnull().sum() / len(df)) * 100,
                'العينة الأولى': str(df[col].iloc[0]) if len(df) > 0 else ''
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                numeric_col = pd.to_numeric(df[col], errors='coerce')
                col_stats.update({
                    'المتوسط': numeric_col.mean(),
                    'الوسيط': numeric_col.median(),
                    'الحد الأدنى': numeric_col.min(),
                    'الحد الأقصى': numeric_col.max(),
                    'الانحراف المعياري': numeric_col.std()
                })
            
            stats_data.append(col_stats)
        
        return pd.DataFrame(stats_data)
    
    def _create_unique_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """إنشاء قيم فريدة للأعمدة النصية"""
        unique_data = []
        
        for col in df.columns:
            if df[col].dtype == 'object' and df[col].nunique() <= 20:
                unique_vals = df[col].dropna().unique()[:10]  # أول 10 قيم فقط
                unique_str = ', '.join(str(v) for v in unique_vals)
                if len(unique_vals) == 10:
                    unique_str += '...'
                
                unique_data.append({
                    'العمود': col,
                    'القيم الفريدة (أول 10)': unique_str,
                    'عدد القيم الفريدة': df[col].nunique()
                })
        
        return pd.DataFrame(unique_data)
    
    def _create_dataframe_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """إنشاء معلومات عن DataFrame"""
        info_data = [
            ['عدد السجلات', len(df)],
            ['عدد الأعمدة', len(df.columns)],
            ['الأعمدة الرقمية', df.select_dtypes(include=[np.number]).shape[1]],
            ['الأعمدة النصية', df.select_dtypes(include=['object']).shape[1]],
            ['الأعمدة التاريخية', df.select_dtypes(include=['datetime64']).shape[1]],
            ['إجمالي القيم المفقودة', df.isnull().sum().sum()],
            ['نسبة البيانات المكتملة', f"{((1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))) * 100):.1f}%"],
            ['تاريخ الإنشاء', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        return pd.DataFrame(info_data, columns=['المعلومة', 'القيمة'])
    
    # ==================== تصدير التقارير ====================
    
    def export_report(
        self,
        report_text: str,
        filename: str,
        format: str = 'txt',
        title: str = "تقرير تحليل المتجر الإلكتروني"
    ) -> Dict[str, Any]:
        """
        تصدير التقرير النصي
        
        Args:
            report_text: نص التقرير
            filename: اسم الملف
            format: تنسيق التقرير ('txt', 'pdf', 'html', 'md')
            title: عنوان التقرير
            
        Returns:
            dict: معلومات التصدير
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename}_{timestamp}"
        
        export_info = {
            'success': False,
            'message': '',
            'file_path': '',
            'file_size': 0
        }
        
        try:
            if format.lower() == 'txt':
                file_path = self._export_text_report(report_text, base_filename)
                export_info['message'] = 'تم تصدير التقرير النصي بنجاح'
                
            elif format.lower() == 'pdf':
                file_path = self._export_pdf_report(report_text, base_filename, title)
                export_info['message'] = 'تم تصدير التقرير إلى PDF بنجاح'
                
            elif format.lower() == 'html':
                file_path = self._export_html_report(report_text, base_filename, title)
                export_info['message'] = 'تم تصدير التقرير إلى HTML بنجاح'
                
            elif format.lower() == 'md':
                file_path = self._export_markdown_report(report_text, base_filename)
                export_info['message'] = 'تم تصدير التقرير إلى Markdown بنجاح'
                
            else:
                export_info['message'] = f'تنسيق التقرير غير مدعوم: {format}'
                return export_info
            
            if os.path.exists(file_path):
                export_info.update({
                    'success': True,
                    'file_path': str(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_name': os.path.basename(file_path),
                    'format': format
                })
                
        except Exception as e:
            export_info['message'] = f'خطأ في تصدير التقرير: {str(e)}'
            
        return export_info
    
    def _export_text_report(self, report_text: str, filename: str) -> str:
        """تصدير تقرير نصي"""
        file_path = self.output_dir / f"{filename}.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        return str(file_path)
    
    def _export_pdf_report(self, report_text: str, filename: str, title: str) -> str:
        """تصدير تقرير PDF"""
        file_path = self.output_dir / f"{filename}.pdf"
        
        if HAS_REPORTLAB:
            self._create_pdf_with_reportlab(report_text, str(file_path), title)
        elif HAS_PDFKIT:
            self._create_pdf_with_pdfkit(report_text, str(file_path))
        else:
            # بديل بسيط إذا لم تكن المكتبات متوفرة
            self._create_simple_pdf(report_text, str(file_path))
        
        return str(file_path)
    
    def _create_pdf_with_reportlab(self, text: str, filepath: str, title: str):
        """إنشاء PDF باستخدام ReportLab"""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # العنوان
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E4053'),
            alignment=1,  # مركز
            spaceAfter=30
        )
        
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 20))
        
        # التاريخ
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=1
        )
        elements.append(Paragraph(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
        elements.append(Spacer(1, 30))
        
        # محتوى التقرير
        lines = text.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith('=' * 50):
                    # العنوان الرئيسي
                    heading_text = line.replace('=', '').strip()
                    elements.append(Paragraph(heading_text, styles['Heading2']))
                    elements.append(Spacer(1, 10))
                elif line.startswith('•') or line.startswith('-'):
                    # قائمة نقطية
                    elements.append(Paragraph(f"• {line[1:].strip()}", styles['Normal']))
                else:
                    elements.append(Paragraph(line, styles['Normal']))
                elements.append(Spacer(1, 5))
        
        doc.build(elements)
    
    def _create_pdf_with_pdfkit(self, text: str, filepath: str):
        """إنشاء PDF باستخدام PDFKit"""
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير تحليل المتجر الإلكتروني</title>
            <style>
                body {{ font-family: 'DejaVu Sans', sans-serif; line-height: 1.6; margin: 40px; }}
                h1 {{ color: #2E4053; text-align: center; }}
                h2 {{ color: #3498DB; border-bottom: 2px solid #3498DB; padding-bottom: 5px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ margin-bottom: 30px; }}
                .footer {{ text-align: center; margin-top: 50px; color: #7F8C8D; font-size: 12px; }}
                pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>تقرير تحليل المتجر الإلكتروني</h1>
                <p>تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <pre>{text}</pre>
            
            <div class="footer">
                <p>تم إنشاء هذا التقرير تلقائياً بواسطة نظام تحليل المتاجر الإلكترونية</p>
            </div>
        </body>
        </html>
        """
        
        pdfkit.from_string(html_content, filepath)
    
    def _create_simple_pdf(self, text: str, filepath: str):
        """إنشاء PDF بسيط (بديل عند عدم توفر مكتبات)"""
        # تحويل النص إلى HTML بسيط
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير تحليل المتجر الإلكتروني</title>
        </head>
        <body>
            <h1>تقرير تحليل المتجر الإلكتروني</h1>
            <p>تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <hr>
            <pre>{text}</pre>
        </body>
        </html>
        """
        
        # حفظ ك HTML (بديل للPDF)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # تغيير الامتداد إلى .html بدلاً من .pdf
        new_filepath = filepath.replace('.pdf', '.html')
        os.rename(filepath, new_filepath)
        return new_filepath
    
    def _export_html_report(self, report_text: str, filename: str, title: str) -> str:
        """تصدير تقرير HTML"""
        file_path = self.output_dir / f"{filename}.html"
        
        # تحويل النص إلى HTML
        html_lines = []
        lines = report_text.split('\n')
        
        for line in lines:
            if line.startswith('=' * 50):
                html_lines.append(f'<h2>{line.replace("=", "").strip()}</h2>')
            elif line.startswith('•'):
                html_lines.append(f'<li>{line[1:].strip()}</li>')
            elif line.strip():
                html_lines.append(f'<p>{line.strip()}</p>')
            else:
                html_lines.append('<br>')
        
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Arial', 'Segoe UI', sans-serif;
                    line-height: 1.8;
                    margin: 40px;
                    background-color: #f9f9f9;
                    color: #333;
                }}
                .container {{
                    max-width: 1000px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #4CAF50;
                }}
                h1 {{
                    color: #2E4053;
                    font-size: 32px;
                    margin-bottom: 10px;
                }}
                h2 {{
                    color: #3498DB;
                    border-right: 4px solid #3498DB;
                    padding-right: 15px;
                    margin-top: 30px;
                    margin-bottom: 20px;
                }}
                p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                ul {{
                    margin-right: 20px;
                    margin-bottom: 20px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7F8C8D;
                    font-size: 14px;
                }}
                .highlight {{
                    background-color: #FFF9C4;
                    padding: 2px 5px;
                    border-radius: 3px;
                }}
                .kpi {{
                    background-color: #E3F2FD;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    border-right: 4px solid #2196F3;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div class="content">
                    {''.join(html_lines)}
                </div>
                
                <div class="footer">
                    <p>تم إنشاء هذا التقرير تلقائياً بواسطة نظام تحليل المتاجر الإلكترونية</p>
                    <p>© {datetime.now().year} - جميع الحقوق محفوظة</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(file_path)
    
    def _export_markdown_report(self, report_text: str, filename: str) -> str:
        """تصدير تقرير Markdown"""
        file_path = self.output_dir / f"{filename}.md"
        
        md_content = f"""# تقرير تحليل المتجر الإلكتروني\n\n"""
        md_content += f"**تاريخ التقرير:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        md_content += "---\n\n"
        md_content += report_text.replace('•', '-')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return str(file_path)
    
    # ==================== تصدير الرسوم البيانية ====================
    
    def export_charts(
        self,
        figures: List[go.Figure],
        filenames: List[str] = None,
        format: str = 'png',
        width: int = 1200,
        height: int = 800,
        scale: int = 2
    ) -> Dict[str, Any]:
        """
        تصدير الرسوم البيانية
        
        Args:
            figures: قائمة الرسوم البيانية
            filenames: أسماء الملفات (اختياري)
            format: تنسيق الصورة ('png', 'jpeg', 'svg', 'pdf', 'html')
            width: العرض بالبكسل
            height: الارتفاع بالبكسل
            scale: مقياس الدقة
            
        Returns:
            dict: معلومات التصدير
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_info = {
            'success': False,
            'message': '',
            'files': [],
            'total_size': 0,
            'zip_file': None
        }
        
        try:
            exported_files = []
            
            for i, fig in enumerate(figures):
                if filenames and i < len(filenames):
                    base_name = filenames[i]
                else:
                    base_name = f"chart_{i+1}"
                
                filename = f"{base_name}_{timestamp}"
                file_info = self._export_single_chart(fig, filename, format, width, height, scale)
                
                if file_info['success']:
                    exported_files.append(file_info)
            
            if exported_files:
                # إنشاء ملف مضغوط لجميع الرسوم
                zip_path = self._create_charts_zip(exported_files, timestamp)
                
                export_info.update({
                    'success': True,
                    'message': f'تم تصدير {len(exported_files)} رسم بياني بنجاح',
                    'files': exported_files,
                    'total_size': sum(f['file_size'] for f in exported_files),
                    'zip_file': str(zip_path) if zip_path else None
                })
            else:
                export_info['message'] = 'لم يتم تصدير أي رسوم بيانية'
                
        except Exception as e:
            export_info['message'] = f'خطأ في تصدير الرسوم البيانية: {str(e)}'
            
        return export_info
    
    def _export_single_chart(
        self,
        figure: go.Figure,
        filename: str,
        format: str,
        width: int,
        height: int,
        scale: int
    ) -> Dict[str, Any]:
        """تصدير رسم بياني واحد"""
        file_info = {
            'success': False,
            'file_path': '',
            'file_size': 0,
            'format': format
        }
        
        try:
            if format.lower() == 'html':
                file_path = self.output_dir / f"{filename}.html"
                figure.write_html(str(file_path), include_plotlyjs='cdn')
                
            elif format.lower() in ['png', 'jpeg', 'pdf', 'svg']:
                file_path = self.output_dir / f"{filename}.{format}"
                figure.write_image(
                    str(file_path),
                    width=width,
                    height=height,
                    scale=scale,
                    engine='kaleido'  # أو 'orca'
                )
            else:
                file_info['message'] = f'تنسيق الرسم البياني غير مدعوم: {format}'
                return file_info
            
            if os.path.exists(file_path):
                file_info.update({
                    'success': True,
                    'file_path': str(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_name': os.path.basename(file_path)
                })
                
        except Exception as e:
            file_info['message'] = f'خطأ في تصدير الرسم البياني: {str(e)}'
            
        return file_info
    
    def _create_charts_zip(self, files_info: List[Dict], timestamp: str) -> Optional[str]:
        """إنشاء ملف مضغوط للرسوم البيانية"""
        if not files_info:
            return None
        
        zip_path = self.output_dir / f"charts_export_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in files_info:
                file_path = file_info['file_path']
                if os.path.exists(file_path):
                    zipf.write(file_path, os.path.basename(file_path))
        
        return str(zip_path)
    
    def export_chart_to_base64(
        self,
        figure: go.Figure,
        format: str = 'png',
        width: int = 800,
        height: int = 600
    ) -> str:
        """
        تصدير الرسم البياني إلى صيغة base64
        
        Returns:
            str: صورة base64
        """
        try:
            if format.lower() == 'svg':
                img_bytes = figure.to_image(format='svg')
            else:
                img_bytes = figure.to_image(format=format, width=width, height=height)
            
            base64_str = base64.b64encode(img_bytes).decode('utf-8')
            
            if format.lower() == 'svg':
                return f"data:image/svg+xml;base64,{base64_str}"
            else:
                return f"data:image/{format};base64,{base64_str}"
                
        except Exception as e:
            print(f"Error exporting chart to base64: {e}")
            return ""
    
    # ==================== تصدير التحليلات ====================
    
    def export_analysis(
        self,
        analysis_data: Dict[str, Any],
        filename: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        تصدير نتائج التحليل
        
        Args:
            analysis_data: بيانات التحليل
            filename: اسم الملف
            format: تنسيق التصدير ('json', 'excel', 'html')
            
        Returns:
            dict: معلومات التصدير
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{filename}_{timestamp}"
        
        export_info = {
            'success': False,
            'message': '',
            'file_path': '',
            'file_size': 0
        }
        
        try:
            if format.lower() == 'json':
                file_path = self._export_analysis_json(analysis_data, base_filename)
                export_info['message'] = 'تم تصدير التحليل إلى JSON بنجاح'
                
            elif format.lower() == 'excel':
                file_path = self._export_analysis_excel(analysis_data, base_filename)
                export_info['message'] = 'تم تصدير التحليل إلى Excel بنجاح'
                
            elif format.lower() == 'html':
                file_path = self._export_analysis_html(analysis_data, base_filename)
                export_info['message'] = 'تم تصدير التحليل إلى HTML بنجاح'
                
            else:
                export_info['message'] = f'تنسيق التحليل غير مدعوم: {format}'
                return export_info
            
            if os.path.exists(file_path):
                export_info.update({
                    'success': True,
                    'file_path': str(file_path),
                    'file_size': os.path.getsize(file_path),
                    'file_name': os.path.basename(file_path)
                })
                
        except Exception as e:
            export_info['message'] = f'خطأ في تصدير التحليل: {str(e)}'
            
        return export_info
    
    def _export_analysis_json(self, analysis_data: Dict, filename: str) -> str:
        """تصدير التحليل إلى JSON"""
        file_path = self.output_dir / f"{filename}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
        
        return str(file_path)
    
    def _export_analysis_excel(self, analysis_data: Dict, filename: str) -> str:
        """تصدير التحليل إلى Excel مع أوراق متعددة"""
        file_path = self.output_dir / f"{filename}.xlsx"
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # تصدير كل قسم في ورقة منفصلة
            for section_name, section_data in analysis_data.items():
                if isinstance(section_data, dict):
                    # تحويل القاموس إلى DataFrame
                    if all(isinstance(v, (int, float, str)) for v in section_data.values()):
                        df = pd.DataFrame([section_data])
                    else:
                        # محاولة تسطيح البيانات المتداخلة
                        flat_data = self._flatten_dict(section_data)
                        df = pd.DataFrame([flat_data])
                elif isinstance(section_data, list):
                    df = pd.DataFrame(section_data)
                else:
                    continue
                
                # تقليل اسم الورقة إذا كان طويلاً
                sheet_name = str(section_name)[:31]  # Excel limit
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        return str(file_path)
    
    def _flatten_dict(self, nested_dict: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """تسطيح القاموس المتداخل"""
        items = []
        for k, v in nested_dict.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # تحويل القائمة إلى سلسلة
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _export_analysis_html(self, analysis_data: Dict, filename: str) -> str:
        """تصدير التحليل إلى HTML"""
        file_path = self.output_dir / f"{filename}.html"
        
        html_content = self._generate_analysis_html(analysis_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(file_path)
    
    def _generate_analysis_html(self, analysis_data: Dict) -> str:
        """إنشاء HTML لنتائج التحليل"""
        
        sections_html = ""
        
        for section_name, section_data in analysis_data.items():
            section_title = section_name.replace('_', ' ').title()
            
            if isinstance(section_data, dict):
                items_html = ""
                for key, value in section_data.items():
                    if isinstance(value, dict):
                        value_str = "<ul>"
                        for sub_key, sub_value in value.items():
                            value_str += f"<li><strong>{sub_key}:</strong> {sub_value}</li>"
                        value_str += "</ul>"
                    else:
                        value_str = str(value)
                    
                    items_html += f"""
                    <div class="analysis-item">
                        <span class="item-key">{key}:</span>
                        <span class="item-value">{value_str}</span>
                    </div>
                    """
                
                sections_html += f"""
                <div class="analysis-section">
                    <h3>{section_title}</h3>
                    <div class="section-content">
                        {items_html}
                    </div>
                </div>
                """
            elif isinstance(section_data, list):
                list_items = ""
                for item in section_data:
                    list_items += f"<li>{item}</li>"
                
                sections_html += f"""
                <div class="analysis-section">
                    <h3>{section_title}</h3>
                    <ul class="section-list">
                        {list_items}
                    </ul>
                </div>
                """
        
        html = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>نتائج تحليل المتجر الإلكتروني</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f7fa;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #4CAF50;
                }}
                h1 {{
                    color: #2E4053;
                    margin-bottom: 10px;
                }}
                h3 {{
                    color: #3498DB;
                    border-right: 4px solid #3498DB;
                    padding-right: 15px;
                    margin-top: 30px;
                    margin-bottom: 20px;
                }}
                .analysis-section {{
                    margin-bottom: 30px;
                    padding: 20px;
                    background-color: #f9f9f9;
                    border-radius: 8px;
                    border-right: 3px solid #ddd;
                }}
                .analysis-item {{
                    margin-bottom: 10px;
                    padding: 8px 12px;
                    background-color: white;
                    border-radius: 5px;
                    display: flex;
                    justify-content: space-between;
                    border-right: 2px solid #eee;
                }}
                .item-key {{
                    font-weight: bold;
                    color: #2E4053;
                }}
                .item-value {{
                    color: #7F8C8D;
                }}
                .section-list {{
                    list-style-type: none;
                    padding: 0;
                }}
                .section-list li {{
                    padding: 10px 15px;
                    margin-bottom: 8px;
                    background-color: #E3F2FD;
                    border-radius: 5px;
                    border-right: 3px solid #2196F3;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    color: #7F8C8D;
                    font-size: 14px;
                }}
                .highlight {{
                    background-color: #FFF9C4;
                    padding: 2px 5px;
                    border-radius: 3px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>نتائج تحليل المتجر الإلكتروني</h1>
                    <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
                
                <div class="analysis-content">
                    {sections_html}
                </div>
                
                <div class="footer">
                    <p>تم إنشاء هذا التقرير تلقائياً بواسطة نظام تحليل المتاجر الإلكترونية</p>
                    <p>© {datetime.now().year} - جميع الحقوق محفوظة</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # ==================== تصدير شامل ====================
    
    def export_comprehensive_report(
        self,
        dataframes: Dict[str, pd.DataFrame],
        analysis_results: Dict[str, Any],
        report_text: str,
        figures: List[go.Figure] = None,
        base_filename: str = "ecommerce_analysis"
    ) -> Dict[str, Any]:
        """
        تصدير تقرير شامل متعدد الأجزاء
        
        Args:
            dataframes: DataFrames للتصدير
            analysis_results: نتائج التحليل
            report_text: نص التقرير
            figures: الرسوم البيانية
            base_filename: اسم الملف الأساسي
            
        Returns:
            dict: معلومات التصدير الشامل
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_info = {
            'success': False,
            'message': '',
            'files': [],
            'zip_file': None,
            'total_size': 0
        }
        
        try:
            exported_files = []
            
            # 1. تصدير البيانات
            for df_name, df in dataframes.items():
                if df_name in ['raw_data', 'processed_data', 'merged_data']:
                    df_filename = f"{base_filename}_{df_name}_{timestamp}"
                    df_export = self.export_dataframe(df, df_filename, 'excel')
                    
                    if df_export['success']:
                        exported_files.append({
                            'type': 'data',
                            'name': df_name,
                            'info': df_export
                        })
            
            # 2. تصدير التحليل
            analysis_filename = f"{base_filename}_analysis_{timestamp}"
            analysis_export = self.export_analysis(analysis_results, analysis_filename, 'excel')
            
            if analysis_export['success']:
                exported_files.append({
                    'type': 'analysis',
                    'name': 'analysis_results',
                    'info': analysis_export
                })
            
            # 3. تصدير التقرير
            report_filename = f"{base_filename}_report_{timestamp}"
            report_export = self.export_report(report_text, report_filename, 'pdf', 'تقرير تحليل المتجر')
            
            if report_export['success']:
                exported_files.append({
                    'type': 'report',
                    'name': 'analysis_report',
                    'info': report_export
                })
            
            # 4. تصدير الرسوم البيانية
            if figures:
                charts_export = self.export_charts(
                    figures, 
                    [f"{base_filename}_chart_{i+1}" for i in range(len(figures))],
                    'png'
                )
                
                if charts_export['success'] and charts_export.get('zip_file'):
                    exported_files.append({
                        'type': 'charts',
                        'name': 'all_charts',
                        'info': {
                            'file_path': charts_export['zip_file'],
                            'file_size': charts_export['total_size']
                        }
                    })
            
            # 5. إنشاء دليل README
            readme_content = self._create_readme_file(dataframes, analysis_results, timestamp)
            readme_path = self.output_dir / f"README_{timestamp}.txt"
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            exported_files.append({
                'type': 'readme',
                'name': 'readme',
                'info': {
                    'file_path': str(readme_path),
                    'file_size': os.path.getsize(readme_path)
                }
            })
            
            # 6. إنشاء ملف مضغوط شامل
            if exported_files:
                zip_path = self._create_comprehensive_zip(exported_files, base_filename, timestamp)
                
                export_info.update({
                    'success': True,
                    'message': f'تم تصدير {len(exported_files)} ملف بنجاح',
                    'files': exported_files,
                    'zip_file': str(zip_path),
                    'total_size': sum(f['info'].get('file_size', 0) for f in exported_files)
                })
            else:
                export_info['message'] = 'لم يتم تصدير أي ملفات'
                
        except Exception as e:
            export_info['message'] = f'خطأ في التصدير الشامل: {str(e)}'
            
        return export_info
    
    def _create_readme_file(
        self, 
        dataframes: Dict[str, pd.DataFrame], 
        analysis_results: Dict[str, Any],
        timestamp: str
    ) -> str:
        """إنشاء ملف README للتقرير الشامل"""
        
        readme_content = f"""
        ========================================
        تقرير تحليل المتجر الإلكتروني - ملف README
        ========================================
        
        معلومات التصدير:
        - تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        - معرّف الدفعة: {timestamp}
        
        الملفات المصدرة:
        """
        
        # معلومات DataFrames
        for df_name, df in dataframes.items():
            readme_content += f"""
        - {df_name}.xlsx:
          • عدد السجلات: {len(df):,}
          • عدد الأعمدة: {len(df.columns)}
          • الحقول: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}
            """
        
        # معلومات التحليل
        if 'store_profile' in analysis_results:
            profile = analysis_results['store_profile']
            readme_content += f"""
        
        معلومات المتجر:
        - نوع المتجر: {profile.get('store_type', 'غير محدد')}
        - عدد المنتجات: {profile.get('total_products', 0)}
        - عدد العملاء: {profile.get('total_customers', 0)}
        - عدد الطلبات: {profile.get('total_orders', 0)}
            """
        
        readme_content += f"""
        
        هيكل المجلد:
        - البيانات الخام: البيانات الأصلية قبل المعالجة
        - التحليلات: نتائج التحليل والإحصائيات
        - التقارير: التقارير النصية والرسوم البيانية
        - الرسوم: الرسوم البيانية والتصورات
        
        معلومات الاتصال:
        - نظام تحليل المتاجر الإلكترونية
        - البريد الإلكتروني: support@ecommerce-analytics.com
        - الموقع: https://analytics.ecommerce.com
        
        ========================================
        نهاية الملف
        ========================================
        """
        
        return readme_content
    
    def _create_comprehensive_zip(
        self, 
        files_info: List[Dict], 
        base_filename: str, 
        timestamp: str
    ) -> str:
        """إنشاء ملف مضغوط شامل"""
        zip_path = self.output_dir / f"{base_filename}_full_export_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in files_info:
                file_path = file_info['info'].get('file_path')
                if file_path and os.path.exists(file_path):
                    # إضافة الملف بالاسم المناسب
                    file_type = file_info['type']
                    file_name = file_info['name']
                    ext = os.path.splitext(file_path)[1]
                    
                    zip_name = f"{file_type}/{file_name}{ext}"
                    zipf.write(file_path, zip_name)
        
        return str(zip_path)
    
    # ==================== أدوات مساعدة ====================
    
    def get_export_formats(self) -> Dict[str, List[str]]:
        """الحصول على قائمة بالتنسيقات المدعومة"""
        return {
            'data': ['excel', 'csv', 'json', 'parquet', 'html'],
            'reports': ['txt', 'pdf', 'html', 'md'],
            'charts': ['png', 'jpeg', 'svg', 'pdf', 'html'],
            'analysis': ['json', 'excel', 'html']
        }
    
    def cleanup_old_exports(self, days_old: int = 7) -> int:
        """
        تنظيف الملفات القديمة
        
        Args:
            days_old: عدد الأيام للحفاظ على الملفات
            
        Returns:
            int: عدد الملفات المحذوفة
        """
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for file_path in self.output_dir.glob('**/*'):
            if file_path.is_file():
                if os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                    except:
                        pass
        
        return deleted_count
    
    def get_export_stats(self) -> Dict[str, Any]:
        """الحصول على إحصائيات الملفات المصدرة"""
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'file_types': {},
            'recent_exports': []
        }
        
        for file_path in self.output_dir.glob('**/*'):
            if file_path.is_file():
                stats['total_files'] += 1
                stats['total_size_mb'] += os.path.getsize(file_path) / (1024 * 1024)
                
                ext = file_path.suffix.lower()
                stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                
                stats['recent_exports'].append({
                    'name': file_path.name,
                    'size_mb': os.path.getsize(file_path) / (1024 * 1024),
                    'modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                    'path': str(file_path)
                })
        
        # ترتيب الملفات الحديثة
        stats['recent_exports'].sort(key=lambda x: x['modified'], reverse=True)
        stats['recent_exports'] = stats['recent_exports'][:10]  # آخر 10 ملفات فقط
        
        return stats

# ==================== واجهات مبسطة ====================

def export_to_excel(df: pd.DataFrame, filename: str) -> str:
    """واجهة مبسطة لتصدير إلى Excel"""
    exporter = EcommerceExporters()
    result = exporter.export_dataframe(df, filename, 'excel')
    return result['file_path'] if result['success'] else None

def export_to_csv(df: pd.DataFrame, filename: str) -> str:
    """واجهة مبسطة لتصدير إلى CSV"""
    exporter = EcommerceExporters()
    result = exporter.export_dataframe(df, filename, 'csv')
    return result['file_path'] if result['success'] else None

def export_to_pdf(report_text: str, filename: str) -> str:
    """واجهة مبسطة لتصدير إلى PDF"""
    exporter = EcommerceExporters()
    result = exporter.export_report(report_text, filename, 'pdf')
    return result['file_path'] if result['success'] else None

def export_chart_image(figure: go.Figure, filename: str) -> str:
    """واجهة مبسطة لتصدير الرسم البياني"""
    exporter = EcommerceExporters()
    result = exporter.export_charts([figure], [filename], 'png')
    
    if result['success'] and result['files']:
        return result['files'][0]['file_path']
    return None

# ==================== اختبار الوحدة ====================

if __name__ == "__main__":
    print("اختبار وحدة التصدير...")
    
    # إنشاء بيانات تجريبية
    test_df = pd.DataFrame({
        'المنتج': ['منتج 1', 'منتج 2', 'منتج 3'],
        'الكمية': [10, 20, 15],
        'السعر': [100, 200, 150],
        'التاريخ': pd.date_range('2024-01-01', periods=3)
    })
    
    # إنشاء رسم بياني تجريبي
    test_fig = px.bar(test_df, x='المنتج', y='الكمية', title='المنتجات المباعة')
    
    # إنشاء تحليل تجريبي
    test_analysis = {
        'store_profile': {
            'store_type': 'fashion',
            'total_products': 50,
            'total_customers': 100
        },
        'performance_kpis': {
            'gmv': 50000,
            'aov': 150
        }
    }
    
    # اختبار المصدر
    exporter = EcommerceExporters('test_exports')
    
    # 1. تصدير البيانات
    print("1. تصدير البيانات...")
    data_result = exporter.export_dataframe(test_df, 'test_data', 'excel')
    print(f"   النتيجة: {data_result['message']}")
    
    # 2. تصدير الرسم البياني
    print("2. تصدير الرسم البياني...")
    chart_result = exporter.export_charts([test_fig], ['test_chart'], 'png')
    print(f"   النتيجة: {chart_result['message']}")
    
    # 3. تصدير التحليل
    print("3. تصدير التحليل...")
    analysis_result = exporter.export_analysis(test_analysis, 'test_analysis', 'json')
    print(f"   النتيجة: {analysis_result['message']}")
    
    # 4. تصدير التقرير
    print("4. تصدير التقرير...")
    report_text = "هذا تقرير تجريبي\nلاختبار نظام التصدير"
    report_result = exporter.export_report(report_text, 'test_report', 'txt')
    print(f"   النتيجة: {report_result['message']}")
    
    # 5. الحصول على إحصائيات
    print("5. إحصائيات التصدير...")
    stats = exporter.get_export_stats()
    print(f"   عدد الملفات: {stats['total_files']}")
    print(f"   الحجم الإجمالي: {stats['total_size_mb']:.2f} MB")
    
    print("\nتم اختبار وحدة التصدير بنجاح!")