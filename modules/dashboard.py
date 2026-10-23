"""
Executive Health Intelligence Dashboard Module for MediGuardian AI
Synthesizes multi-stream biometric data into 4 core metrics, weekly summaries, cautious pattern detection, and clinical CSV export.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

from datetime import datetime, date, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.supabase_client import select_data, insert_data
from utils.calculations import calculate_bmr, calculate_tdee
from utils.translations import t, get_current_language


def show(user_id: str):
    st.markdown(f"## {t('dash_title')}")
    st.caption(t("dash_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # Fetch User Profile
    user_records = select_data("users", user_id=user_id)
    user_profile = user_records[0] if user_records else {}
    user_name = user_profile.get("name") or "Learner"

    # Fetch Data Streams
    nutrition_logs = select_data("nutrition_logs", user_id=user_id, order_by="created_at", ascending=False)
    heart_logs = select_data("heart_logs", user_id=user_id, order_by="created_at", ascending=False)
    daily_logs = select_data("daily_health_logs", user_id=user_id, order_by="created_at", ascending=False)
    medicines = select_data("medicines", user_id=user_id, order_by="created_at", ascending=False)
    intake_logs = select_data("intake_logs", user_id=user_id, order_by="created_at", ascending=False)
    lab_reports = select_data("lab_reports", user_id=user_id, order_by="created_at", ascending=False)

    # Calculate 7-Day Window
    today = date.today()
    seven_days_ago = today - timedelta(days=7)
    seven_days_ago_str = seven_days_ago.isoformat()

    # 1. METRIC 1: Avg Calories Last 7 Days
    recent_nutr = [n for n in nutrition_logs if str(n.get("log_date", ""))[:10] >= seven_days_ago_str]
    days_with_nutr = set(str(n.get("log_date", ""))[:10] for n in recent_nutr)
    tot_recent_cals = sum(float(n.get("calories") or 0.0) for n in recent_nutr)
    avg_cals = (tot_recent_cals / len(days_with_nutr)) if days_with_nutr else 0.0

    bmr = calculate_bmr(
        user_profile.get("weight_kg") or 65.0,
        user_profile.get("height_cm") or 170.0,
        user_profile.get("age") or 30,
        user_profile.get("gender") or "Other"
    )
    tdee = calculate_tdee(bmr, user_profile.get("activity_level") or "Moderately active")

    # 2. METRIC 2: Avg Sleep Hours
    recent_daily = [d for d in daily_logs if str(d.get("log_date", ""))[:10] >= seven_days_ago_str]
    sleep_values = [float(d.get("sleep_hours") or 0.0) for d in recent_daily if d.get("sleep_hours") is not None]
    avg_sleep = (sum(sleep_values) / len(sleep_values)) if sleep_values else 7.0

    # 3. METRIC 3: Medication Adherence %
    active_meds = [m for m in medicines if m.get("is_active", True)]
    recent_intakes = [i for i in intake_logs if str(i.get("created_at", ""))[:10] >= seven_days_ago_str]
    if active_meds:
        expected_doses = max(1, len(active_meds) * 7)
        adherence_pct = min(100.0, round((len(recent_intakes) / expected_doses) * 100.0, 1))
    else:
        adherence_pct = 100.0 if not medicines else 0.0

    # 4. METRIC 4: Pending / Active Medicines
    pending_count = len(active_meds)

    # Compute Real-time Vitality Score (0-100)
    cal_diff_pct = abs(avg_cals - tdee) / max(1.0, tdee) if avg_cals > 0 else 0.4
    s_nutr = 25 if cal_diff_pct <= 0.15 else (18 if cal_diff_pct <= 0.30 else 12)
    s_sleep = 25 if (7.0 <= avg_sleep <= 9.0) else (18 if (6.0 <= avg_sleep < 7.0) else 12)
    latest_heart = heart_logs[0] if heart_logs else None
    if latest_heart:
        sys_val = latest_heart.get("systolic") or 120
        dia_val = latest_heart.get("diastolic") or 80
        s_bp = 25 if (sys_val < 120 and dia_val < 80) else (18 if sys_val <= 135 else 12)
    else:
        s_bp = 20
    s_adh = min(25, round(adherence_pct * 0.25))
    vitality_score = int(s_nutr + s_sleep + s_bp + s_adh)

    # Top Section: Greeting + Metrics + Vitality Index Gauge
    st.markdown(f"### 👋 {t('welcome')}, **{user_name}**")
    col_hero_left, col_hero_gauge = st.columns([1.6, 1], gap="medium")

    is_hi = get_current_language() == "हिंदी"

    with col_hero_left:
        m1, m2 = st.columns(2)
        m1.metric(
            t("kpi_avg_calories"),
            f"{avg_cals:.0f} kcal/day" if avg_cals > 0 else ("कोई लॉग नहीं" if is_hi else "No logs yet"),
            f"{t('target')}: {tdee:.0f} kcal"
        )
        m2.metric(
            t("kpi_avg_sleep"),
            f"{avg_sleep:.1f} hrs/night",
            t("target_sleep") if avg_sleep >= 7 else t("sleep_below_optimal")
        )

        m3, m4 = st.columns(2)
        m3.metric(
            t("kpi_med_adherence"),
            f"{adherence_pct:.0f}%",
            f"{len(recent_intakes)} {t('doses_logged_week')}"
        )
        m4.metric(
            t("kpi_active_prescriptions"),
            f"{pending_count}",
            f"{sum(1 for m in active_meds if int(m.get('quantity_left', 0)) < 5)} {t('low_stock_count')}"
        )

    with col_hero_gauge:
        # Interactive Speedometer Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=vitality_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': t("vitality_score_title"), 'font': {'size': 15, 'color': '#1e293b'}},
            number={'suffix': "/100", 'font': {'size': 26, 'color': '#2563eb'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "gray"},
                'bar': {'color': "#2563eb", 'thickness': 0.28},
                'steps': [
                    {'range': [0, 45], 'color': "#fee2e2"},
                    {'range': [45, 75], 'color': "#fef3c7"},
                    {'range': [75, 100], 'color': "#dcfce7"}
                ],
                'threshold': {
                    'line': {'color': "#16a34a", 'width': 3},
                    'thickness': 0.8,
                    'value': 80
                }
            }
        ))
        fig_gauge.update_layout(
            height=210,
            margin=dict(l=15, r=15, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Interactive Launchpad Navigation Tiles
    st.markdown(f"#### {t('quick_actions')}")
    col_act1, col_act2, col_act3, col_act4, col_act5, col_act6 = st.columns(6)

    def go_to(dest_key):
        st.session_state["active_module_key"] = dest_key
        st.session_state["nav_choice"] = dest_key
        st.rerun()

    with col_act1:
        if st.button(t("btn_log_meal"), use_container_width=True):
            go_to("calorie_tracker")
    with col_act2:
        if st.button(t("btn_track_bp"), use_container_width=True):
            go_to("heart_health")
    with col_act3:
        if st.button(t("btn_meds_doses"), use_container_width=True):
            go_to("medicine_tracker")
    with col_act4:
        if st.button(t("btn_lab_report"), use_container_width=True):
            go_to("report_analyzer")
    with col_act5:
        if st.button(t("btn_meal_plan"), use_container_width=True):
            go_to("diet_planner")
    with col_act6:
        if st.button(t("btn_emergency"), use_container_width=True, type="primary"):
            go_to("emergency_assistant")

    # Interactive Quick Hydration Bar
    st.markdown(f"#### {t('hydration_title')}")
    col_w1, col_w2, col_w3, col_w_info = st.columns([1, 1, 1, 1.5])
    
    with col_w1:
        if st.button(t("btn_glass"), use_container_width=True):
            insert_data("daily_health_logs", {
                "user_id": user_id,
                "log_date": today.isoformat(),
                "water_liters": 0.25,
                "sleep_hours": 7.0,
                "exercise_min": 0,
                "symptoms": "None",
                "mood": "Calm",
                "created_at": datetime.now().isoformat()
            })
            st.toast("💧 Logged +250ml of water hydration!", icon="✅")
            st.rerun()

    with col_w2:
        if st.button(t("btn_bottle"), use_container_width=True):
            insert_data("daily_health_logs", {
                "user_id": user_id,
                "log_date": today.isoformat(),
                "water_liters": 0.5,
                "sleep_hours": 7.0,
                "exercise_min": 0,
                "symptoms": "None",
                "mood": "Calm",
                "created_at": datetime.now().isoformat()
            })
            st.toast("💧 Logged +500ml of hydration!", icon="✅")
            st.rerun()

    with col_w3:
        if st.button(t("btn_liter"), use_container_width=True):
            insert_data("daily_health_logs", {
                "user_id": user_id,
                "log_date": today.isoformat(),
                "water_liters": 1.0,
                "sleep_hours": 7.0,
                "exercise_min": 0,
                "symptoms": "None",
                "mood": "Calm",
                "created_at": datetime.now().isoformat()
            })
            st.toast("💧 Logged +1.0 Liter hydration!", icon="✅")
            st.rerun()

    with col_w_info:
        # Calculate today's logged water
        today_daily = [d for d in daily_logs if str(d.get("log_date", ""))[:10] == today.isoformat()]
        today_water = sum(float(d.get("water_liters") or 0.0) for d in today_daily)
        st.markdown(f"**{t('today_hydration')}:** `{today_water:.2f} / 3.0 L` {t('target')}")
        st.progress(min(1.0, today_water / 3.0))

    st.divider()

    # 2. Weekly Multi-Stream Data Synthesis & Visualizations
    st.markdown(f"### {t('weekly_synthesis')}")

    tab_vis1, tab_vis2, tab_vis3 = st.tabs([t("tab_cal_water"), t("tab_sleep_exercise"), t("tab_cardio_vitals")])

    with tab_vis1:
        # Build 7-day consolidated dataframe
        date_list = [(today - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        cal_dict = {d: 0.0 for d in date_list}
        water_dict = {d: 0.0 for d in date_list}

        for n in nutrition_logs:
            d = str(n.get("log_date", ""))[:10]
            if d in cal_dict:
                cal_dict[d] += float(n.get("calories") or 0.0)
                water_dict[d] += float(n.get("water_ml") or 0.0) / 1000.0

        for dl in daily_logs:
            d = str(dl.get("log_date", ""))[:10]
            if d in water_dict and dl.get("water_liters"):
                water_dict[d] = max(water_dict[d], float(dl.get("water_liters")))

        df_sync = pd.DataFrame({
            "Date": [datetime.strptime(d, "%Y-%m-%d").strftime("%a, %b %d") for d in date_list],
            "Calories (kcal)": [cal_dict[d] for d in date_list],
            "Water (Liters)": [water_dict[d] for d in date_list]
        })

        fig_cal_water = go.Figure()
        fig_cal_water.add_trace(go.Bar(
            x=df_sync["Date"],
            y=df_sync["Calories (kcal)"],
            name="Daily Calories (kcal)",
            marker_color="#3b82f6"
        ))
        fig_cal_water.add_trace(go.Scatter(
            x=df_sync["Date"],
            y=df_sync["Water (Liters)"],
            name="Water Intake (L)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#06b6d4", width=3)
        ))
        fig_cal_water.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(title="Energy (kcal)"),
            yaxis2=dict(title="Hydration (L)", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_cal_water, use_container_width=True)

    with tab_vis2:
        sleep_map = {d: 0.0 for d in date_list}
        exercise_map = {d: 0.0 for d in date_list}
        for dl in daily_logs:
            d = str(dl.get("log_date", ""))[:10]
            if d in sleep_map:
                sleep_map[d] = float(dl.get("sleep_hours") or 0.0)
                exercise_map[d] = float(dl.get("exercise_min") or 0.0)

        df_lifestyle = pd.DataFrame({
            "Date": [datetime.strptime(d, "%Y-%m-%d").strftime("%a, %b %d") for d in date_list],
            "Sleep (Hours)": [sleep_map[d] for d in date_list],
            "Exercise (Minutes)": [exercise_map[d] for d in date_list]
        })

        fig_life = go.Figure()
        fig_life.add_trace(go.Bar(
            x=df_lifestyle["Date"],
            y=df_lifestyle["Exercise (Minutes)"],
            name="Exercise (Min)",
            marker_color="#10b981"
        ))
        fig_life.add_trace(go.Scatter(
            x=df_lifestyle["Date"],
            y=df_lifestyle["Sleep (Hours)"],
            name="Sleep (Hours)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#8b5cf6", width=3)
        ))
        fig_life.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=25, b=10),
            yaxis=dict(title="Physical Activity (Min)"),
            yaxis2=dict(title="Sleep (Hours)", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_life, use_container_width=True)

    with tab_vis3:
        if heart_logs:
            df_h = pd.DataFrame(heart_logs).head(10)
            df_h["date_str"] = pd.to_datetime(df_h["created_at"]).dt.strftime("%b %d, %H:%M")
            fig_h = go.Figure()
            fig_h.add_trace(go.Scatter(x=df_h["date_str"], y=df_h["systolic"], name="Systolic", line=dict(color="#ef4444", width=2)))
            fig_h.add_trace(go.Scatter(x=df_h["date_str"], y=df_h["diastolic"], name="Diastolic", line=dict(color="#3b82f6", width=2)))
            fig_h.update_layout(
                height=320,
                margin=dict(l=10, r=10, t=25, b=10),
                yaxis_title="Blood Pressure (mmHg)",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.info("No cardiovascular vitals recorded yet. Use the Heart Health module to log readings.")

    st.divider()

    # 3. Cautious Pattern Observation (Pandas Analysis)
    st.markdown("### 🔍 Cautious Preventive Pattern Observations")
    st.caption("Heuristic behavioral correlation detection across your multi-stream health logs.")

    patterns_found = []

    if daily_logs and len(daily_logs) >= 2:
        df_d = pd.DataFrame(daily_logs)
        df_d["sleep_num"] = pd.to_numeric(df_d.get("sleep_hours"), errors="coerce").fillna(7.0)
        df_d["exercise_num"] = pd.to_numeric(df_d.get("exercise_min"), errors="coerce").fillna(0.0)
        df_d["sym_str"] = df_d.get("symptoms", "").fillna("None").astype(str).str.lower()

        # Heuristic 1: Sleep < 6h vs Symptoms (e.g. headache, fatigue)
        short_sleep = df_d[df_d["sleep_num"] < 6.0]
        if not short_sleep.empty:
            headache_count = short_sleep[short_sleep["sym_str"].str.contains("headache|migraine|head ache")].shape[0]
            fatigue_count = short_sleep[short_sleep["sym_str"].str.contains("fatigue|tired|exhaust")].shape[0]

            if headache_count > 0:
                patterns_found.append(
                    f"💡 **Sleep Duration & Headache:** You logged 'headache' **{headache_count} time(s)** on days with sleep duration under 6 hours."
                )
            if fatigue_count > 0:
                patterns_found.append(
                    f"💡 **Sleep Duration & Fatigue:** You logged 'fatigue' **{fatigue_count} time(s)** following nights with less than 6 hours of sleep."
                )

        # Heuristic 2: Exercise vs Mood
        if "mood" in df_d.columns:
            active_days = df_d[df_d["exercise_num"] >= 30.0]
            if not active_days.empty:
                energetic_count = active_days[active_days["mood"].str.lower().str.contains("energetic|calm")].shape[0]
                if energetic_count >= 2:
                    patterns_found.append(
                        f"🏃 **Physical Activity & Mood:** On **{energetic_count} days** with 30+ minutes of exercise, you reported an 'Energetic' or 'Calm' mood."
                    )

    if not patterns_found:
        patterns_found.append("🌱 Continue logging your daily sleep, nutrition, and symptoms to discover personalized lifestyle patterns.")

    # Render pattern alert box
    for p in patterns_found:
        st.markdown(
            f'<div style="background-color: #f1f5f9; border-left: 5px solid #64748b; padding: 12px 16px; border-radius: 6px; margin-bottom: 8px;">'
            f'<p style="margin: 0; color: #1e293b; font-size: 14.5px;">{p}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Scientific Caution Disclaimer
    st.caption(f"🔬 *{t('association_disclaimer')}*")

    st.divider()

    # 4. Export Summary CSV for Doctor
    st.markdown(f"### {t('clinical_export_title')}")
    st.markdown(t("clinical_export_desc"))

    # Build comprehensive export dataframe
    export_rows = []
    # Merge daily records
    date_tracker = {}
    for n in nutrition_logs:
        d = str(n.get("log_date", ""))[:10]
        if d not in date_tracker:
            date_tracker[d] = {"date": d, "calories": 0.0, "water_ml": 0.0, "systolic": None, "diastolic": None, "resting_hr": None, "sleep_hrs": None, "exercise_min": None, "symptoms": "", "meds_taken": 0}
        date_tracker[d]["calories"] += float(n.get("calories") or 0.0)
        date_tracker[d]["water_ml"] += float(n.get("water_ml") or 0.0)

    for h in heart_logs:
        d = str(h.get("log_date", ""))[:10]
        if d not in date_tracker:
            date_tracker[d] = {"date": d, "calories": 0.0, "water_ml": 0.0, "systolic": None, "diastolic": None, "resting_hr": None, "sleep_hrs": None, "exercise_min": None, "symptoms": "", "meds_taken": 0}
        date_tracker[d]["systolic"] = h.get("systolic")
        date_tracker[d]["diastolic"] = h.get("diastolic")
        date_tracker[d]["resting_hr"] = h.get("resting_hr")

    for dl in daily_logs:
        d = str(dl.get("log_date", ""))[:10]
        if d not in date_tracker:
            date_tracker[d] = {"date": d, "calories": 0.0, "water_ml": 0.0, "systolic": None, "diastolic": None, "resting_hr": None, "sleep_hrs": None, "exercise_min": None, "symptoms": "", "meds_taken": 0}
        date_tracker[d]["sleep_hrs"] = dl.get("sleep_hours")
        date_tracker[d]["exercise_min"] = dl.get("exercise_min")
        date_tracker[d]["symptoms"] = dl.get("symptoms", "")

    for i in intake_logs:
        d = str(i.get("created_at", ""))[:10]
        if d in date_tracker:
            date_tracker[d]["meds_taken"] += 1

    df_export = pd.DataFrame(list(date_tracker.values()))
    if not df_export.empty:
        df_export = df_export.sort_values(by="date", ascending=False)
        csv_bytes = df_export.to_csv(index=False).encode("utf-8")

        st.download_button(
            label=t("btn_download_summary"),
            data=csv_bytes,
            file_name=f"MediGuardian_Doctor_Summary_{user_name}_{today.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.info("Log some vitals, meals, or habits to generate your clinical export file.")
