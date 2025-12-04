# ecom_analytics.py
import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# اجعل modules و utils متاحة
sys.path.append(str(Path(__file__).parent))

# استيراد الوحدات المعاد بناؤها
from modules.detector import StoreTypeDetector
from modules.mapper import EcommerceColumnMapper, ColumnMapper  # ColumnMapper كـ alias للتوافق
from modules.analyzer import EcommerceAnalyzer, AnalysisConfig
from modules.visualizer import EcommerceVisualizer, ChartConfig
from modules.reporter import ReportGenerator
from utils.validators import EcommerceValidators
from utils.helpers import validate_file_upload, prepare_dataframe_display
from utils.exporters import EcommerceExporters
from utils.translation import Translator, LanguageManager

# ===== تهيئة الصفحة =====
st.set_page_config(page_title="نظام تحليل المتاجر الإلكترونية", layout="wide", page_icon="📊")

# ===== واجهة بسيطة للرفع والتحليل =====
def sidebar_controls(trans):
    st.sidebar.header(trans("Controls", "التحكم"))
    language = st.sidebar.selectbox(trans("Language", "اللغة"), options=["ar", "en"], index=0 if st.session_state.get('language','ar')=='ar' else 1)
    st.session_state.language = language
    st.sidebar.markdown("---")
    upload_help = st.sidebar.info(trans(
        "Upload a CSV/Excel file with orders. Columns like order_id/order_date/total_amount help automatic mapping.",
        "ارفع ملف CSV أو Excel يحوي بيانات الطلبات. أعمدة مثل order_id/order_date/total_amount تسهل التعرف التلقائي."
    ))
    return language

def main():
    # init session
    if 'language' not in st.session_state:
        st.session_state.language = 'ar'
    language = sidebar_controls(Translator().translate)
    trans = Translator().translate

    st.title(trans("E-commerce Analytics", "نظام تحليل المتاجر الإلكترونية"))

    uploaded_file = st.file_uploader(trans("Upload CSV / Excel", "ارفع CSV أو Excel"), type=['csv','xlsx','xls','json'])
    if uploaded_file is not None:
        # تحقق من الملف
        check = EcommerceValidators.validate_file_upload(uploaded_file)
        if not check['valid']:
            st.error(check['message'])
            return

        # قراءة الملف إلى dataframe
        try:
            if check['file_type'] == 'csv':
                df = pd.read_csv(uploaded_file, encoding=check.get('encoding','utf-8'), on_bad_lines='skip')
            elif check['file_type'] == 'excel':
                df = pd.read_excel(uploaded_file)
            elif check['file_type'] == 'json':
                df = pd.read_json(uploaded_file)
            else:
                st.error(trans("Unsupported file type", "نوع الملف غير مدعوم"))
                return
        except Exception as e:
            st.error(trans("Error reading file:", "خطأ في قراءة الملف:") + f" {e}")
            return

        st.success(trans("File loaded successfully", "تم تحميل الملف"))
        st.subheader(trans("Preview", "معاينة"))
        st.dataframe(prepare_dataframe_display(df))

        # كشف نوع المتجر
        detector = StoreTypeDetector()
        store_type, scores = detector.detect(df)
        st.info(trans("Detected store type:", "نوع المتجر المكتشف:") + f" {store_type}  (scores: {scores})")

        # تعيين أعمدة تلقائي
        mapper = EcommerceColumnMapper()
        mapping = mapper.auto_map(df)
        st.write(trans("Auto column mapping", "تعيين الأعمدة تلقائياً"))
        st.json(mapping)

        # تحليل
        analyzer = EcommerceAnalyzer(config=AnalysisConfig(store_type=store_type, language=language))
        results = analyzer.analyze(df, mapping)
        st.subheader(trans("Analysis Results", "نتائج التحليل"))
        st.json(results, expanded=False)

        # تصورات أساسية
        visualizer = EcommerceVisualizer(ChartConfig(language=language))
        exporters = EcommerceExporters(output_dir="exports")
        reporter = ReportGenerator(language=language)

        # KPIs
        kpi = {
            'total_revenue': results['sales_performance'].get('total_revenue', 0),
            'average_order_value': results['sales_performance'].get('average_order_value', 0),
            'total_customers': results['store_profile'].get('unique_customers', 0),
            'total_products': results['store_profile'].get('unique_products', 0)
        }
        fig_kpi = visualizer.create_kpi_dashboard(kpi)
        st.plotly_chart(fig_kpi, use_container_width=True)

        # مبيان اتجاه المبيعات
        if mapping.get('order_date') and mapping.get('total_amount'):
            fig_trend = visualizer.create_sales_trend_chart(df, mapping['order_date'], mapping['total_amount'])
            st.plotly_chart(fig_trend, use_container_width=True)

        # تصدير تقرير (نصّي) وملف Excel
        report_text = reporter.generate_report(results, store_type)
        st.download_button("Download report (txt)", data=report_text, file_name="report.txt")
        export_info = exporters.export_dataframe(df, filename="data_export", format='excel')
        if export_info.get('success'):
            st.success("Exported Excel: " + export_info['file_name'])
        else:
            st.warning("Export failed: " + export_info.get('message',''))

    else:
        st.info(trans("Upload a dataset (CSV/Excel) to start analysis.", "ارفع ملف بيانات للبدء في التحليل."))

if __name__ == "__main__":
    main()