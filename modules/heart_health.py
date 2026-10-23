"""
Heart Health & Cardiovascular Wellness Module for MediGuardian AI
Logs vitals, visualizes longitudinal cardiovascular biomarkers, and provides preventive education.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

from datetime import datetime, date
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.supabase_client import insert_data, select_data
from utils.calculations import check_bp_category
from utils.translations import t, get_current_language


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    st.markdown(f"## {t('heart_title')}")
    st.caption(t("heart_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # 1. Vital Signs Entry Form
    st.markdown(f"### {t('log_vitals_title')}")

    with st.form("heart_log_form", clear_on_submit=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            systolic = st.number_input(t("systolic"), min_value=60, max_value=250, value=120, step=1, help="Upper number: pressure when heart contracts.")
            diastolic = st.number_input(t("diastolic"), min_value=40, max_value=160, value=80, step=1, help="Lower number: pressure when heart rests between beats.")
        with c2:
            resting_hr = st.number_input(t("resting_hr"), min_value=40, max_value=220, value=72, step=1, help="Typical adult resting heart rate is 60–100 BPM.")
            activity_min = st.number_input(t("cardio_activity"), min_value=0, max_value=360, value=30, step=5)
        with c3:
            cholesterol_total = st.number_input(t("total_cholesterol"), min_value=50.0, max_value=500.0, value=185.0, step=5.0)
            blood_glucose = st.number_input(t("blood_glucose"), min_value=40.0, max_value=500.0, value=95.0, step=5.0)
        with c4:
            smoking = st.checkbox(t("smoking_check"), value=False)
            notes = st.text_input(t("notes_context"), placeholder="e.g. Measured in morning before breakfast")

        submitted = st.form_submit_button(t("btn_record_vitals"), use_container_width=True, type="primary")

        if submitted:
            log_payload = {
                "user_id": user_id,
                "log_date": date.today().isoformat(),
                "systolic": int(systolic),
                "diastolic": int(diastolic),
                "resting_hr": int(resting_hr),
                "cholesterol_total": float(cholesterol_total),
                "blood_glucose": float(blood_glucose),
                "smoking": bool(smoking),
                "activity_min": int(activity_min),
                "notes": notes,
                "created_at": datetime.now().isoformat()
            }
            try:
                insert_data("heart_logs", log_payload)
                st.success("✅ Vital signs logged successfully!")
            except Exception as e:
                st.error(f"Failed to record log: {e}")

    # Educational check on current input or latest log
    bp_category, bp_color, bp_context = check_bp_category(systolic, diastolic)
    st.markdown(f"**{t('current_assessment')}** :{bp_color}[**{bp_category}**]")
    st.caption(bp_context)

    # Mandatory threshold notification if systolic > 140
    if systolic > 140 or diastolic > 90:
        st.info(t("bp_outside_warning"))

    st.divider()

    # 2. Historical Trends & Visualizations
    st.markdown(f"### {t('longitudinal_trends')}")
    heart_logs = select_data("heart_logs", user_id=user_id, order_by="created_at", ascending=True)

    if heart_logs and len(heart_logs) > 0:
        df_heart = pd.DataFrame(heart_logs)
        # Parse date
        df_heart["formatted_date"] = pd.to_datetime(df_heart["created_at"]).dt.strftime("%b %d, %H:%M")

        tab_bp, tab_quadrant, tab_hr, tab_biomarkers = st.tabs([
            t("tab_bp_trend"),
            t("tab_bp_quadrant"),
            t("tab_hr_trend"),
            t("tab_lipids_glucose")
        ])

        with tab_bp:
            fig_bp = go.Figure()
            fig_bp.add_trace(go.Scatter(
                x=df_heart["formatted_date"],
                y=df_heart["systolic"],
                mode="lines+markers",
                name="Systolic BP (mmHg)",
                line=dict(color="#ef4444", width=3)
            ))
            fig_bp.add_trace(go.Scatter(
                x=df_heart["formatted_date"],
                y=df_heart["diastolic"],
                mode="lines+markers",
                name="Diastolic BP (mmHg)",
                line=dict(color="#3b82f6", width=3)
            ))
            fig_bp.add_hline(y=120, line_dash="dot", line_color="gray", annotation_text="Standard Systolic Threshold (120)")
            fig_bp.add_hline(y=80, line_dash="dot", line_color="gray", annotation_text="Standard Diastolic Threshold (80)")
            fig_bp.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=25, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis_title="Pressure (mmHg)",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bp, use_container_width=True)

        with tab_quadrant:
            # Interactive 2D BP Risk Matrix Quadrant
            st.markdown("#### 🎯 Clinical Blood Pressure Risk Zone Mapping")
            st.caption("Plots your recorded readings onto ACC/AHA clinical classification zones.")

            fig_quad = go.Figure()

            # Background clinical zones
            fig_quad.add_shape(type="rect", x0=40, y0=70, x1=80, y1=120, fillcolor="rgba(34, 197, 94, 0.15)", line_width=0, layer="below")
            fig_quad.add_shape(type="rect", x0=40, y0=120, x1=80, y1=129, fillcolor="rgba(234, 179, 8, 0.18)", line_width=0, layer="below")
            fig_quad.add_shape(type="rect", x0=80, y0=70, x1=89, y1=139, fillcolor="rgba(249, 115, 22, 0.18)", line_width=0, layer="below")
            fig_quad.add_shape(type="rect", x0=40, y0=130, x1=80, y1=139, fillcolor="rgba(249, 115, 22, 0.18)", line_width=0, layer="below")
            fig_quad.add_shape(type="rect", x0=40, y0=140, x1=140, y1=220, fillcolor="rgba(239, 68, 68, 0.18)", line_width=0, layer="below")

            # Historical points
            fig_quad.add_trace(go.Scatter(
                x=df_heart["diastolic"],
                y=df_heart["systolic"],
                mode="markers",
                name="Historical BP Logs",
                marker=dict(size=10, color="#2563eb", symbol="circle", opacity=0.7),
                text=df_heart["formatted_date"],
                hovertemplate="Diastolic: %{x} mmHg<br>Systolic: %{y} mmHg<br>Logged: %{text}<extra></extra>"
            ))

            # Latest point highlighted
            if not df_heart.empty:
                latest_p = df_heart.iloc[-1]
                fig_quad.add_trace(go.Scatter(
                    x=[latest_p["diastolic"]],
                    y=[latest_p["systolic"]],
                    mode="markers+text",
                    name="Latest Reading",
                    marker=dict(size=16, color="#dc2626", symbol="star", line=dict(width=2, color="white")),
                    text=["Latest Reading"],
                    textposition="top center",
                    hovertemplate="Latest Diastolic: %{x} mmHg<br>Latest Systolic: %{y} mmHg<extra></extra>"
                ))

            fig_quad.update_layout(
                xaxis=dict(title="Diastolic BP (mmHg)", range=[50, 120]),
                yaxis=dict(title="Systolic BP (mmHg)", range=[80, 190]),
                height=360,
                margin=dict(l=10, r=10, t=20, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_quad, use_container_width=True)

        with tab_hr:
            fig_hr = px.line(
                df_heart,
                x="formatted_date",
                y="resting_hr",
                markers=True,
                labels={"resting_hr": "BPM", "formatted_date": "Timestamp"},
                color_discrete_sequence=["#10b981"]
            )
            fig_hr.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Tachycardia threshold (100 BPM)")
            fig_hr.add_hline(y=60, line_dash="dash", line_color="blue", annotation_text="Bradycardia threshold (60 BPM)")
            fig_hr.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=25, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_hr, use_container_width=True)

        with tab_biomarkers:
            fig_bio = go.Figure()
            if "cholesterol_total" in df_heart.columns:
                fig_bio.add_trace(go.Scatter(
                    x=df_heart["formatted_date"],
                    y=df_heart["cholesterol_total"],
                    mode="lines+markers",
                    name="Total Cholesterol (mg/dL)",
                    line=dict(color="#f59e0b")
                ))
            if "blood_glucose" in df_heart.columns:
                fig_bio.add_trace(go.Scatter(
                    x=df_heart["formatted_date"],
                    y=df_heart["blood_glucose"],
                    mode="lines+markers",
                    name="Blood Glucose (mg/dL)",
                    line=dict(color="#8b5cf6")
                ))
            fig_bio.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=25, b=10),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_bio, use_container_width=True)
    else:
        st.info("No vital sign records logged yet. Enter your first measurement above.")

    st.divider()

    # 3. Five Educational Risk Factor Expanders
    st.markdown("### 📚 5 Major Modifiable Cardiovascular Risk Factors")

    with st.expander("1. Hypertension (Persistent High Blood Pressure)"):
        st.markdown("""
        - **What it means:** Known as the 'silent killer' because it typically exhibits no overt warning symptoms until advanced stages.
        - **Mechanism:** Excessive hydrostatic pressure against endothelial artery walls causes arterial stiffness and micro-vascular strain.
        - **Preventive lifestyle factors:** Reducing dietary sodium intake (< 2,300 mg/day or ~1 teaspoon), embracing potassium-rich foods (bananas, spinach, dal), and engaging in 150 minutes of weekly moderate aerobic exercise.
        """)

    with st.expander("2. High LDL Cholesterol & Dyslipidemia"):
        st.markdown("""
        - **What it means:** Elevated circulating low-density lipoprotein particles can become trapped and oxidized within arterial linings, forming atheromatous plaques.
        - **Mechanism:** Over time, plaques can narrow the coronary arteries or rupture, causing acute thrombotic events.
        - **Preventive lifestyle factors:** Replacing trans fats and deep-fried items with unsaturated fats (almonds, walnuts, mustard/olive oils) and increasing soluble viscous fiber (oats, isabgol/psyllium, legumes).
        """)

    with st.expander("3. Tobacco Smoking & Second-Hand Exposure"):
        st.markdown("""
        - **What it means:** Cigarette smoke contains thousands of chemicals, including nicotine and carbon monoxide, which immediately elevate heart rate and constrict peripheral arteries.
        - **Mechanism:** Carbon monoxide binds strongly to hemoglobin, reducing oxygen-carrying capacity, while particulate toxins accelerate endothelial inflammation.
        - **Preventive action:** Complete smoking cessation reduces myocardial infarction risk by almost 50% within just 1 to 2 years of quitting.
        """)

    with st.expander("4. Sedentary Lifestyle & Physical Inactivity"):
        st.markdown("""
        - **What it means:** Prolonged sitting (> 8 hours daily) reduces lipoprotein lipase activity, impairing the body's ability to clear fat from the bloodstream.
        - **Mechanism:** Regular cardio movement enhances myocardial stroke volume, endothelial nitric oxide synthesis, and insulin sensitivity.
        - **Actionable habit:** Break up sitting every 45 minutes with a 2-minute stroll; aim for 7,000–10,000 steps daily.
        """)

    with st.expander("5. Chronic Stress & Insufficient Sleep (<6h)"):
        st.markdown("""
        - **What it means:** Sustained sympathetic nervous system hyperactivity causes chronic elevation of cortisol and catecholamines.
        - **Mechanism:** Prolonged cortisol spikes promote insulin resistance, systemic low-grade inflammation, and elevated resting heart rate.
        - **Restorative practice:** Prioritizing 7–8 hours of consistent, dark-room restorative sleep and incorporating deep diaphragmatic breathing or meditation.
        """)
