"""
النظام الرئيسي لتحليل بيانات المتاجر الإلكترونية - Ecommerce Analytics Platform
واجهة Streamlit للتحليل الشامل للمتاجر الإلكترونية
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# إضافة مسارات الملفات للوحدات
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# استيراد جميع الوحدات
try:
    from modules.detector import StoreTypeDetector
    from modules.mapper import EcommerceColumnMapper
    from modules.analyzer import EcommerceAnalyzer, AnalysisConfig
    from modules.visualizer import EcommerceVisualizer, ChartConfig
    from modules.reporter import ReportGenerator
    
    from utils.validators import EcommerceValidators
    from utils.helpers import (
        format_currency, format_percentage, format_date,
        calculate_date_range, create_summary_stats,
        validate_file_upload, prepare_dataframe_display
    )
    from utils.exporters import EcommerceExporters
    
    from utils.translation import Translator, LanguageManager
    
except ImportError as e:
    st.error(f"خطأ في تحميل الوحدات: {e}")
    st.info("يرجى التأكد من وجود جميع الملفات في الهيكل المطلوب")

# ==================== تهيئة التطبيق ====================

class EcommerceAnalyticsApp:
    """التطبيق الرئيسي لتحليل المتاجر الإلكترونية"""
    
    def __init__(self):
        """تهيئة التطبيق"""
        self.setup_page_config()
        self.init_session_state()
        self.translator = Translator()
        
    def setup_page_config(self):
        """إعداد إعدادات صفحة Streamlit"""
        st.set_page_config(
            page_title="نظام تحليل المتاجر الإلكترونية",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={
                'Get Help': 'https://github.com/your-repo',
                'Report a bug': 'https://github.com/your-repo/issues',
                'About': 'نظام متكامل لتحليل بيانات المتاجر الإلكترونية'
            }
        )
        
        # تخصيص التنسيق
        st.markdown("""
        <style>
        .main-header {
            text-align: center;
            color: #2E4053;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .section-header {
            color: #3498DB;
            border-right: 5px solid #3498DB;
            padding-right: 15px;
            margin-top: 30px;
            margin-bottom: 20px;
        }
        .kpi-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            border-top: 4px solid #4CAF50;
        }
        .warning-box {
            background-color: #FFF3CD;
            border: 1px solid #FFEAA7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .success-box {
            background-color: #D1ECF1;
            border: 1px solid #BEE5EB;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def init_session_state(self):
        """تهيئة حالة الجلسة"""
        if 'dataframe' not in st.session_state:
            st.session_state.dataframe = None
        if 'store_type' not in st.session_state:
            st.session_state.store_type = None
        if 'column_mapping' not in st.session_state:
            st.session_state.column_mapping = {}
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'الرئيسية'
        if 'language' not in st.session_state:
            st.session_state.language = 'ar'
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        if 'export_dir' not in st.session_state:
            st.session_state.export_dir = 'exports'
    
    # ==================== واجهات الصفحات ====================
    
    def render_home_page(self):
        """عرض الصفحة الرئيسية"""
        st.markdown("""
        <div class="main-header">
            <h1>📊 نظام تحليل المتاجر الإلكترونية</h1>
            <p>أدوات متكاملة لتحليل بيانات متجرك الإلكتروني واتخاذ قرارات ذكية</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            ### 📁 رفع البيانات
            - دعم تنسيقات CSV، Excel، JSON
            - تحقق تلقائي من جودة البيانات
            - تنظيف وتجهيز البيانات
            """)
        
        with col2:
            st.success("""
            ### 🔍 التحليل الذكي
            - كشف تلقائي لنوع المتجر
            - تعيين ذكي للأعمدة
            - تحليل شامل للأداء
            """)
        
        with col3:
            st.warning("""
            ### 📈 التقارير والتصدير
            - تقارير تفاعلية
            - رسوم بيانية متعددة
            - تصدير بتنسيقات مختلفة
            """)
        
        st.markdown("---")
        
        # إحصائيات سريعة
        st.subheader("🚀 ابدأ التحليل الآن")
        uploaded_file = st.file_uploader(
            "اسحب وأفلت ملف البيانات الخاص بك هنا",
            type=['csv', 'xlsx', 'xls', 'json'],
            help="يمكنك رفع ملفات CSV، Excel، أو JSON"
        )
        
        if uploaded_file:
            validation_result = validate_file_upload(uploaded_file)
            
            if validation_result['valid']:
                st.session_state.dataframe = validation_result['dataframe']
                st.session_state.current_page = 'رفع البيانات'
                st.success("✅ تم تحميل الملف بنجاح! انتقل إلى صفحة 'رفع البيانات' للمتابعة.")
                st.rerun()
            else:
                st.error(f"❌ خطأ: {validation_result['error']}")
    
    def render_upload_page(self):
        """عرض صفحة رفع البيانات"""
        st.markdown('<h2 class="section-header">📁 رفع البيانات والتحقق</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.dataframe is None:
            st.warning("⚠️ لم يتم رفع أي بيانات بعد.")
            if st.button("العودة إلى الرئيسية"):
                st.session_state.current_page = 'الرئيسية'
                st.rerun()
            return
        
        # عرض البيانات
        st.subheader("معاينة البيانات")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            display_df = prepare_dataframe_display(st.session_state.dataframe)
            st.dataframe(display_df, use_container_width=True)
        
        with col2:
            st.metric("عدد السجلات", len(st.session_state.dataframe))
            st.metric("عدد الأعمدة", len(st.session_state.dataframe.columns))
            
            # كشف نوع المتجر
            if st.button("🔍 كشف نوع المتجر تلقائياً"):
                detector = StoreTypeDetector()
                store_type, confidence = detector.detect(st.session_state.dataframe)
                st.session_state.store_type = store_type
                
                st.success(f"✅ تم الكشف: {store_type}")
                st.info(f"درجة الثقة: {confidence.get(store_type, 0):.1f}%")
            
            if st.session_state.store_type:
                st.info(f"📌 نوع المتجر: {st.session_state.store_type}")
        
        # تحليل جودة البيانات
        st.subheader("📊 تقييم جودة البيانات")
        
        validator = EcommerceValidators()
        quality_score = validator.get_data_quality_score(st.session_state.dataframe)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("درجة الجودة", f"{quality_score['score']}/100")
        
        with col2:
            color_map = {'A': 'green', 'B': 'blue', 'C': 'yellow', 'D': 'orange', 'F': 'red'}
            st.markdown(f"<h3 style='color:{color_map.get(quality_score['grade'], 'black')}'>{quality_score['grade']}</h3>", 
                       unsafe_allow_html=True)
            st.caption("التقييم العام")
        
        with col3:
            st.progress(quality_score['score'] / 100)
        
        # عرض المشاكل
        if quality_score['details']['missing_percentage'] > 10:
            st.warning(f"⚠️ نسبة القيم المفقودة: {quality_score['details']['missing_percentage']:.1f}%")
        
        if quality_score['details']['duplicate_percentage'] > 5:
            st.warning(f"⚠️ نسبة التكرار: {quality_score['details']['duplicate_percentage']:.1f}%")
        
        # زر المتابعة
        if st.button("➡️ المتابعة إلى تعيين الأعمدة", type="primary"):
            st.session_state.current_page = 'تعيين الأعمدة'
            st.rerun()
    
    def render_mapping_page(self):
        """عرض صفحة تعيين الأعمدة"""
        st.markdown('<h2 class="section-header">🔗 تعيين أعمدة البيانات</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.dataframe is None:
            st.error("❌ لا توجد بيانات. يرجى الرجوع لرفع البيانات.")
            return
        
        # التعرف التلقائي
        mapper = EcommerceColumnMapper()
        auto_mapping = mapper.auto_detect(st.session_state.dataframe)
        
        st.subheader("التعرف التلقائي على الأعمدة")
        
        if not auto_mapping:
            st.warning("⚠️ لم يتمكن النظام من التعرف على الأعمدة تلقائياً.")
        else:
            st.success(f"✅ تم التعرف على {len(auto_mapping)} عمود")
        
        # تعيين يدوي
        st.subheader("تعيين الأعمدة يدوياً")
        
        required_fields = {
            'معرف الطلب': 'transaction_id',
            'تاريخ الطلب': 'order_date',
            'المبلغ الإجمالي': 'total_amount',
            'معرف المنتج': 'product_id',
            'الكمية': 'quantity'
        }
        
        st.session_state.column_mapping = {}
        
        for display_name, field_name in required_fields.items():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.write(f"**{display_name}:**")
            
            with col2:
                # اقتراح التلقائي إن وجد
                suggested = auto_mapping.get(field_name, '❌ غير متوفر')
                options = ['❌ غير متوفر'] + list(st.session_state.dataframe.columns)
                
                selected = st.selectbox(
                    f"اختر عمود {display_name}",
                    options,
                    index=options.index(suggested) if suggested in options else 0,
                    key=f"select_{field_name}",
                    label_visibility="collapsed"
                )
                
                if selected != '❌ غير متوفر':
                    st.session_state.column_mapping[field_name] = selected
        
        # التحقق من التعيين
        validation = mapper.validate_mapping(st.session_state.dataframe, st.session_state.column_mapping)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if validation['valid']:
                st.success("✅ تعيين الأعمدة صحيح")
            else:
                st.error("❌ تعيين الأعمدة غير مكتمل")
        
        with col2:
            if validation['valid']:
                if st.button("▶️ بدء التحليل", type="primary"):
                    st.session_state.current_page = 'التحليل والرؤى'
                    st.rerun()
            else:
                st.warning("⚠️ يرجى تعيين الحقول المطلوبة قبل المتابعة")
    
    def render_analysis_page(self):
        """عرض صفحة التحليل والرؤى"""
        st.markdown('<h2 class="section-header">📈 التحليل والرؤى</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.dataframe is None or not st.session_state.column_mapping:
            st.error("❌ البيانات غير مكتملة. يرجى الرجوع للخطوات السابقة.")
            return
        
        # إجراء التحليل
        if st.session_state.analysis_results is None:
            with st.spinner("🔄 جاري تحليل البيانات..."):
                config = AnalysisConfig(
                    store_type=st.session_state.store_type or 'general',
                    currency='SAR',
                    language=st.session_state.language
                )
                
                analyzer = EcommerceAnalyzer(config)
                st.session_state.analysis_results = analyzer.analyze(
                    st.session_state.dataframe,
                    st.session_state.column_mapping
                )
        
        results = st.session_state.analysis_results
        
        # لوحة مؤشرات الأداء الرئيسية
        st.subheader("📊 مؤشرات الأداء الرئيسية")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            revenue = results['sales_performance'].get('total_revenue', 0)
            st.metric("الإيرادات", format_currency(revenue))
        
        with col2:
            aov = results['sales_performance'].get('average_order_value', 0)
            st.metric("متوسط قيمة الطلب", format_currency(aov))
        
        with col3:
            customers = results['customer_analysis'].get('total_customers', 0)
            st.metric("عدد العملاء", f"{customers:,}")
        
        with col4:
            repeat_rate = results['customer_analysis'].get('repeat_rate', 0)
            st.metric("معدل التكرار", format_percentage(repeat_rate))
        
        # الرسوم البيانية
        st.subheader("📊 التصورات البيانية")
        
        # تكوين الرسوم البيانية
        chart_config = ChartConfig(
            theme='plotly_white',
            color_scale='Viridis',
            width=800,
            height=400,
            language=st.session_state.language
        )
        
        visualizer = EcommerceVisualizer(chart_config)
        
        # مخطط المبيعات
        if 'order_date' in st.session_state.column_mapping and 'total_amount' in st.session_state.column_mapping:
            sales_fig = visualizer.create_sales_trend_chart(
                st.session_state.dataframe,
                st.session_state.column_mapping['order_date'],
                st.session_state.column_mapping['total_amount']
            )
            st.plotly_chart(sales_fig, use_container_width=True)
        
        # مخطط أفضل المنتجات
        if 'product_name' in st.session_state.column_mapping and 'quantity' in st.session_state.column_mapping:
            products_fig = visualizer.create_top_products_chart(
                st.session_state.dataframe,
                st.session_state.column_mapping['product_name'],
                st.session_state.column_mapping['quantity']
            )
            st.plotly_chart(products_fig, use_container_width=True)
        
        # تحليل العملاء
        st.subheader("👥 تحليل العملاء")
        
        customer_segments = results['customer_analysis'].get('customer_segments', {})
        
        if customer_segments:
            segments_fig = visualizer.create_customer_segments_chart(customer_segments)
            st.plotly_chart(segments_fig, use_container_width=True)
        
        # مقارنة مع معايير الصناعة
        st.subheader("📊 مقارنة مع معايير الصناعة")
        
        store_kpis = {
            'aov': aov,
            'conversion_rate': results.get('benchmarks', {}).get('conversion_rate', 0),
            'repeat_rate': repeat_rate
        }
        
        benchmarks_fig = visualizer.create_benchmark_comparison_chart(
            store_kpis,
            results.get('benchmarks', {})
        )
        
        if benchmarks_fig:
            st.plotly_chart(benchmarks_fig, use_container_width=True)
        
        # زر التقرير
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("📄 إنشاء تقرير مفصل", type="primary"):
                st.session_state.current_page = 'التقارير'
                st.rerun()
    
    def render_reports_page(self):
        """عرض صفحة التقارير"""
        st.markdown('<h2 class="section-header">📄 التقارير والتصدير</h2>', 
                   unsafe_allow_html=True)
        
        if st.session_state.analysis_results is None:
            st.error("❌ لا توجد نتائج تحليل. يرجى الرجوع لصفحة التحليل.")
            return
        
        results = st.session_state.analysis_results
        
        # إنشاء التقرير
        reporter = ReportGenerator(language=st.session_state.language)
        report_text = reporter.generate_report(
            results,
            st.session_state.store_type or 'general'
        )
        
        # معاينة التقرير
        st.subheader("معاينة التقرير")
        
        with st.expander("عرض التقرير الكامل", expanded=True):
            st.text_area("التقرير", report_text, height=400)
        
        # خيارات التصدير
        st.subheader("خيارات التصدير")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            export_format = st.selectbox(
                "تنسيق التقرير",
                ['PDF', 'HTML', 'Word', 'Excel', 'JSON']
            )
        
        with col2:
            include_charts = st.checkbox("تضمين الرسوم البيانية", value=True)
        
        with col3:
            email_report = st.checkbox("إرسال بالإيميل")
        
        # إنشاء التصدير
        exporter = EcommerceExporters(st.session_state.export_dir)
        
        if st.button("🚀 إنشاء وتحميل التقرير", type="primary"):
            with st.spinner("🔄 جاري إنشاء التقرير..."):
                # تصدير التقرير
                report_export = exporter.export_report(
                    report_text,
                    'ecommerce_report',
                    export_format.lower(),
                    'تقرير تحليل المتجر الإلكتروني'
                )
                
                if report_export['success']:
                    st.success("✅ تم إنشاء التقرير بنجاح")
                    
                    # عرض رابط التنزيل
                    with open(report_export['file_path'], 'rb') as f:
                        report_bytes = f.read()
                    
                    st.download_button(
                        label=f"📥 تحميل التقرير ({export_format})",
                        data=report_bytes,
                        file_name=f"ecommerce_report_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
                        mime=f"application/{export_format.lower()}"
                    )
        
        # تصدير البيانات الخام
        st.subheader("تصدير البيانات")
        
        if st.button("📊 تصدير البيانات الخام"):
            data_export = exporter.export_dataframe(
                st.session_state.dataframe,
                'ecommerce_data',
                'excel',
                include_index=False
            )
            
            if data_export['success']:
                with open(data_export['file_path'], 'rb') as f:
                    data_bytes = f.read()
                
                st.download_button(
                    label="📥 تحميل البيانات",
                    data=data_bytes,
                    file_name=f"ecommerce_data_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    def render_settings_page(self):
        """عرض صفحة الإعدادات"""
        st.markdown('<h2 class="section-header">⚙️ الإعدادات</h2>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # إعدادات اللغة
            language = st.selectbox(
                "اللغة",
                ['ar', 'en'],
                format_func=lambda x: 'العربية 🇸🇦' if x == 'ar' else 'English 🇺🇸',
                index=0 if st.session_state.language == 'ar' else 1
            )
            
            if language != st.session_state.language:
                st.session_state.language = language
                st.success(f"✅ تم تغيير اللغة إلى {'العربية' if language == 'ar' else 'الإنجليزية'}")
        
        with col2:
            # إعدادات المظهر
            theme = st.selectbox(
                "المظهر",
                ['light', 'dark'],
                format_func=lambda x: 'فاتح ☀️' if x == 'light' else 'داكن 🌙',
                index=0 if st.session_state.theme == 'light' else 1
            )
            
            if theme != st.session_state.theme:
                st.session_state.theme = theme
                st.success(f"✅ تم تغيير المظهر إلى {'الوضع الفاتح' if theme == 'light' else 'الوضع الداكن'}")
        
        # إعدادات التصدير
        st.subheader("إعدادات التصدير")
        
        export_dir = st.text_input(
            "مسار حفظ الملفات",
            value=st.session_state.export_dir,
            help="المجلد الذي سيتم حفظ الملفات المصدرة فيه"
        )
        
        if export_dir != st.session_state.export_dir:
            st.session_state.export_dir = export_dir
            st.success(f"✅ تم تغيير مسار الحفظ إلى {export_dir}")
        
        # تنظيف الملفات القديمة
        st.subheader("الصيانة")
        
        if st.button("🧹 تنظيف الملفات القديمة", type="secondary"):
            exporter = EcommerceExporters(st.session_state.export_dir)
            deleted_count = exporter.cleanup_old_exports(days_old=7)
            st.info(f"🗑️ تم حذف {deleted_count} ملف قديم")
        
        # إحصائيات النظام
        st.subheader("إحصائيات النظام")
        
        exporter = EcommerceExporters(st.session_state.export_dir)
        stats = exporter.get_export_stats()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("إجمالي الملفات", stats['total_files'])
        
        with col2:
            st.metric("الحجم الإجمالي", f"{stats['total_size_mb']:.1f} MB")
        
        with col3:
            st.metric("أنواع الملفات", len(stats['file_types']))
    
    def render_sidebar(self):
        """عرض الشريط الجانبي"""
        with st.sidebar:
            st.image("https://via.placeholder.com/150x50/4CAF50/FFFFFF?text=Ecommerce+Analytics", 
                    use_container_width=True)
            
            st.markdown("---")
            
            # قائمة التنقل
            pages = {
                "🏠 الرئيسية": "الرئيسية",
                "📁 رفع البيانات": "رفع البيانات",
                "🔗 تعيين الأعمدة": "تعيين الأعمدة",
                "📈 التحليل والرؤى": "التحليل والرؤى",
                "📄 التقارير": "التقارير",
                "⚙️ الإعدادات": "الإعدادات"
            }
            
            selected_page = st.selectbox(
                "التنقل",
                list(pages.keys()),
                index=list(pages.keys()).index(
                    next((k for k, v in pages.items() if v == st.session_state.current_page), "🏠 الرئيسية")
                ),
                label_visibility="collapsed"
            )
            
            if pages[selected_page] != st.session_state.current_page:
                st.session_state.current_page = pages[selected_page]
                st.rerun()
            
            st.markdown("---")
            
            # معلومات النظام
            st.markdown("### معلومات النظام")
            
            if st.session_state.dataframe is not None:
                st.info(f"📊 **البيانات:** {len(st.session_state.dataframe):,} سجل")
            
            if st.session_state.store_type:
                st.info(f"🏪 **نوع المتجر:** {st.session_state.store_type}")
            
            if st.session_state.analysis_results:
                st.success("✅ **التحليل:** مكتمل")
            
            st.markdown("---")
            
            # مسح الجلسة
            if st.button("🔄 مسح الجلسة", type="secondary", use_container_width=True):
                self.init_session_state()
                st.rerun()
            
            # معلومات إضافية
            st.caption("""
            ---
            **الإصدار:** 2.0.0  
            **آخر تحديث:** 2024  
            [الدعم الفني](mailto:support@ecommerce-analytics.com)
            """)
    
    def run(self):
        """تشغيل التطبيق"""
        # عرض الشريط الجانبي
        self.render_sidebar()
        
        # عرض الصفحة المحددة
        page_handlers = {
            'الرئيسية': self.render_home_page,
            'رفع البيانات': self.render_upload_page,
            'تعيين الأعمدة': self.render_mapping_page,
            'التحليل والرؤى': self.render_analysis_page,
            'التقارير': self.render_reports_page,
            'الإعدادات': self.render_settings_page
        }
        
        handler = page_handlers.get(st.session_state.current_page, self.render_home_page)
        handler()

# ==================== تشغيل التطبيق ====================

if __name__ == "__main__":
    try:
        app = EcommerceAnalyticsApp()
        app.run()
    except Exception as e:
        st.error(f"حدث خطأ في النظام: {str(e)}")
        st.info("يرجى تحديث الصفحة والمحاولة مرة أخرى")