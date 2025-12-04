
#!/usr/bin/env python3
"""
ecom_analytics.py - المنصة الرئيسية لتحليل بيانات التجارة الإلكترونية
الملف الرئيسي للتطبيق مع واجهة المستخدم الرسومية
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# استيراد الوحدات الداخلية
from modules.detector import StoreDetector
from modules.mapper import ColumnMapper
from modules.analyzer import SalesAnalyzer
from modules.visualizer import DataVisualizer
from modules.reporter import ReportGenerator
from utils.translation import Translator
from utils.helpers import DataProcessor, FileHandler
from utils.validators import DataValidator
from utils.exporters import ReportExporter


class EcommerceAnalyticsApp:
    """التطبيق الرئيسي لمنصة تحليل بيانات التجارة الإلكترونية"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("منصة تحليل بيانات التجارة الإلكترونية")
        self.root.geometry("1200x800")
        
        # تهيئة المتغيرات
        self.dataframe = None
        self.store_type = None
        self.analysis_results = {}
        self.current_language = 'ar'  # اللغة الافتراضية: العربية
        self.translator = Translator()
        
        # إنشاء مجلدات التطبيق
        self.create_app_folders()
        
        # تحميل الإعدادات
        self.config = self.load_config()
        
        # تهيئة الوحدات
        self.init_modules()
        
        # إنشاء واجهة المستخدم
        self.setup_ui()
        
        # تعيين أيقونة التطبيق
        self.set_icon()
        
    def create_app_folders(self):
        """إنشاء المجلدات المطلوبة للتطبيق"""
        folders = ['data/uploaded', 'data/processed', 'reports', 'reports/templates']
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def load_config(self):
        """تحميل إعدادات التطبيق من ملف config.json"""
        config_path = 'config.json'
        default_config = {
            "app_name": "Ecommerce Analytics Platform",
            "version": "1.0.0",
            "supported_formats": [".csv", ".xlsx", ".xls"],
            "default_language": "ar",
            "max_file_size_mb": 50,
            "report_templates": {
                "arabic": "templates/report_template_ar.html",
                "english": "templates/report_template_en.html"
            }
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # إنشاء ملف الإعدادات الافتراضي
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, ensure_ascii=False, indent=4)
                return default_config
        except Exception as e:
            print(f"خطأ في تحميل الإعدادات: {e}")
            return default_config
    
    def init_modules(self):
        """تهيئة الوحدات الرئيسية"""
        self.store_detector = StoreDetector()
        self.column_mapper = ColumnMapper()
        self.sales_analyzer = SalesAnalyzer()
        self.data_visualizer = DataVisualizer()
        self.report_generator = ReportGenerator()
        self.data_processor = DataProcessor()
        self.file_handler = FileHandler()
        self.data_validator = DataValidator()
        self.report_exporter = ReportExporter()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # إنشاء شريط القوائم
        self.setup_menu()
        
        # إنشاء دفتر تبويب رئيسي
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # إنشاء تبويبات
        self.setup_upload_tab()
        self.setup_mapping_tab()
        self.setup_analysis_tab()
        self.setup_visualization_tab()
        self.setup_report_tab()
        self.setup_log_tab()
        
        # تعطيل التبويبات في البداية
        self.disable_tabs()
    
    def setup_menu(self):
        """إعداد شريط القوائم"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="فتح ملف", command=self.open_file)
        file_menu.add_command(label="فتح ملف حديث", command=self.open_recent_file)
        file_menu.add_separator()
        file_menu.add_command(label="حفظ التقرير", command=self.save_report)
        file_menu.add_command(label="تصدير النتائج", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # قائمة التحرير
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="تحرير", menu=edit_menu)
        edit_menu.add_command(label="تفضيلات", command=self.open_settings)
        
        # قائمة العرض
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="عرض", menu=view_menu)
        view_menu.add_command(label="تغيير اللغة", command=self.toggle_language)
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        help_menu.add_command(label="دليل المستخدم", command=self.show_help)
        help_menu.add_command(label="عن البرنامج", command=self.show_about)
    
    def setup_upload_tab(self):
        """إعداد تبويب رفع الملفات"""
        self.upload_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.upload_tab, text="رفع البيانات")
        
        # إطار العنوان
        title_frame = ttk.LabelFrame(self.upload_tab, text="رفع ملف البيانات")
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(title_frame, text="منصة تحليل بيانات التجارة الإلكترونية", 
                 font=("Arial", 16, "bold")).pack(pady=10)
        
        ttk.Label(title_frame, text="قم برفع ملف بيانات المبيعات (CSV أو Excel) للبدء في التحليل",
                 font=("Arial", 11)).pack(pady=5)
        
        # إطار رفع الملف
        upload_frame = ttk.Frame(self.upload_tab)
        upload_frame.pack(pady=50)
        
        # زر رفع الملف
        self.upload_btn = ttk.Button(upload_frame, text="اختر ملف البيانات", 
                                    command=self.open_file, width=30)
        self.upload_btn.pack(pady=10)
        
        # معلومات الملف
        self.file_info_frame = ttk.LabelFrame(upload_frame, text="معلومات الملف")
        self.file_info_frame.pack(pady=20, fill=tk.X, padx=50)
        
        self.file_info_text = tk.Text(self.file_info_frame, height=8, width=60)
        self.file_info_text.pack(padx=10, pady=10)
        self.file_info_text.config(state=tk.DISABLED)
        
        # شريط التقدم
        self.progress_bar = ttk.Progressbar(upload_frame, length=400, mode='indeterminate')
        self.progress_bar.pack(pady=10)
        
        # زر التحليل
        self.analyze_btn = ttk.Button(upload_frame, text="بدء التحليل", 
                                     command=self.start_analysis, state=tk.DISABLED)
        self.analyze_btn.pack(pady=20)
    
    def setup_mapping_tab(self):
        """إعداد تبويب تعيين الأعمدة"""
        self.mapping_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mapping_tab, text="تعيين الأعمدة")
        
        ttk.Label(self.mapping_tab, text="تعيين أعمدة البيانات", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # إطار تعيين الأعمدة
        self.mapping_frame = ttk.LabelFrame(self.mapping_tab, text="تعيين الحقول")
        self.mapping_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # قائمة الأعمدة
        self.column_listbox = tk.Listbox(self.mapping_frame, height=15)
        self.column_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # إطار التحكم
        control_frame = ttk.Frame(self.mapping_frame)
        control_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        ttk.Label(control_frame, text="تعيين كـ:").pack(pady=5)
        
        self.mapping_combo = ttk.Combobox(control_frame, values=[
            "معرف المنتج", "اسم المنتج", "الكمية", "السعر", 
            "التاريخ", "العملة", "الفئة", "البلد", "العميل"
        ])
        self.mapping_combo.pack(pady=5)
        
        ttk.Button(control_frame, text="تعيين", command=self.map_column).pack(pady=10)
        ttk.Button(control_frame, text="تلقائي", command=self.auto_map).pack(pady=5)
        ttk.Button(control_frame, text="مسح الكل", command=self.clear_mapping).pack(pady=5)
        
        # عرض التعيينات
        self.mapping_text = scrolledtext.ScrolledText(self.mapping_frame, height=10)
        self.mapping_text.pack(fill=tk.X, padx=5, pady=5)
    
    def setup_analysis_tab(self):
        """إعداد تبويب التحليل"""
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="التحليل")
        
        # إطار النتائج
        self.results_frame = ttk.LabelFrame(self.analysis_tab, text="نتائج التحليل")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # دفتر تبويب للنتائج
        self.results_notebook = ttk.Notebook(self.results_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # تبويب الملخص
        self.summary_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.summary_tab, text="ملخص")
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_tab, height=20)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تبويب الإحصائيات
        self.stats_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.stats_tab, text="إحصائيات")
        
        self.stats_text = scrolledtext.ScrolledText(self.stats_tab, height=20)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # تبويب التحليل الزمني
        self.temporal_tab = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.temporal_tab, text="تحليل زمني")
        
        self.temporal_text = scrolledtext.ScrolledText(self.temporal_tab, height=20)
        self.temporal_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_visualization_tab(self):
        """إعداد تبويب الرسوم البيانية"""
        self.visualization_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.visualization_tab, text="الرسوم البيانية")
        
        # إطار التحكم
        control_frame = ttk.Frame(self.visualization_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(control_frame, text="نوع الرسم البياني:").pack(side=tk.LEFT, padx=5)
        
        self.chart_combo = ttk.Combobox(control_frame, values=[
            "مبيعات يومية", "مبيعات شهرية", "أفضل المنتجات", 
            "توزيع الفئات", "اتجاه المبيعات", "خريطة المبيعات"
        ])
        self.chart_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="عرض", command=self.generate_chart).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="حفظ الصورة", command=self.save_chart).pack(side=tk.LEFT, padx=5)
        
        # إطار الرسم البياني
        self.chart_frame = ttk.Frame(self.visualization_tab)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_report_tab(self):
        """إعداد تبويب التقرير"""
        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text="التقرير")
        
        # إطار التقرير
        report_control_frame = ttk.Frame(self.report_tab)
        report_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(report_control_frame, text="إنشاء التقرير", 
                  command=self.generate_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(report_control_frame, text="حفظ كـ PDF", 
                  command=self.save_pdf_report).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(report_control_frame, text="حفظ كـ HTML", 
                  command=self.save_html_report).pack(side=tk.LEFT, padx=5)
        
        # عرض التقرير
        self.report_text = scrolledtext.ScrolledText(self.report_tab, height=30)
        self.report_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_log_tab(self):
        """إعداد تبويب السجل"""
        self.log_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.log_tab, text="سجل النظام")
        
        self.log_text = scrolledtext.ScrolledText(self.log_tab, height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # أزرار السجل
        log_buttons_frame = ttk.Frame(self.log_tab)
        log_buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(log_buttons_frame, text="مسح السجل", 
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(log_buttons_frame, text="حفظ السجل", 
                  command=self.save_log).pack(side=tk.LEFT, padx=5)
    
    def disable_tabs(self):
        """تعطيل جميع التبويبات عدا تبويب الرفع"""
        for i in range(1, self.notebook.index("end")):
            self.notebook.tab(i, state="disabled")
    
    def enable_tabs(self):
        """تفعيل جميع التبويب"""
        for i in range(self.notebook.index("end")):
            self.notebook.tab(i, state="normal")
    
    def open_file(self):
        """فتح ملف البيانات"""
        file_types = [
            ("ملفات CSV", "*.csv"),
            ("ملفات Excel", "*.xlsx"),
            ("ملفات Excel", "*.xls"),
            ("جميع الملفات", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="اختر ملف البيانات",
            filetypes=file_types
        )
        
        if file_path:
            self.process_file(file_path)
    
    def process_file(self, file_path):
        """معالجة الملف المرفوع"""
        try:
            self.show_progress(True)
            self.log_message(f"جاري معالجة الملف: {file_path}")
            
            # نسخ الملف إلى مجلد المرفوعات
            filename = os.path.basename(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            saved_path = f"data/uploaded/{timestamp}_{filename}"
            
            import shutil
            shutil.copy2(file_path, saved_path)
            
            # قراءة الملف
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            else:
                df = pd.read_excel(file_path)
            
            self.dataframe = df
            self.log_message(f"تم تحميل الملف بنجاح: {filename}")
            self.log_message(f"عدد الصفوف: {len(df)}، عدد الأعمدة: {len(df.columns)}")
            
            # تحديث معلومات الملف
            self.update_file_info(df, filename)
            
            # كشف نوع المتجر
            self.detect_store_type(df)
            
            # تمكين زر التحليل
            self.analyze_btn.config(state=tk.NORMAL)
            
            # تحديث قائمة الأعمدة
            self.update_column_list(df)
            
            self.log_message("جاهز للتحليل. اضغط على 'بدء التحليل' للمتابعة.")
            
        except Exception as e:
            self.log_message(f"خطأ في معالجة الملف: {str(e)}", error=True)
            messagebox.showerror("خطأ", f"حدث خطأ في معالجة الملف:\n{str(e)}")
        finally:
            self.show_progress(False)
    
    def update_file_info(self, df, filename):
        """تحديث معلومات الملف"""
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        
        info = f"اسم الملف: {filename}\n"
        info += f"عدد الصفوف: {len(df):,}\n"
        info += f"عدد الأعمدة: {len(df.columns)}\n"
        info += f"نوع الملف: {filename.split('.')[-1].upper()}\n\n"
        info += "الأعمدة:\n"
        
        for i, col in enumerate(df.columns):
            info += f"{i+1}. {col}\n"
            if i >= 10:  # عرض أول 10 أعمدة فقط
                info += f"... و {len(df.columns) - 10} أعمدة أخرى\n"
                break
        
        self.file_info_text.insert(1.0, info)
        self.file_info_text.config(state=tk.DISABLED)
    
    def detect_store_type(self, df):
        """كشف نوع المتجر"""
        try:
            self.store_type = self.store_detector.detect(df)
            self.log_message(f"نوع المتجر المكتشف: {self.store_type}")
            
            # تحديث معلومات الملف
            self.file_info_text.config(state=tk.NORMAL)
            self.file_info_text.insert(tk.END, f"\nنوع المتجر: {self.store_type}\n")
            self.file_info_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.log_message(f"خطأ في كشف نوع المتجر: {str(e)}", warning=True)
            self.store_type = "غير محدد"
    
    def update_column_list(self, df):
        """تحديث قائمة الأعمدة"""
        self.column_listbox.delete(0, tk.END)
        for col in df.columns:
            self.column_listbox.insert(tk.END, col)
    
    def start_analysis(self):
        """بدء عملية التحليل"""
        if self.dataframe is None:
            messagebox.showwarning("تحذير", "الرجاء رفع ملف بيانات أولاً")
            return
        
        try:
            self.show_progress(True)
            self.log_message("بدء عملية التحليل...")
            
            # تفعيل التبويبات
            self.enable_tabs()
            
            # تعيين الأعمدة تلقائياً
            self.auto_map()
            
            # معالجة البيانات
            processed_df = self.data_processor.clean_data(self.dataframe)
            
            # التحليل
            self.analysis_results = self.sales_analyzer.analyze(processed_df)
            
            # عرض النتائج
            self.display_analysis_results()
            
            # إنشاء الرسوم البيانية الأولية
            self.create_initial_charts(processed_df)
            
            self.log_message("تم التحليل بنجاح!")
            
            # التبديل إلى تبويب النتائج
            self.notebook.select(2)  # تبويب التحليل
            
        except Exception as e:
            self.log_message(f"خطأ في التحليل: {str(e)}", error=True)
            messagebox.showerror("خطأ", f"حدث خطأ في التحليل:\n{str(e)}")
        finally:
            self.show_progress(False)
    
    def display_analysis_results(self):
        """عرض نتائج التحليل"""
        if not self.analysis_results:
            return
        
        # عرض الملخص
        summary = "ملخص النتائج:\n\n"
        summary += f"إجمالي المبيعات: {self.analysis_results.get('total_sales', 0):,.2f}\n"
        summary += f"متوسط المبيعات اليومية: {self.analysis_results.get('avg_daily_sales', 0):,.2f}\n"
        summary += f"عدد المنتجات المباعة: {self.analysis_results.get('total_products_sold', 0):,}\n"
        summary += f"عدد العملاء: {self.analysis_results.get('total_customers', 0)}\n"
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, summary)
        
        # عرض الإحصائيات
        stats = "الإحصائيات التفصيلية:\n\n"
        for key, value in self.analysis_results.get('statistics', {}).items():
            stats += f"{key}: {value}\n"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        
        # عرض التحليل الزمني
        temporal = "التحليل الزمني:\n\n"
        temporal_data = self.analysis_results.get('temporal_analysis', {})
        for period, data in temporal_data.items():
            temporal += f"{period}:\n"
            for item in data:
                temporal += f"  {item}\n"
        
        self.temporal_text.delete(1.0, tk.END)
        self.temporal_text.insert(1.0, temporal)
    
    def create_initial_charts(self, df):
        """إنشاء الرسوم البيانية الأولية"""
        try:
            # مسح الإطار الحالي
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # إنشاء رسم بياني للمبيعات الشهرية
            fig = self.data_visualizer.create_monthly_sales_chart(df)
            
            # تضمين الرسم في الواجهة
            canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.log_message("تم إنشاء الرسم البياني الأولي")
            
        except Exception as e:
            self.log_message(f"خطأ في إنشاء الرسم البياني: {str(e)}", warning=True)
    
    def generate_chart(self):
        """إنشاء رسم بياني حسب الاختيار"""
        if self.dataframe is None:
            return
        
        chart_type = self.chart_combo.get()
        if not chart_type:
            return
        
        try:
            # مسح الإطار الحالي
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            fig = None
            
            # إنشاء الرسم البياني المحدد
            if chart_type == "مبيعات يومية":
                fig = self.data_visualizer.create_daily_sales_chart(self.dataframe)
            elif chart_type == "مبيعات شهرية":
                fig = self.data_visualizer.create_monthly_sales_chart(self.dataframe)
            elif chart_type == "أفضل المنتجات":
                fig = self.data_visualizer.create_top_products_chart(self.dataframe)
            elif chart_type == "توزيع الفئات":
                fig = self.data_visualizer.create_category_distribution_chart(self.dataframe)
            elif chart_type == "اتجاه المبيعات":
                fig = self.data_visualizer.create_sales_trend_chart(self.dataframe)
            elif chart_type == "خريطة المبيعات":
                fig = self.data_visualizer.create_sales_map(self.dataframe)
            
            if fig:
                # تضمين الرسم في الواجهة
                canvas = FigureCanvasTkAgg(fig, self.chart_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
                
                self.log_message(f"تم إنشاء الرسم البياني: {chart_type}")
            else:
                self.log_message("نوع الرسم البياني غير مدعوم", warning=True)
                
        except Exception as e:
            self.log_message(f"خطأ في إنشاء الرسم البياني: {str(e)}", error=True)
    
    def save_chart(self):
        """حفظ الرسم البياني كصورة"""
        if not hasattr(self, 'current_figure'):
            messagebox.showwarning("تحذير", "لا يوجد رسم بياني لحفظه")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("PDF Document", "*.pdf"),
                ("SVG Image", "*.svg")
            ]
        )
        
        if file_path:
            try:
                self.current_figure.savefig(file_path, dpi=300, bbox_inches='tight')
                self.log_message(f"تم حفظ الرسم البياني في: {file_path}")
                messagebox.showinfo("نجاح", "تم حفظ الرسم البياني بنجاح")
            except Exception as e:
                self.log_message(f"خطأ في حفظ الرسم: {str(e)}", error=True)
                messagebox.showerror("خطأ", f"حدث خطأ في الحفظ:\n{str(e)}")
    
    def map_column(self):
        """تعيين عمود محدد"""
        selection = self.column_listbox.curselection()
        if not selection:
            messagebox.showwarning("تحذير", "الرجاء اختيار عمود أولاً")
            return
        
        column = self.column_listbox.get(selection[0])
        mapping = self.mapping_combo.get()
        
        if not mapping:
            messagebox.showwarning("تحذير", "الرجاء اختيار نوع التعيين")
            return
        
        # تحديث النص
        self.mapping_text.insert(tk.END, f"{column} ← {mapping}\n")
        
        # حفظ التعيين
        self.column_mapper.add_mapping(column, mapping)
        
        self.log_message(f"تم تعيين العمود '{column}' كـ '{mapping}'")
    
    def auto_map(self):
        """التعيين التلقائي للأعمدة"""
        try:
            if self.dataframe is not None:
                mappings = self.column_mapper.auto_map(self.dataframe)
                
                # مسح النص الحالي
                self.mapping_text.delete(1.0, tk.END)
                
                # عرض التعيينات
                for col, mapping in mappings.items():
                    self.mapping_text.insert(tk.END, f"{col} ← {mapping}\n")
                
                self.log_message("تم التعيين التلقائي للأعمدة")
        except Exception as e:
            self.log_message(f"خطأ في التعيين التلقائي: {str(e)}", error=True)
    
    def clear_mapping(self):
        """مسح جميع التعيينات"""
        self.column_mapper.clear_mappings()
        self.mapping_text.delete(1.0, tk.END)
        self.log_message("تم مسح جميع التعيينات")
    
    def generate_report(self):
        """إنشاء التقرير"""
        if not self.analysis_results:
            messagebox.showwarning("تحذير", "الرجاء إجراء التحليل أولاً")
            return
        
        try:
            self.log_message("جاري إنشاء التقرير...")
            
            # إنشاء التقرير
            report = self.report_generator.generate(
                self.analysis_results,
                self.dataframe,
                self.store_type,
                language=self.current_language
            )
            
            # عرض التقرير
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(1.0, report)
            
            self.log_message("تم إنشاء التقرير بنجاح")
            
            # التبديل إلى تبويب التقرير
            self.notebook.select(4)  # تبويب التقرير
            
        except Exception as e:
            self.log_message(f"خطأ في إنشاء التقرير: {str(e)}", error=True)
            messagebox.showerror("خطأ", f"حدث خطأ في إنشاء التقرير:\n{str(e)}")
    
    def save_pdf_report(self):
        """حفظ التقرير كـ PDF"""
        self.save_report_as('pdf')
    
    def save_html_report(self):
        """حفظ التقرير كـ HTML"""
        self.save_report_as('html')
    
    def save_report_as(self, format_type):
        """حفظ التقرير بصيغة محددة"""
        if not self.analysis_results:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=[(f"{format_type.upper()} Files", f"*.{format_type}")]
        )
        
        if file_path:
            try:
                self.report_exporter.export_report(
                    self.analysis_results,
                    file_path,
                    format_type,
                    language=self.current_language
                )
                self.log_message(f"تم حفظ التقرير في: {file_path}")
                messagebox.showinfo("نجاح", "تم حفظ التقرير بنجاح")
            except Exception as e:
                self.log_message(f"خطأ في حفظ التقرير: {str(e)}", error=True)
                messagebox.showerror("خطأ", f"حدث خطأ في الحفظ:\n{str(e)}")
    
    def save_report(self):
        """حفظ التقرير"""
        self.save_report_as('pdf')
    
    def export_results(self):
        """تصدير النتائج"""
        if not self.analysis_results:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Files", "*.xlsx"),
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json")
            ]
        )
        
        if file_path:
            try:
                self.report_exporter.export_data(
                    self.analysis_results,
                    file_path
                )
                self.log_message(f"تم تصدير النتائج في: {file_path}")
                messagebox.showinfo("نجاح", "تم تصدير النتائج بنجاح")
            except Exception as e:
                self.log_message(f"خطأ في التصدير: {str(e)}", error=True)
                messagebox.showerror("خطأ", f"حدث خطأ في التصدير:\n{str(e)}")
    
    def open_recent_file(self):
        """فتح ملف حديث"""
        # هذه وظيفة بسيطة للتوضيح
        recent_dir = "data/uploaded"
        if os.path.exists(recent_dir):
            file_path = filedialog.askopenfilename(
                initialdir=recent_dir,
                title="اختر ملف حديث"
            )
            if file_path:
                self.process_file(file_path)
    
    def open_settings(self):
        """فتح نافذة الإعدادات"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("الإعدادات")
        settings_window.geometry("500x400")
        
        ttk.Label(settings_window, text="إعدادات التطبيق", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # إضافة عناصر الإعدادات هنا
        
        ttk.Button(settings_window, text="حفظ", 
                  command=settings_window.destroy).pack(pady=20)
    
    def toggle_language(self):
        """تبديل اللغة"""
        self.current_language = 'en' if self.current_language == 'ar' else 'ar'
        self.translator.set_language(self.current_language)
        
        # تحديث واجهة المستخدم (هذا يحتاج إلى مزيد من التطوير)
        self.log_message(f"تم تغيير اللغة إلى: {self.current_language}")
    
    def show_help(self):
        """عرض دليل المستخدم"""
        help_text = """
        دليل استخدام منصة تحليل بيانات التجارة الإلكترونية
        
        1. رفع الملف:
           - اضغط على "اختر ملف البيانات"
           - اختر ملف CSV أو Excel يحتوي على بيانات المبيعات
        
        2. التحليل:
           - بعد رفع الملف، اضغط على "بدء التحليل"
           - سيتم تحليل البيانات تلقائياً وعرض النتائج
        
        3. الرسوم البيانية:
           - انتقل إلى تبويب "الرسوم البيانية"
           - اختر نوع الرسم البياني ثم اضغط "عرض"
        
        4. التقرير:
           - انتقل إلى تبويب "التقرير"
           - اضغط على "إنشاء التقرير" لعرض التقرير
           - يمكنك حفظ التقرير بصيغ مختلفة
        
        ملاحظة: يجب أن يحتوي ملف البيانات على الأعمدة التالية:
        - تاريخ البيع (أو طلب)
        - كمية المنتج
        - سعر المنتج
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("دليل المستخدم")
        help_window.geometry("600x500")
        
        text_widget = scrolledtext.ScrolledText(help_window, width=70, height=30)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_about(self):
        """عرض معلومات عن البرنامج"""
        about_text = f"""
        منصة تحليل بيانات التجارة الإلكترونية
        
        الإصدار: {self.config.get('version', '1.0.0')}
        
        وصف:
        منصة متكاملة لتحليل بيانات التجارة الإلكترونية
        تدعم تحليل المبيعات وإعداد التقارير والرسوم البيانية
        
        المميزات:
        - تحليل بيانات المبيعات من مختلف المنصات
        - إنشاء تقارير مفصلة باللغتين العربية والإنجليزية
        - رسوم بيانية تفاعلية
        - تصدير النتائج بصيغ متعددة
        
        حقوق النشر © 2024. جميع الحقوق محفوظة.
        """
        
        messagebox.showinfo("عن البرنامج", about_text)
    
    def log_message(self, message, level="info", error=False, warning=False):
        """إضافة رسالة إلى سجل النظام"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if error:
            level = "ERROR"
            prefix = "[ERROR]"
        elif warning:
            level = "WARNING"
            prefix = "[WARNING]"
        else:
            level = "INFO"
            prefix = "[INFO]"
        
        log_entry = f"{timestamp} {prefix} {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # طباعة في الكونسول أيضاً
        print(log_entry.strip())
    
    def clear_log(self):
        """مسح سجل النظام"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("تم مسح سجل النظام")
    
    def save_log(self):
        """حفظ سجل النظام"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt")]
        )
        
        if file_path:
            try:
                log_content = self.log_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.log_message(f"تم حفظ السجل في: {file_path}")
                messagebox.showinfo("نجاح", "تم حفظ السجل بنجاح")
            except Exception as e:
                self.log_message(f"خطأ في حفظ السجل: {str(e)}", error=True)
                messagebox.showerror("خطأ", f"حدث خطأ في الحفظ:\n{str(e)}")
    
    def show_progress(self, show=True):
        """إظهار أو إخفاء شريط التقدم"""
        if show:
            self.progress_bar.start(10)
        else:
            self.progress_bar.stop()
    
    def set_icon(self):
        """تعيين أيقونة التطبيق"""
        try:
            icon_path = "static/images/logo.png"
            if os.path.exists(icon_path):
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, icon)
        except:
            pass  # تجاهل الخطأ إذا لم توجد الأيقونة


def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    try:
        root = tk.Tk()
        app = EcommerceAnalyticsApp(root)
        root.mainloop()
    except Exception as e:
        print(f"خطأ في تشغيل التطبيق: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
