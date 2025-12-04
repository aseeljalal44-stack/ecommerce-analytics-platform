# ecom_analytics.py - الملف الرئيسي لتطبيق تحليل بيانات التجارة الإلكترونية
import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
import sys
import traceback

# إضافة مسارات النظام للوحدات الداخلية
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.detector import detect_store_type, SUPPORTED_STORES
from modules.mapper import ColumnMapper
from modules.analyzer import EcommerceAnalyzer
from modules.visualizer import DataVisualizer
from modules.reporter import ReportGenerator
from utils.translation import TranslationSystem
from utils.helpers import (
    load_config, save_config, create_directory, 
    validate_file_type, clean_dataframe, generate_unique_id
)
from utils.validators import validate_uploaded_file
from utils.exporters import export_to_excel, export_to_pdf

# تهيئة التطبيق
st.set_page_config(
    page_title="نظام تحليل بيانات التجارة الإلكترونية",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تهيئة نظام الترجمة
translator = TranslationSystem()
config = load_config()

class EcommerceAnalyticsApp:
    def __init__(self):
        """تهيئة تطبيق تحليل البيانات"""
        self.initialize_session_state()
        self.setup_ui()
        
    def initialize_session_state(self):
        """تهيئة حالة الجلسة"""
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'df' not in st.session_state:
            st.session_state.df = None
        if 'store_type' not in st.session_state:
            st.session_state.store_type = None
        if 'column_mapping' not in st.session_state:
            st.session_state.column_mapping = {}
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'language' not in st.session_state:
            st.session_state.language = config.get('default_language', 'ar')
        if 'user_id' not in st.session_state:
            st.session_state.user_id = generate_unique_id()
            
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # شريط جانبي للتنقل والإعدادات
        with st.sidebar:
            self.render_sidebar()
            
        # المنطقة الرئيسية
        self.render_main_area()
        
    def render_sidebar(self):
        """عرض الشريط الجانبي"""
        st.title("⚙️ الإعدادات")
        
        # اختيار اللغة
        language_options = {
            'ar': 'العربية',
            'en': 'English'
        }
        selected_lang = st.selectbox(
            "🌍 اللغة / Language",
            options=list(language_options.keys()),
            format_func=lambda x: language_options[x],
            index=list(language_options.keys()).index(st.session_state.language)
        )
        
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.rerun()
            
        # معلومات حول البيانات المرفوعة
        if st.session_state.data_loaded:
            st.success("✅ بيانات مرفوعة")
            if st.session_state.store_type:
                st.info(f"نوع المتجر: {st.session_state.store_type}")
            st.metric("عدد الصفوف", len(st.session_state.df))
            st.metric("عدد الأعمدة", len(st.session_state.df.columns))
            
        # قسم المساعدة
        st.divider()
        with st.expander("❓ المساعدة"):
            st.markdown("""
            ### كيفية الاستخدام:
            1. قم برفع ملف Excel أو CSV
            2. اختر نوع المتجر أو اكتشفه تلقائياً
            3. قم بتعيين الأعمدة يدوياً إذا لزم الأمر
            4. استعرض التحليلات والرسوم البيانية
            5. قم بإنشاء وتصدير التقارير
            """)
            
        # معلومات الإصدار
        st.caption(f"الإصدار: {config.get('version', '1.0.0')}")
        
    def render_main_area(self):
        """عرض المنطقة الرئيسية"""
        # شريط العنوان
        title = translator.translate("ecommerce_data_analytics", st.session_state.language)
        st.title(f"📊 {title}")
        
        # علامات التبويب الرئيسية
        tabs = st.tabs([
            translator.translate("upload_data", st.session_state.language),
            translator.translate("column_mapping", st.session_state.language),
            translator.translate("data_analysis", st.session_state.language),
            translator.translate("visualizations", st.session_state.language),
            translator.translate("reports", st.session_state.language)
        ])
        
        # علامة تبويب رفع البيانات
        with tabs[0]:
            self.render_upload_tab()
            
        # علامة تبويب تعيين الأعمدة
        with tabs[1]:
            self.render_mapping_tab()
            
        # علامة تبويب التحليل
        with tabs[2]:
            self.render_analysis_tab()
            
        # علامة تبويب الرسوم البيانية
        with tabs[3]:
            self.render_visualization_tab()
            
        # علامة تبويب التقارير
        with tabs[4]:
            self.render_reports_tab()
            
    def render_upload_tab(self):
        """عرض علامة تبويب رفع البيانات"""
        st.header(translator.translate("upload_data_section", st.session_state.language))
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # رفع الملف
            uploaded_file = st.file_uploader(
                translator.translate("choose_file", st.session_state.language),
                type=['csv', 'xlsx', 'xls'],
                help=translator.translate("upload_help", st.session_state.language)
            )
            
            if uploaded_file is not None:
                try:
                    # التحقق من صحة الملف
                    validation_result = validate_uploaded_file(uploaded_file)
                    
                    if not validation_result['valid']:
                        st.error(f"❌ {validation_result['message']}")
                        return
                        
                    # قراءة البيانات
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                        
                    # تنظيف البيانات
                    df = clean_dataframe(df)
                    
                    # حفظ في حالة الجلسة
                    st.session_state.df = df
                    st.session_state.data_loaded = True
                    st.session_state.original_filename = uploaded_file.name
                    
                    # كشف نوع المتجر
                    store_type = detect_store_type(df)
                    st.session_state.store_type = store_type
                    
                    st.success(f"✅ {translator.translate('file_uploaded_success', st.session_state.language)}")
                    st.success(f"🔍 {translator.translate('store_detected', st.session_state.language)}: {store_type}")
                    
                except Exception as e:
                    st.error(f"❌ {translator.translate('upload_error', st.session_state.language)}: {str(e)}")
                    
        with col2:
            # عرض أنواع المتاجر المدعومة
            if st.button(translator.translate("view_supported_stores", st.session_state.language)):
                with st.expander(translator.translate("supported_stores", st.session_state.language)):
                    for store, desc in SUPPORTED_STORES.items():
                        st.write(f"**{store}**: {desc}")
                        
        # عرض معاينة البيانات
        if st.session_state.data_loaded:
            st.subheader(translator.translate("data_preview", st.session_state.language))
            st.dataframe(st.session_state.df.head(10), use_container_width=True)
            
            # إحصائيات سريعة
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(translator.translate("total_rows", st.session_state.language), len(st.session_state.df))
            with col2:
                st.metric(translator.translate("total_columns", st.session_state.language), len(st.session_state.df.columns))
            with col3:
                st.metric(translator.translate("data_size", st.session_state.language), 
                         f"{st.session_state.df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
                
    def render_mapping_tab(self):
        """عرض علامة تبويب تعيين الأعمدة"""
        st.header(translator.translate("column_mapping_section", st.session_state.language))
        
        if not st.session_state.data_loaded:
            st.warning(translator.translate("upload_data_first", st.session_state.language))
            return
            
        # إنشاء كائن تعيين الأعمدة
        mapper = ColumnMapper(st.session_state.df, st.session_state.store_type)
        
        # تعيين تلقائي
        if st.button(translator.translate("auto_map_columns", st.session_state.language)):
            auto_mapping = mapper.auto_map_columns()
            st.session_state.column_mapping = auto_mapping
            st.success(translator.translate("auto_mapping_complete", st.session_state.language))
            
        # تعيين يدوي
        st.subheader(translator.translate("manual_mapping", st.session_state.language))
        
        # الحصول على الأعمدة المطلوبة للمتجر المحدد
        required_columns = mapper.get_required_columns()
        
        # إنشاء واجهة تعيين يدوية
        col_mapping_ui = {}
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{translator.translate('required_columns', st.session_state.language)}:**")
            for col_type in required_columns:
                st.write(f"- {col_type}: {required_columns[col_type]}")
                
        with col2:
            st.write(f"**{translator.translate('available_columns', st.session_state.language)}:**")
            available_cols = list(st.session_state.df.columns)
            st.write(", ".join(available_cols))
            
        # واجهة التعيين
        st.subheader(translator.translate("map_columns", st.session_state.language))
        
        for col_type, description in required_columns.items():
            current_mapping = st.session_state.column_mapping.get(col_type, '')
            selected_col = st.selectbox(
                f"{description} ({col_type})",
                options=[''] + available_cols,
                index=0 if current_mapping not in available_cols else available_cols.index(current_mapping) + 1,
                key=f"map_{col_type}"
            )
            if selected_col:
                col_mapping_ui[col_type] = selected_col
                
        # زر حفظ التعيين
        if st.button(translator.translate("save_mapping", st.session_state.language)):
            if col_mapping_ui:
                st.session_state.column_mapping = col_mapping_ui
                st.success(translator.translate("mapping_saved", st.session_state.language))
                
        # عرض التعيين الحالي
        if st.session_state.column_mapping:
            st.subheader(translator.translate("current_mapping", st.session_state.language))
            mapping_df = pd.DataFrame(
                list(st.session_state.column_mapping.items()),
                columns=[translator.translate("column_type", st.session_state.language),
                        translator.translate("mapped_column", st.session_state.language)]
            )
            st.dataframe(mapping_df, use_container_width=True)
            
    def render_analysis_tab(self):
        """عرض علامة تبويب التحليل"""
        st.header(translator.translate("data_analysis_section", st.session_state.language))
        
        if not st.session_state.data_loaded:
            st.warning(translator.translate("upload_data_first", st.session_state.language))
            return
            
        if not st.session_state.column_mapping:
            st.warning(translator.translate("map_columns_first", st.session_state.language))
            return
            
        # تحليل البيانات
        if st.button(translator.translate("run_analysis", st.session_state.language), type="primary"):
            with st.spinner(translator.translate("analyzing_data", st.session_state.language)):
                try:
                    analyzer = EcommerceAnalyzer(
                        st.session_state.df,
                        st.session_state.column_mapping,
                        st.session_state.store_type
                    )
                    
                    # إجراء التحليلات
                    analysis_results = analyzer.perform_complete_analysis()
                    st.session_state.analysis_results = analysis_results
                    
                    st.success(translator.translate("analysis_complete", st.session_state.language))
                    
                except Exception as e:
                    st.error(f"❌ {translator.translate('analysis_error', st.session_state.language)}: {str(e)}")
                    
        # عرض نتائج التحليل
        if st.session_state.analysis_results:
            results = st.session_state.analysis_results
            
            # عرض ملخص النتائج
            st.subheader(translator.translate("analysis_summary", st.session_state.language))
            
            # مؤشرات الأداء الرئيسية
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    translator.translate("total_sales", st.session_state.language),
                    f"{results.get('total_sales', 0):,.0f} {results.get('currency', '')}"
                )
                
            with col2:
                st.metric(
                    translator.translate("total_orders", st.session_state.language),
                    f"{results.get('total_orders', 0):,}"
                )
                
            with col3:
                st.metric(
                    translator.translate("total_customers", st.session_state.language),
                    f"{results.get('total_customers', 0):,}"
                )
                
            with col4:
                st.metric(
                    translator.translate("avg_order_value", st.session_state.language),
                    f"{results.get('avg_order_value', 0):,.0f} {results.get('currency', '')}"
                )
                
            # تحليلات تفصيلية
            st.subheader(translator.translate("detailed_analysis", st.session_state.language))
            
            tabs_analysis = st.tabs([
                translator.translate("sales_trends", st.session_state.language),
                translator.translate("product_analysis", st.session_state.language),
                translator.translate("customer_analysis", st.session_state.language),
                translator.translate("geographic_analysis", st.session_state.language)
            ])
            
            with tabs_analysis[0]:
                if 'sales_trends' in results:
                    trend_data = results['sales_trends']
                    if isinstance(trend_data, pd.DataFrame) and not trend_data.empty:
                        st.dataframe(trend_data, use_container_width=True)
                        
            with tabs_analysis[1]:
                if 'top_products' in results:
                    top_products = results['top_products']
                    if isinstance(top_products, pd.DataFrame) and not top_products.empty:
                        st.dataframe(top_products.head(10), use_container_width=True)
                        
            with tabs_analysis[2]:
                if 'customer_segments' in results:
                    segments = results['customer_segments']
                    if isinstance(segments, pd.DataFrame) and not segments.empty:
                        st.dataframe(segments, use_container_width=True)
                        
            with tabs_analysis[3]:
                if 'geographic_distribution' in results:
                    geo_data = results['geographic_distribution']
                    if isinstance(geo_data, pd.DataFrame) and not geo_data.empty:
                        st.dataframe(geo_data, use_container_width=True)
                        
    def render_visualization_tab(self):
        """عرض علامة تبويب الرسوم البيانية"""
        st.header(translator.translate("data_visualization", st.session_state.language))
        
        if not st.session_state.data_loaded or not st.session_state.analysis_results:
            st.warning(translator.translate("run_analysis_first", st.session_state.language))
            return
            
        visualizer = DataVisualizer(st.session_state.analysis_results)
        
        # اختيار نوع الرسم البياني
        chart_type = st.selectbox(
            translator.translate("select_chart_type", st.session_state.language),
            options=[
                'sales_trend',
                'top_products',
                'sales_by_category',
                'customer_segments',
                'geographic_distribution',
                'payment_methods',
                'monthly_comparison'
            ],
            format_func=lambda x: translator.translate(x, st.session_state.language)
        )
        
        # توليد الرسم البياني المحدد
        fig = visualizer.generate_chart(chart_type, language=st.session_state.language)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
            
            # خيارات التصدير
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(translator.translate("export_chart_image", st.session_state.language)):
                    # تصدير كصورة
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"chart_{chart_type}_{timestamp}.png"
                    fig.write_image(filename)
                    st.success(f"✅ {translator.translate('chart_exported', st.session_state.language)}: {filename}")
                    
            with col2:
                if st.button(translator.translate("export_chart_data", st.session_state.language)):
                    # تصدير البيانات
                    chart_data = visualizer.get_chart_data(chart_type)
                    if chart_data is not None:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        csv_filename = f"chart_data_{chart_type}_{timestamp}.csv"
                        if isinstance(chart_data, pd.DataFrame):
                            chart_data.to_csv(csv_filename, index=False)
                            st.success(f"✅ {translator.translate('data_exported', st.session_state.language)}: {csv_filename}")
                            
        # توليد جميع الرسوم البيانية
        st.subheader(translator.translate("all_charts", st.session_state.language))
        
        if st.button(translator.translate("generate_all_charts", st.session_state.language)):
            all_figs = visualizer.generate_all_charts(language=st.session_state.language)
            
            for chart_name, fig in all_figs.items():
                if fig:
                    st.subheader(translator.translate(chart_name, st.session_state.language))
                    st.plotly_chart(fig, use_container_width=True)
                    st.divider()
                    
    def render_reports_tab(self):
        """عرض علامة تبويب التقارير"""
        st.header(translator.translate("reports_generation", st.session_state.language))
        
        if not st.session_state.data_loaded or not st.session_state.analysis_results:
            st.warning(translator.translate("run_analysis_first", st.session_state.language))
            return
            
        # إنشاء كائن التقارير
        report_gen = ReportGenerator(
            st.session_state.analysis_results,
            st.session_state.store_type,
            st.session_state.language
        )
        
        # خيارات التقرير
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox(
                translator.translate("select_report_type", st.session_state.language),
                options=['executive', 'detailed', 'custom'],
                format_func=lambda x: translator.translate(f'report_type_{x}', st.session_state.language)
            )
            
        with col2:
            output_format = st.selectbox(
                translator.translate("select_output_format", st.session_state.language),
                options=['html', 'pdf', 'excel'],
                format_func=lambda x: translator.translate(f'format_{x}', st.session_state.language)
            )
            
        # خيارات مخصصة
        if report_type == 'custom':
            st.subheader(translator.translate("custom_report_options", st.session_state.language))
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_sections = st.multiselect(
                    translator.translate("include_sections", st.session_state.language),
                    options=['summary', 'sales', 'products', 'customers', 'geography', 'recommendations'],
                    default=['summary', 'sales', 'products']
                )
                
            with col2:
                include_charts = st.checkbox(translator.translate("include_charts", st.session_state.language), value=True)
                include_data_tables = st.checkbox(translator.translate("include_data_tables", st.session_state.language), value=True)
                
        # إنشاء التقرير
        if st.button(translator.translate("generate_report", st.session_state.language), type="primary"):
            with st.spinner(translator.translate("generating_report", st.session_state.language)):
                try:
                    if report_type == 'custom':
                        report_content = report_gen.generate_custom_report(
                            sections=include_sections,
                            include_charts=include_charts,
                            include_tables=include_data_tables
                        )
                    else:
                        report_content = report_gen.generate_report(report_type)
                        
                    # حفظ التقرير
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_filename = f"ecom_report_{report_type}_{timestamp}"
                    
                    if output_format == 'html':
                        filename = f"{report_filename}.html"
                        report_gen.save_report(report_content, filename)
                        
                    elif output_format == 'pdf':
                        filename = f"{report_filename}.pdf"
                        # سيتم تنفيذ تصدير PDF هنا
                        st.info("⚠️ ميزة تصدير PDF تحت التطوير")
                        
                    elif output_format == 'excel':
                        filename = f"{report_filename}.xlsx"
                        export_to_excel(st.session_state.analysis_results, filename)
                        
                    st.success(f"✅ {translator.translate('report_generated', st.session_state.language)}: {filename}")
                    
                    # عرض معاينة التقرير
                    with st.expander(translator.translate("report_preview", st.session_state.language)):
                        if output_format == 'html':
                            st.components.v1.html(report_content, height=600, scrolling=True)
                        elif output_format == 'excel':
                            st.write(translator.translate("excel_report_created", st.session_state.language))
                            
                except Exception as e:
                    st.error(f"❌ {translator.translate('report_error', st.session_state.language)}: {str(e)}")
                    st.error(traceback.format_exc())
                    
        # قوالب التقارير السريعة
        st.subheader(translator.translate("quick_report_templates", st.session_state.language))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(translator.translate("sales_summary", st.session_state.language)):
                quick_report = report_gen.generate_sales_summary()
                st.download_button(
                    label=translator.translate("download_html", st.session_state.language),
                    data=quick_report,
                    file_name=f"sales_summary_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                
        with col2:
            if st.button(translator.translate("product_report", st.session_state.language)):
                quick_report = report_gen.generate_product_report()
                st.download_button(
                    label=translator.translate("download_html", st.session_state.language),
                    data=quick_report,
                    file_name=f"product_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                
        with col3:
            if st.button(translator.translate("customer_report", st.session_state.language)):
                quick_report = report_gen.generate_customer_report()
                st.download_button(
                    label=translator.translate("download_html", st.session_state.language),
                    data=quick_report,
                    file_name=f"customer_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    try:
        # إنشاء مجلدات التخزين إذا لم تكن موجودة
        create_directory('data/uploaded')
        create_directory('data/processed')
        create_directory('reports')
        create_directory('static')
        
        # تشغيل التطبيق
        app = EcommerceAnalyticsApp()
        
        # تذييل الصفحة
        st.divider()
        st.caption(translator.translate("footer_note", st.session_state.language))
        
    except Exception as e:
        st.error(f"❌ {translator.translate('app_error', st.session_state.language)}: {str(e)}")
        st.error(traceback.format_exc())

if __name__ == "__main__":
    main()