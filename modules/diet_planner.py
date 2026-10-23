"""
Diet Planner Module for MediGuardian AI
Generates deterministic, culturally adapted, and budget-conscious Indian meal plans.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

from datetime import datetime
import streamlit as st
import pandas as pd

from utils.supabase_client import insert_data, select_data
from utils.calculations import calculate_bmr, calculate_tdee
from utils.translations import t, get_current_language


def generate_deterministic_plan(goal: str, diet_pref: str, budget: str, allergies: str, target_cals: float) -> list:
    """
    Deterministically crafts a 4-meal daily menu tailored to goal, preference, budget, and allergy flags.
    """
    pref = diet_pref.lower()
    g = goal.lower()
    b = budget.lower()
    al = (allergies or "").lower()

    is_veg = "veg" in pref and "non" not in pref
    is_nonveg = "non-veg" in pref or "chicken" in pref or "fish" in pref
    is_low_budget = "low" in b or "economy" in b

    # Adjust calorie target slightly according to physiological goal
    if "loss" in g:
        adjusted_cals = max(1200.0, target_cals - 400.0)
    elif "gain" in g:
        adjusted_cals = target_cals + 350.0
    else:
        adjusted_cals = target_cals

    # Default plans
    if is_veg and is_low_budget:
        plan = [
            {
                "Meal": "Breakfast",
                "Items": "Poha with roasted peanuts & lemon + 1 cup spiced Curd/Dahi" if "dairy" not in al else "Vegetable Poha with roasted peanuts & herbal tea",
                "Calories (kcal)": round(adjusted_cals * 0.25),
                "Key Nutrients": "Complex Carbs, Vitamin C, Iron"
            },
            {
                "Meal": "Lunch",
                "Items": "1 cup Yellow Dal Tadka + 1 cup Steamed Brown/White Rice + 1 Roti + Fresh Cucumber slices",
                "Calories (kcal)": round(adjusted_cals * 0.35),
                "Key Nutrients": "Plant Protein, Dietary Fiber, Potassium"
            },
            {
                "Meal": "Evening Snack",
                "Items": "1 fistful Roasted Chana (Bengal Gram) + 1 cup Masala Chai (Low sugar)",
                "Calories (kcal)": round(adjusted_cals * 0.12),
                "Key Nutrients": "Resistant Starch, Clean Protein"
            },
            {
                "Meal": "Dinner",
                "Items": "Moong Dal Khichdi with carrots & peas + 1 glass Buttermilk (Chaas)" if "dairy" not in al else "Moong Dal Khichdi with steamed spinach",
                "Calories (kcal)": round(adjusted_cals * 0.28),
                "Key Nutrients": "Easily digestible protein, Probiotics, Magnesium"
            }
        ]
    elif is_nonveg:
        plan = [
            {
                "Meal": "Breakfast",
                "Items": "2 Boiled Eggs / Veggie Egg Omelette + 2 Whole wheat toasts / 1 Besan Chilla",
                "Calories (kcal)": round(adjusted_cals * 0.25),
                "Key Nutrients": "High Quality Complete Protein, Choline, B12"
            },
            {
                "Meal": "Lunch",
                "Items": "Home-style Chicken Curry (or Fish Curry) + 1 cup Steamed Rice + Green Salad",
                "Calories (kcal)": round(adjusted_cals * 0.35),
                "Key Nutrients": "Lean Protein, Omega-3 Fatty Acids, Iron"
            },
            {
                "Meal": "Evening Snack",
                "Items": "Sprouts Salad with tomato, cucumber & chaat masala + handful of roasted makhana",
                "Calories (kcal)": round(adjusted_cals * 0.12),
                "Key Nutrients": "Antioxidants, Low Glycemic Load"
            },
            {
                "Meal": "Dinner",
                "Items": "Yellow Dal or Grilled Chicken Tikka + 2 Multigrain Rotis + Steamed Veggies",
                "Calories (kcal)": round(adjusted_cals * 0.28),
                "Key Nutrients": "High Satiety, Sustained Amino Acid Release"
            }
        ]
    else:  # Vegetarian Medium/High Budget
        plan = [
            {
                "Meal": "Breakfast",
                "Items": "2 Besan Chilla stuffed with Crumbled Paneer & Coriander + Mint Chutney",
                "Calories (kcal)": round(adjusted_cals * 0.25),
                "Key Nutrients": "High Protein, Fiber, Calcium"
            },
            {
                "Meal": "Lunch",
                "Items": "Palak Paneer (or Chole) + 2 Phulkas + 1 cup Brown Rice + Onion-Tomato Raita",
                "Calories (kcal)": round(adjusted_cals * 0.35),
                "Key Nutrients": "Bioavailable Calcium, Folate, Iron"
            },
            {
                "Meal": "Evening Snack",
                "Items": "1 cup Roasted Makhana (Foxnuts) with turmeric + 6-8 soaked Almonds",
                "Calories (kcal)": round(adjusted_cals * 0.12),
                "Key Nutrients": "Healthy Fats, Vitamin E, Flavonoids"
            },
            {
                "Meal": "Dinner",
                "Items": "Rajma Masala / Mixed Vegetable Paneer Bhurji + 2 Rotis + Green Cucumber Salad",
                "Calories (kcal)": round(adjusted_cals * 0.28),
                "Key Nutrients": "Slow-digesting complex carbs, Gut-friendly fiber"
            }
        ]

    return plan, adjusted_cals


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    st.markdown(f"## {t('diet_title')}")
    st.caption(t("diet_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # Fetch user profile to calculate accurate caloric recommendations
    user_records = select_data("users", user_id=user_id)
    user_profile = user_records[0] if user_records else {}

    weight = float(user_profile.get("weight_kg") or 65.0)
    height = float(user_profile.get("height_cm") or 170.0)
    age = int(user_profile.get("age") or 30)
    gender = str(user_profile.get("gender") or "Other")
    activity = str(user_profile.get("activity_level") or "Moderately active")

    bmr = calculate_bmr(weight, height, age, gender)
    baseline_tdee = calculate_tdee(bmr, activity)

    col_cfg1, col_cfg2 = st.columns([1, 1])

    with col_cfg1:
        st.markdown("#### 🎯 " + ("स्वास्थ्य लक्ष्य एवं प्राथमिकताएं" if is_hi else "Health Goal & Preferences"))
        goal = st.selectbox(
            t("wellness_objective"),
            ["Weight Loss & Fat Reduction", "Healthy Maintenance", "Muscle Gain & Strength", "Heart-Healthy / Low-Sodium"]
        )
        diet_pref = st.selectbox(
            t("dietary_lifestyle"),
            ["Vegetarian", "Non-Vegetarian", "Eggetarian", "Vegan"],
            index=0 if "veg" in str(user_profile.get("dietary_preference", "")).lower() else 1
        )

    with col_cfg2:
        st.markdown("#### 💰 " + ("बजट एवं संवेदनशीलता" if is_hi else "Budget & Sensitivities"))
        budget = st.selectbox(
            t("budget_tier"),
            ["Low Budget (Budget-friendly local pulses & grains)", "Medium (Balanced seasonal vegetables & dairy)", "High (High protein nuts, seeds & lean meats)"]
        )
        allergies = st.text_input(
            t("allergies_label"),
            value=user_profile.get("allergies") or "None",
            placeholder="e.g. Lactose intolerant, Peanut allergy, Gluten sensitive"
        )

    generate_clicked = st.button(t("btn_generate_diet"), type="primary", use_container_width=True)

    # Maintain generated plan in session state
    if "current_diet_plan" not in st.session_state or generate_clicked:
        plan_rows, adjusted_target = generate_deterministic_plan(goal, diet_pref, budget, allergies, baseline_tdee)
        st.session_state["current_diet_plan"] = plan_rows
        st.session_state["current_adjusted_target"] = adjusted_target

    plan_rows = st.session_state.get("current_diet_plan", [])
    adjusted_target = st.session_state.get("current_adjusted_target", baseline_tdee)

    st.divider()

    # Interactive Calorie Scaling Control
    scaled_target = st.slider(
        t("fine_tune_cals"),
        min_value=1200,
        max_value=3500,
        value=int(adjusted_target),
        step=50,
        help="दैनिक व्यायाम अथवा भूख के अनुसार अपने लक्षित कैलोरी सेवन को गतिशील रूप से समायोजित करें।" if is_hi else "Slide to dynamically calibrate your target caloric intake based on daily training or hunger."
    )

    # Plan Summary Metrics
    total_plan_cals = sum(item["Calories (kcal)"] for item in plan_rows)
    m1, m2, m3 = st.columns(3)
    lbl_tdee = "गणना बेसलाइन TDEE" if is_hi else "Calculated Baseline TDEE"
    lbl_target = "लक्षित कैलोरी सेवन" if is_hi else "Target Caloric Intake"
    lbl_plan_cals = "योजना कुल कैलोरी" if is_hi else "Generated Plan Calories"
    lbl_vs_tdee = "TDEE तुलना" if is_hi else "vs TDEE"

    m1.metric(lbl_tdee, f"{baseline_tdee:.0f} kcal")
    m2.metric(lbl_target, f"{scaled_target} kcal", f"{scaled_target - int(baseline_tdee):+d} {lbl_vs_tdee}")
    m3.metric(lbl_plan_cals, f"{total_plan_cals:.0f} kcal")

    st.markdown(f"### {t('customize_plan')}")
    st.caption("आप सहेजने या निर्यात करने से पहले नीचे दी गई तालिका में किसी भी सेल को सीधे संपादित कर सकते हैं।" if is_hi else "You can edit any cell directly in the table below before saving or exporting.")

    df_plan = pd.DataFrame(plan_rows)
    edited_df = st.data_editor(
        df_plan,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Meal": st.column_config.SelectboxColumn("भोजन प्रकार" if is_hi else "Meal Type", options=["Breakfast", "Lunch", "Evening Snack", "Dinner"]),
            "Items": st.column_config.TextColumn("खाद्य सामग्री" if is_hi else "Food Items & Ingredients", width="large"),
            "Calories (kcal)": st.column_config.NumberColumn("अनुमानित कैलोरी" if is_hi else "Estimated Calories", min_value=50, max_value=1500),
            "Key Nutrients": st.column_config.TextColumn("प्रमुख पोषक तत्व" if is_hi else "Nutritional Highlights")
        }
    )

    # Save to database and CSV Export
    btn_col1, btn_col2 = st.columns([1, 1])

    with btn_col1:
        if st.button(t("btn_save_diet"), use_container_width=True):
            # Format row data into columns required by diet_plans table
            b_text = ""
            l_text = ""
            d_text = ""
            s_text = ""
            for _, r in edited_df.iterrows():
                m_type = str(r.get("Meal", "")).lower()
                desc = f"{r.get('Items')} ({r.get('Calories (kcal)')} kcal)"
                if "breakfast" in m_type:
                    b_text = desc
                elif "lunch" in m_type:
                    l_text = desc
                elif "dinner" in m_type:
                    d_text = desc
                else:
                    s_text = desc

            record = {
                "user_id": user_id,
                "goal": goal,
                "target_calories": adjusted_target,
                "breakfast": b_text or "Custom Breakfast",
                "lunch": l_text or "Custom Lunch",
                "dinner": d_text or "Custom Dinner",
                "snacks": s_text or "Custom Snack",
                "is_editable": True,
                "created_at": datetime.now().isoformat()
            }
            try:
                insert_data("diet_plans", record)
                st.success("🎉 डाइट प्लान आपकी प्रोफ़ाइल में सफलतापूर्वक सुरक्षित हो गया!" if is_hi else "🎉 Diet plan successfully saved to your profile!")
            except Exception as e:
                st.error(f"योजना सहेजने में विफल: {e}" if is_hi else f"Failed to save plan: {e}")

    with btn_col2:
        csv_data = edited_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=t("btn_export_csv"),
            data=csv_data,
            file_name=f"MediGuardian_DietPlan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Previously saved diet plans
    st.divider()
    st.markdown(f"### {t('saved_plans_title')}")
    saved_plans = select_data("diet_plans", user_id=user_id, order_by="created_at", ascending=False)
    if saved_plans:
        for p in saved_plans[:3]:
            plan_date = str(p.get('created_at', ''))[:10]
            plan_goal = p.get('goal', 'Custom')
            expander_title = f"योजना दिनांक {plan_date} - लक्ष्य: {plan_goal}" if is_hi else f"Plan created on {plan_date} - Goal: {plan_goal}"
            with st.expander(expander_title):
                st.write(f"**{'लक्षित ऊर्जा' if is_hi else 'Target Energy'}:** {p.get('target_calories')} kcal")
                st.write(f"- **{'नाश्ता (Breakfast)' if is_hi else 'Breakfast'}:** {p.get('breakfast')}")
                st.write(f"- **{'दोपहर का भोजन (Lunch)' if is_hi else 'Lunch'}:** {p.get('lunch')}")
                st.write(f"- **{'नाश्ता/स्नैक्स (Snacks)' if is_hi else 'Snacks'}:** {p.get('snacks')}")
                st.write(f"- **{'रात का खाना (Dinner)' if is_hi else 'Dinner'}:** {p.get('dinner')}")
    else:
        st.info("कोई पूर्व डाइट प्लान नहीं मिला। अपना पहला मेनू सुरक्षित करने के लिए ऊपर 'डाइट प्लान सुरक्षित करें' पर क्लिक करें।" if is_hi else "No previously saved diet plans found. Click 'Save Diet Plan' above to save your first menu.")
