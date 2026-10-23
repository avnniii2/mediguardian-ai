"""
Lab Report Analyzer & Biomarker Visualizer Module for MediGuardian AI
Extracts medical lab records using safe OCR, enables human verification, and plots longitudinal trends.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 102 (Ambulance) or 112.
"""

from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.supabase_client import insert_data, select_data
from utils.ocr_helper import extract_text, parse_lab_values, get_sample_lab_report_text, evaluate_outside_range
from utils.llm_helper import get_ai_summary
from utils.translations import t, get_current_language


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    st.markdown(f"## {t('report_title')}")
    st.caption(t("report_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # 1. File Upload / Sample Selection
    st.markdown(f"### {t('upload_lab_title')}")
    col_up1, col_up2 = st.columns([2, 1])

    with col_up1:
        uploaded_file = st.file_uploader(
            "रिपोर्ट फ़ाइल अपलोड करें (PNG, JPG, PDF, TXT)" if is_hi else "Upload Report (PNG, JPG, JPEG, PDF, TXT)",
            type=["png", "jpg", "jpeg", "pdf", "txt"],
            help="स्पष्ट प्रकाश और उच्च कंट्रास्ट वाली लैब रिपोर्ट या डिजिटल पीडीएफ से सर्वोत्तम ओसीआर परिणाम मिलते हैं।" if is_hi else "High-contrast, clearly lit lab photos or digital PDF reports yield highest OCR accuracy."
        )

    with col_up2:
        st.write("")
        st.write("")
        load_sample = st.button(
            t("btn_load_sample"),
            use_container_width=True,
            help="परीक्षण हेतु व्यापक नमूना डायग्नोस्टिक रिपोर्ट लोड करता है।" if is_hi else "Loads a comprehensive sample diagnostic report for testing."
        )

    # Initialize session state for extracted text
    if "ocr_raw_text" not in st.session_state:
        st.session_state["ocr_raw_text"] = ""
    if "ocr_confidence" not in st.session_state:
        st.session_state["ocr_confidence"] = 0.0
    if "report_filename" not in st.session_state:
        st.session_state["report_filename"] = "manual_entry"

    if load_sample:
        st.session_state["ocr_raw_text"] = get_sample_lab_report_text()
        st.session_state["ocr_confidence"] = 95.0
        st.session_state["report_filename"] = "sample_blood_test.txt"
        st.success("नमूना प्रयोगशाला रिपोर्ट संपादक में लोड हो गई।" if is_hi else "Sample laboratory report loaded into editor.")

    elif uploaded_file is not None:
        if st.session_state.get("last_uploaded_name") != uploaded_file.name:
            with st.spinner("सुरक्षित ओसीआर इंजन द्वारा टेक्स्ट निकाला जा रहा है..." if is_hi else "Extracting text via safe OCR engine..."):
                raw_text, confidence = extract_text(uploaded_file)
                st.session_state["ocr_raw_text"] = raw_text
                st.session_state["ocr_confidence"] = confidence
                st.session_state["report_filename"] = uploaded_file.name
                st.session_state["last_uploaded_name"] = uploaded_file.name

    # Display and edit raw extracted text
    st.markdown(f"#### {t('extracted_text_title')}")
    if st.session_state["ocr_confidence"] > 0:
        st.caption(f"{'अनुमानित ओसीआर सटीकता' if is_hi else 'Estimated OCR Confidence'}: **{st.session_state['ocr_confidence']:.1f}%**")
    else:
        st.caption("नीचे रिपोर्ट का टेक्स्ट चिपकाएं अथवा समीक्षा करें:" if is_hi else "Paste or review report text below:")

    edited_raw_text = st.text_area(
        "रिपोर्ट का मूल टेक्स्ट (सीधे टाइप अथवा पेस्ट भी कर सकते हैं):" if is_hi else "Report Raw Text (You can paste or edit text directly):",
        value=st.session_state["ocr_raw_text"],
        height=180,
        placeholder="उदा. / e.g.\nHemoglobin 14.2 g/dL (13.0 - 17.0)\nFasting Blood Sugar 115 mg/dL (70-100)\nTotal Cholesterol 215 mg/dL (<200)"
    )
    st.session_state["ocr_raw_text"] = edited_raw_text

    st.divider()

    # 2. Parsed Lab Values & Human-in-the-loop Verification
    st.markdown(f"### {t('structured_extraction')}")
    st.markdown(
        "⚠️ **मानवीय सत्यापन अनिवार्य है:** ओसीआर तकनीक कभी-कभी अक्षरों को गलत पढ़ सकती है (उदा. '8' को 'B' या '1' को 'l')। "
        "कृपया प्रत्येक पंक्ति की समीक्षा करें और प्रोफ़ाइल में सहेजने से पहले **'उपयोगकर्ता द्वारा सत्यापित'** चेकबॉक्स टिक करें।"
        if is_hi else
        "⚠️ **Human Verification Required:** OCR algorithms can misread characters (e.g. '8' as 'B' or '1' as 'l'). "
        "Please review each row and check **'is_verified'** before saving to your profile."
    )

    parsed_items = parse_lab_values(st.session_state["ocr_raw_text"])

    if parsed_items:
        df_parsed = pd.DataFrame(parsed_items)

        edited_df = st.data_editor(
            df_parsed,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "test_name": st.column_config.TextColumn("परीक्षण का नाम" if is_hi else "Test Name", required=True),
                "test_value": st.column_config.TextColumn("मान (टेक्स्ट)" if is_hi else "Value (Text)", required=True),
                "test_value_numeric": st.column_config.NumberColumn("संख्यात्मक मान" if is_hi else "Numeric Value", required=False),
                "unit": st.column_config.TextColumn("इकाई (Unit)" if is_hi else "Unit (e.g. mg/dL, %)"),
                "ref_range": st.column_config.TextColumn("संदर्भ सीमा (Ref Range)" if is_hi else "Reference Range"),
                "is_outside_range": st.column_config.CheckboxColumn("सीमा से बाहर?" if is_hi else "Out of Range?", default=False),
                "is_verified": st.column_config.CheckboxColumn("सत्यापित?" if is_hi else "Verified by User?", default=False)
            }
        )

        col_save_btn, col_llm_btn = st.columns([1, 1])

        with col_save_btn:
            if st.button(t("btn_save_verified"), type="primary", use_container_width=True):
                saved_count = 0
                for _, row in edited_df.iterrows():
                    # Only save verified records or prompt user
                    if bool(row.get("is_verified", False)):
                        val_num = row.get("test_value_numeric")
                        if pd.isna(val_num):
                            try:
                                val_num = float(str(row.get("test_value", "")).strip())
                            except Exception:
                                val_num = None

                        record = {
                            "user_id": user_id,
                            "upload_date": datetime.now().isoformat(),
                            "file_name": st.session_state["report_filename"],
                            "test_name": str(row.get("test_name", "")).strip(),
                            "test_value": str(row.get("test_value", "")).strip(),
                            "test_value_numeric": val_num,
                            "unit": str(row.get("unit", "")).strip(),
                            "ref_range": str(row.get("ref_range", "")).strip(),
                            "is_outside_range": bool(row.get("is_outside_range", False)),
                            "is_verified": True,
                            "ocr_confidence": float(st.session_state["ocr_confidence"] or 85.0),
                            "created_at": datetime.now().isoformat()
                        }
                        try:
                            insert_data("lab_reports", record)
                            saved_count += 1
                        except Exception as e:
                            print(f"Error inserting lab report row: {e}")

                if saved_count > 0:
                    st.success(f"🎉 {saved_count} {'सत्यापित लैब परिणाम सफलतापूर्वक सुरक्षित किए गए!' if is_hi else 'verified laboratory result(s) successfully saved!'}")
                else:
                    st.warning("किसी भी पंक्ति में 'सत्यापित' चेकबॉक्स टिक नहीं था। कृपया उन पंक्तियों को चुनें जिन्हें आप सहेजना चाहते हैं।" if is_hi else "No records had 'is_verified' checked. Please mark the checkboxes for rows you wish to store.")

        with col_llm_btn:
            explain_clicked = st.button(t("btn_explain_ai"), use_container_width=True)

        if explain_clicked:
            with st.spinner("शैक्षणिक बायोमार्कर जानकारी प्राप्त की जा रही है..." if is_hi else "Retrieving educational biomarker context..."):
                test_names = [str(r.get("test_name", "")) for _, r in edited_df.iterrows() if r.get("test_name")]
                if is_hi:
                    prompt = (
                        f"कृपया निम्नलिखित प्रयोगशाला परीक्षण मार्करों की सरल, रोगी-अनुकूल और शैक्षणिक व्याख्या हिंदी में प्रदान करें: "
                        f"{', '.join(test_names[:6])}। "
                        f"समझाएं कि वे किन शारीरिक प्रणालियों से संबंधित हैं, सामान्य सीमाएं क्या दर्शाती हैं, "
                        f"और स्पष्ट करें कि यह पूरी तरह से शैक्षणिक है और चिकित्सीय निदान नहीं है।"
                    )
                else:
                    prompt = (
                        f"Please provide a simple, patient-friendly educational explanation of the following laboratory test markers: "
                        f"{', '.join(test_names[:6])}. "
                        f"Explain what physiological systems they relate to, what normal ranges generally indicate, "
                        f"and clarify that this is strictly educational and not a medical diagnosis."
                    )
                ai_explanation = get_ai_summary(prompt)
                st.markdown("#### 💡 " + ("शैक्षणिक बायोमार्कर अंतर्दृष्टि" if is_hi else "Educational Biomarker Insights"))
                st.markdown(ai_explanation)

    else:
        st.info("अभी तक कोई संरचित परीक्षण पंक्तियां नहीं पहचानी गईं। ऊपर लैब टेक्स्ट दर्ज करें या 'नमूना रक्त रिपोर्ट लोड करें' पर क्लिक करें।" if is_hi else "No structured test rows identified yet. Enter lab text above or click 'Load Sample Blood Report'.")

    st.divider()

    # 3. Longitudinal Biomarker Trend Visualizer
    st.markdown(f"### {t('longitudinal_lab_title')}")
    all_reports = select_data("lab_reports", user_id=user_id, order_by="created_at", ascending=True)

    if all_reports and len(all_reports) > 0:
        df_all = pd.DataFrame(all_reports)
        # Unique test names
        available_tests = sorted(list(df_all["test_name"].dropna().unique()))

        if available_tests:
            col_sel_test, col_metric = st.columns([2, 1])
            with col_sel_test:
                chosen_test = st.selectbox("चार्ट हेतु परीक्षण बायोमार्कर चुनें" if is_hi else "Select Test Biomarker to Plot", available_tests)

            test_subset = df_all[df_all["test_name"] == chosen_test].copy()
            test_subset = test_subset.dropna(subset=["test_value_numeric"])

            if not test_subset.empty:
                test_subset["display_date"] = pd.to_datetime(test_subset["created_at"]).dt.strftime("%b %d, %Y")
                latest_row = test_subset.iloc[-1]
                unit_str = latest_row.get("unit") or ""
                ref_str = latest_row.get("ref_range") or "N/A"

                with col_metric:
                    st.metric(
                        f"{'नवीनतम' if is_hi else 'Latest'} {chosen_test}",
                        f"{latest_row['test_value_numeric']} {unit_str}",
                        f"{'संदर्भ सीमा' if is_hi else 'Ref'}: {ref_str}"
                    )

                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    x=test_subset["display_date"],
                    y=test_subset["test_value_numeric"],
                    mode="lines+markers",
                    name=chosen_test,
                    line=dict(color="#2563eb", width=3),
                    marker=dict(size=8, color="#1d4ed8")
                ))

                fig_trend.update_layout(
                    title=f"{'ऐतिहासिक प्रक्षेपवक्र' if is_hi else 'Historical Trajectory'}: {chosen_test} ({unit_str})",
                    height=320,
                    margin=dict(l=10, r=10, t=35, b=10),
                    yaxis_title=unit_str,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_trend, use_container_width=True)

                if latest_row.get("is_outside_range"):
                    st.warning(f"⚠️ {'सूचना: नवीनतम दर्ज किया गया मान' if is_hi else 'Notice: The latest recorded value'} ({latest_row['test_value_numeric']} {unit_str}) {'सामान्य संदर्भ सीमा से बाहर है' if is_hi else 'was flagged as outside typical laboratory reference range'} ({ref_str}). {'कृपया अपने डॉक्टर से चर्चा करें।' if is_hi else 'Please discuss with your doctor.'}")
            else:
                st.info(f"{chosen_test} के लिए अभी कोई संख्यात्मक मान दर्ज नहीं है।" if is_hi else f"No numeric values recorded for {chosen_test} yet.")
    else:
        st.info("आपके इतिहास में अभी कोई सुरक्षित लैब परिणाम नहीं हैं। रुझान ग्राफ अनलॉक करने के लिए ऊपर एक रिपोर्ट सत्यापित और सुरक्षित करें।" if is_hi else "No saved laboratory results in your history yet. Verify and save a report above to unlock trend graphing.")
