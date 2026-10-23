"""
Calorie Tracker Module for MediGuardian AI
Tracks daily nutritional intake, compares against calculated TDEE targets, and visualizes trends.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

from datetime import datetime, date, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.supabase_client import insert_data, select_data, delete_data, get_food_database
from utils.calculations import (
    calculate_calories,
    calculate_bmr,
    calculate_tdee,
    get_all_food_names,
    INDIAN_FOOD_DATABASE
)
from utils.translations import t, get_current_language


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    st.markdown(f"## {t('cal_title')}")
    st.caption(t("cal_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # Fetch User Profile to compute target TDEE
    user_records = select_data("users", user_id=user_id)
    user_profile = user_records[0] if user_records else {}

    weight = float(user_profile.get("weight_kg") or 65.0)
    height = float(user_profile.get("height_cm") or 170.0)
    age = int(user_profile.get("age") or 30)
    gender = str(user_profile.get("gender") or "Other")
    activity = str(user_profile.get("activity_level") or "Moderately active")

    bmr = calculate_bmr(weight, height, age, gender)
    target_calories = calculate_tdee(bmr, activity)

    # 1. Meal Logging Form
    st.markdown(f"### {t('log_meal_title')}")
    food_db_list = get_food_database()
    db_food_names = [f["food_name"] for f in food_db_list if "food_name" in f]
    builtin_names = get_all_food_names()
    combined_food_names = sorted(list(set(db_food_names + builtin_names)))

    with st.form("nutrition_log_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col1:
            meal_type = st.selectbox(
                t("meal_type"),
                ["Breakfast", "Lunch", "Dinner", "Snacks", "Late Night"],
                index=1
            )
            meal_time = st.time_input(t("meal_time"), value=datetime.now().time())

        with col2:
            food_selection_mode = st.radio(
                t("select_food_from"),
                [t("food_db_popular"), t("food_db_custom")],
                horizontal=True
            )
            if food_selection_mode == t("food_db_popular"):
                food_name = st.selectbox(t("food_item"), combined_food_names, index=0)
            else:
                food_name = st.text_input(t("food_item"), placeholder="e.g. Oats with Almond Milk")

        with col3:
            portion_grams = st.number_input(
                t("portion_size"),
                min_value=10.0,
                max_value=2000.0,
                value=150.0,
                step=10.0,
                help="Standard roti is ~40g, 1 bowl dal is ~150g, 1 plate rice is ~150-200g."
            )
            water_ml = st.number_input(
                t("water_with_meal"),
                min_value=0.0,
                max_value=2000.0,
                value=250.0,
                step=50.0
            )

        if food_name and str(food_name).strip():
            live_nutr = calculate_calories(str(food_name).strip(), portion_grams)
            st.info(
                f"⚡ **Estimated Nutrients for {portion_grams:.0f}g:** "
                f"**{live_nutr['calories']:.0f} kcal** &nbsp;|&nbsp; "
                f"Protein: **{live_nutr['protein_g']}g** &nbsp;|&nbsp; "
                f"Carbs: **{live_nutr['carbs_g']}g** &nbsp;|&nbsp; "
                f"Fat: **{live_nutr['fat_g']}g**",
                icon="🥗"
            )

        submitted = st.form_submit_button(t("btn_log_meal_submit"), use_container_width=True, type="primary")

        if submitted:
            if not food_name or not str(food_name).strip():
                st.error("Please enter or select a valid food name.")
            else:
                # Calculate nutrition
                nutrition = calculate_calories(str(food_name).strip(), portion_grams)
                log_payload = {
                    "user_id": user_id,
                    "log_date": date.today().isoformat(),
                    "meal_type": meal_type,
                    "food_name": str(food_name).strip(),
                    "portion_grams": portion_grams,
                    "calories": nutrition["calories"],
                    "protein_g": nutrition["protein_g"],
                    "carbs_g": nutrition["carbs_g"],
                    "fat_g": nutrition["fat_g"],
                    "water_ml": water_ml,
                    "meal_time": meal_time.strftime("%H:%M:%S")
                }
                try:
                    insert_data("nutrition_logs", log_payload)
                    st.success(
                        f"✅ Logged {food_name} ({portion_grams}g): {nutrition['calories']} kcal | "
                        f"P: {nutrition['protein_g']}g, C: {nutrition['carbs_g']}g, F: {nutrition['fat_g']}g"
                    )
                except Exception as e:
                    st.error(f"Failed to log meal: {e}")

    st.divider()

    # 2. Daily Summary & KPI Cards
    today_str = date.today().isoformat()
    all_logs = select_data("nutrition_logs", user_id=user_id, order_by="created_at", ascending=False)
    today_logs = [log for log in all_logs if str(log.get("log_date", ""))[:10] == today_str]

    tot_cal = sum(float(l.get("calories") or 0.0) for l in today_logs)
    tot_protein = sum(float(l.get("protein_g") or 0.0) for l in today_logs)
    tot_carbs = sum(float(l.get("carbs_g") or 0.0) for l in today_logs)
    tot_fat = sum(float(l.get("fat_g") or 0.0) for l in today_logs)
    tot_water = sum(float(l.get("water_ml") or 0.0) for l in today_logs)

    st.markdown(f"### {t('today_nutr_overview')}")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    cal_delta = round(tot_cal - target_calories, 1)
    kpi1.metric(
        t("calories_consumed"),
        f"{tot_cal:.0f} kcal",
        f"{cal_delta:+.0f} vs {t('target')} ({target_calories:.0f})",
        delta_color="normal" if abs(cal_delta) < 200 else "inverse"
    )
    kpi2.metric(t("protein"), f"{tot_protein:.1f} g")
    kpi3.metric(t("carbohydrates"), f"{tot_carbs:.1f} g")
    kpi4.metric(t("fats"), f"{tot_fat:.1f} g")
    kpi5.metric(t("water_consumed"), f"{tot_water / 1000.0:.2f} L")

    # Visualizations
    col_chart1, col_chart2 = st.columns([1.6, 1])

    with col_chart1:
        st.markdown(f"#### {t('seven_day_cal_trend')}")
        # Build 7-day data
        past_7_days = [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        daily_cals = {d: 0.0 for d in past_7_days}
        for log in all_logs:
            d = str(log.get("log_date", ""))[:10]
            if d in daily_cals:
                daily_cals[d] += float(log.get("calories") or 0.0)

        df_trend = pd.DataFrame({
            "Date": [datetime.strptime(d, "%Y-%m-%d").strftime("%b %d") for d in past_7_days],
            "Calories": [daily_cals[d] for d in past_7_days],
            "Target": [target_calories] * len(past_7_days)
        })

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=df_trend["Date"],
            y=df_trend["Calories"],
            name="Logged Calories",
            marker_color="#2563eb"
        ))
        fig_bar.add_trace(go.Scatter(
            x=df_trend["Date"],
            y=df_trend["Target"],
            mode="lines+markers",
            name=f"{t('target')} ({target_calories:.0f} kcal)",
            line=dict(color="#ef4444", width=2, dash="dash")
        ))
        fig_bar.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=25, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_chart2:
        st.markdown(f"#### {t('today_macro_split')}")
        if (tot_protein + tot_carbs + tot_fat) > 0:
            labels = [t("protein"), t("carbohydrates"), t("fats")]
            values = [tot_protein * 4, tot_carbs * 4, tot_fat * 9]  # Energy contribution
            fig_pie = px.pie(
                names=labels,
                values=values,
                hole=0.45,
                color_discrete_sequence=["#10b981", "#f59e0b", "#6366f1"]
            )
            fig_pie.update_layout(
                height=300,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Log a meal today to visualize your macronutrient breakdown." if not is_hi else "आज का पोषक तत्व विश्लेषण देखने के लिए भोजन दर्ज करें।")

    # 3. Today's Logs Table
    st.markdown(f"### {t('today_logged_items')}")
    if today_logs:
        display_data = []
        for l in today_logs:
            display_data.append({
                "ID": l.get("id"),
                "Meal": l.get("meal_type"),
                "Food": l.get("food_name"),
                "Portion (g)": l.get("portion_grams"),
                "Calories (kcal)": l.get("calories"),
                "Protein (g)": l.get("protein_g"),
                "Carbs (g)": l.get("carbs_g"),
                "Fat (g)": l.get("fat_g"),
                "Water (ml)": l.get("water_ml"),
                "Time": l.get("meal_time") or l.get("created_at", "")[:16]
            })
        df_today = pd.DataFrame(display_data)
        st.dataframe(df_today.drop(columns=["ID"]), use_container_width=True)

        with st.expander("🗑️ Delete a log entry"):
            col_del_id, col_del_btn = st.columns([3, 1])
            with col_del_id:
                sel_item = st.selectbox(
                    "Choose entry to delete",
                    display_data,
                    format_func=lambda x: f"{x['Meal']}: {x['Food']} ({x['Portion (g)']}g, {x['Calories (kcal)']} kcal)"
                )
            with col_del_btn:
                st.write("")
                st.write("")
                if st.button("Delete Entry", type="secondary"):
                    delete_data("nutrition_logs", "id", sel_item["ID"])
                    st.success("Entry removed.")
                    st.rerun()
    else:
        st.info("No meals logged for today yet. Use the form above to add your breakfast, lunch, or dinner.")
