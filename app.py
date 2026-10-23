"""
MediGuardian AI - Smart Preventive Healthcare, Nutrition & Emergency Awareness Platform
Single-framework Streamlit application with Supabase integration and offline session_state fallback.

GOAL: Educational wellness app, NOT a diagnostic tool.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

import os
from datetime import datetime, date, timedelta
import streamlit as st

# Safe environment loading
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Core configuration
st.set_page_config(
    page_title="MediGuardian AI - Smart Preventive Healthcare",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Medical Aesthetic Styling (Clean Blue / White Theme with Glassmorphism & Animations)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    :root {
        --primary-blue: #2563eb;
        --primary-hover: #1d4ed8;
        --soft-blue: #eff6ff;
        --border-color: #e2e8f0;
    }
    .main .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
    }
    /* Medical Top Alert Banner with Pulse Animation */
    @keyframes subtlePulse {
        0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
        100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }
    .emergency-top-bar {
        background: linear-gradient(135deg, #b91c1c 0%, #dc2626 50%, #ef4444 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 10px;
        text-align: center;
        font-weight: 700;
        font-size: 15px;
        letter-spacing: 0.3px;
        margin-bottom: 16px;
        animation: subtlePulse 2.5s infinite;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }
    .emergency-top-bar a {
        background: #ffffff;
        color: #b91c1c !important;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 13.5px;
        text-decoration: none !important;
        transition: transform 0.15s ease, background 0.15s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.12);
    }
    .emergency-top-bar a:hover {
        transform: scale(1.05);
        background: #fef08a;
    }
    /* Universal Footer */
    .mediguardian-footer {
        border-top: 1px solid #e2e8f0;
        margin-top: 45px;
        padding-top: 20px;
        text-align: center;
        color: #64748b;
        font-size: 13px;
    }
    /* Metric Cards Glassmorphism */
    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px -2px rgba(0,0,0,0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px -4px rgba(37,99,235,0.08);
        border-color: #bfdbfe;
    }
</style>
""", unsafe_allow_html=True)

# Imports of modules and utilities
from utils.supabase_client import (
    get_supabase,
    is_using_supabase,
    init_local_db,
    get_or_create_user,
    select_data,
    update_data,
    insert_data,
    test_supabase_connection,
    save_supabase_credentials
)
from utils.calculations import calculate_bmr, calculate_tdee

# Module routing
from modules import (
    dashboard,
    calorie_tracker,
    diet_planner,
    heart_health,
    emergency_assistant,
    cpr_learning,
    report_analyzer,
    medicine_tracker
)
from utils.translations import t, get_current_language


def seed_mock_demo_data(user_id: str):
    """Seeds sample logs if local session DB is currently empty for an engaging first-run experience."""
    init_local_db()
    existing_nutr = select_data("nutrition_logs", user_id=user_id)
    if not existing_nutr:
        # Seed 3 days of nutrition
        today = date.today()
        sample_meals = [
            ("Breakfast", "Poha (Flattened Rice)", 150, 195, 3.8, 36.0, 4.2, 300, (today - timedelta(days=2)).isoformat()),
            ("Lunch", "Yellow Dal Tadka", 200, 232, 14.4, 30.2, 6.4, 250, (today - timedelta(days=2)).isoformat()),
            ("Dinner", "Roti / Chapati", 80, 211, 6.5, 37.6, 4.0, 200, (today - timedelta(days=2)).isoformat()),
            ("Breakfast", "Idli (Steamed)", 120, 70, 2.4, 14.4, 0.6, 250, (today - timedelta(days=1)).isoformat()),
            ("Lunch", "Rajma Masala (Kidney Beans)", 200, 280, 16.0, 44.0, 5.0, 300, (today - timedelta(days=1)).isoformat()),
            ("Dinner", "Khichdi (Moong Dal & Rice)", 250, 300, 11.2, 50.0, 6.2, 350, (today - timedelta(days=1)).isoformat()),
            ("Breakfast", "Besan Chilla (Gram Flour Pancake)", 150, 240, 11.2, 28.5, 9.0, 250, today.isoformat()),
            ("Lunch", "Palak Paneer", 200, 380, 20.0, 12.0, 28.0, 300, today.isoformat())
        ]
        for m, f, g, c, p, cb, ft, w, d in sample_meals:
            insert_data("nutrition_logs", {
                "user_id": user_id,
                "log_date": d,
                "meal_type": m,
                "food_name": f,
                "portion_grams": g,
                "calories": c,
                "protein_g": p,
                "carbs_g": cb,
                "fat_g": ft,
                "water_ml": w,
                "meal_time": "13:00:00",
                "created_at": f"{d}T13:00:00"
            })

    existing_heart = select_data("heart_logs", user_id=user_id)
    if not existing_heart:
        today = date.today()
        h_samples = [
            (122, 82, 72, 185.0, 92.0, 30, (today - timedelta(days=3)).isoformat()),
            (126, 84, 76, 190.0, 98.0, 25, (today - timedelta(days=2)).isoformat()),
            (118, 78, 68, 182.0, 90.0, 45, (today - timedelta(days=1)).isoformat()),
            (120, 80, 70, 184.0, 94.0, 35, today.isoformat())
        ]
        for s, d, hr, ch, gl, act, dt in h_samples:
            insert_data("heart_logs", {
                "user_id": user_id,
                "log_date": dt,
                "systolic": s,
                "diastolic": d,
                "resting_hr": hr,
                "cholesterol_total": ch,
                "blood_glucose": gl,
                "smoking": False,
                "activity_min": act,
                "notes": "Routine morning check",
                "created_at": f"{dt}T08:30:00"
            })

    existing_daily = select_data("daily_health_logs", user_id=user_id)
    if not existing_daily:
        today = date.today()
        d_samples = [
            (2.5, 7.5, 30, "None", "Energetic", (today - timedelta(days=3)).isoformat()),
            (2.0, 5.5, 15, "Mild headache", "Tired / Fatigued", (today - timedelta(days=2)).isoformat()),
            (2.8, 8.0, 45, "None", "Calm", (today - timedelta(days=1)).isoformat()),
            (2.4, 7.0, 30, "None", "Energetic", today.isoformat())
        ]
        for w, sl, ex, sym, mo, dt in d_samples:
            insert_data("daily_health_logs", {
                "user_id": user_id,
                "log_date": dt,
                "water_liters": w,
                "sleep_hours": sl,
                "exercise_min": ex,
                "symptoms": sym,
                "mood": mo,
                "created_at": f"{dt}T21:00:00"
            })

    existing_meds = select_data("medicines", user_id=user_id)
    if not existing_meds:
        insert_data("medicines", {
            "user_id": user_id,
            "medicine_name": "Metformin 500mg",
            "batch_id": "BT-2024-X1",
            "schedule_morning": "09:00:00",
            "schedule_night": "21:00:00",
            "expiry_date": (date.today() + timedelta(days=120)).isoformat(),
            "quantity_left": 28,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        })
        insert_data("medicines", {
            "user_id": user_id,
            "medicine_name": "Atorvastatin 10mg",
            "batch_id": "AT-552",
            "schedule_night": "21:30:00",
            "expiry_date": (date.today() + timedelta(days=20)).isoformat(),  # Expiring soon
            "quantity_left": 8,
            "is_active": True,
            "created_at": datetime.now().isoformat()
        })


def main():
    # Ensure active language in session state
    if "app_language" not in st.session_state:
        st.session_state["app_language"] = "English"

    # 1. Top Emergency Action Bar (Ambulance 102 / Emergency 112)
    st.markdown(f"""
    <div class="emergency-top-bar">
        <span>{t("emergency_bar_text")}</span>
        <a href="tel:102">{t("emergency_bar_dial")}</a>
    </div>
    """, unsafe_allow_html=True)

    # 2. Authentication & User Session Management
    init_local_db()

    # Check connection mode
    using_supabase = is_using_supabase()

    # User state in session
    if "current_user_email" not in st.session_state:
        st.session_state["current_user_email"] = "user@example.com"

    # Definition of Platform Modules (Canonical Keys)
    MODULE_DEFS = [
        ("dashboard", "nav_dashboard", "🏥", dashboard.show),
        ("calorie_tracker", "nav_calorie_tracker", "🥗", calorie_tracker.show),
        ("diet_planner", "nav_diet_planner", "📋", diet_planner.show),
        ("heart_health", "nav_heart_health", "❤️", heart_health.show),
        ("emergency_assistant", "nav_emergency_assistant", "🚨", emergency_assistant.show),
        ("cpr_learning", "nav_cpr_learning", "🫀", cpr_learning.show),
        ("report_analyzer", "nav_report_analyzer", "🔬", report_analyzer.show),
        ("medicine_tracker", "nav_medicine_tracker", "💊", medicine_tracker.show),
    ]

    # Legacy & Quick Action key normalization map
    KEY_MAP = {
        "Dashboard": "dashboard",
        "Calorie Tracker": "calorie_tracker",
        "Diet Planner": "diet_planner",
        "Heart Health": "heart_health",
        "Emergency Assistant": "emergency_assistant",
        "CPR Learning": "cpr_learning",
        "Report Analyzer": "report_analyzer",
        "Medicine Tracker": "medicine_tracker",
        "डैशबोर्ड": "dashboard",
        "कैलोरी ट्रैकर": "calorie_tracker",
        "डाइट प्लानर": "diet_planner",
        "हृदय स्वास्थ्य": "heart_health",
        "आपातकालीन सहायता": "emergency_assistant",
        "सीपीआर सीखें": "cpr_learning",
        "लैब रिपोर्ट विश्लेषक": "report_analyzer",
        "दवा ट्रैकर": "medicine_tracker",
    }

    # Handle external module switches from Quick Action launchpad tiles
    if "nav_choice" in st.session_state:
        req = st.session_state.pop("nav_choice")
        if req in KEY_MAP:
            st.session_state["active_module_key"] = KEY_MAP[req]
        elif any(req == k for (k, _, _, _) in MODULE_DEFS):
            st.session_state["active_module_key"] = req

    if "active_module_key" not in st.session_state:
        st.session_state["active_module_key"] = "dashboard"

    # Sidebar Header & Controls
    with st.sidebar:
        st.markdown("## 🏥 MediGuardian AI")
        st.caption(t("app_subtitle"))

        # Prominent Language Selector (English / हिंदी)
        cur_lang = st.session_state.get("app_language", "English")
        lang_idx = 0 if cur_lang == "English" else 1

        def on_lang_change():
            st.session_state["app_language"] = st.session_state.get("sidebar_language_toggle", "English")

        st.radio(
            f"🌐 {t('language_label')}",
            options=["English", "हिंदी"],
            index=lang_idx,
            horizontal=True,
            key="sidebar_language_toggle",
            on_change=on_lang_change
        )

        st.divider()

        # Database Status Badge
        if using_supabase:
            st.success(f"🟢 {t('connected_supabase')}", icon="⚡")
            with st.expander(f"⚙️ {t('supabase_settings')}"):
                st.caption(t("connected_notice"))
                if st.button(t("btn_disconnect"), use_container_width=True):
                    save_supabase_credentials("", "")
                    st.rerun()
        else:
            st.warning(f"🟡 {t('offline_mode')}", icon="💾")
            with st.expander(t("connect_supabase_title"), expanded=False):
                st.caption(t("connect_supabase_desc"))
                supa_url_input = st.text_input(t("project_url"), placeholder="https://yourproject.supabase.co", key="cfg_supa_url")
                supa_key_input = st.text_input(t("anon_key"), type="password", placeholder="eyJhbGciOi...", key="cfg_supa_key")

                if st.button(t("btn_connect_supabase"), type="primary", use_container_width=True):
                    if not supa_url_input or not supa_key_input:
                        st.error("Please enter both Supabase URL and Anon Key.")
                    else:
                        with st.spinner("Connecting to Supabase..."):
                            ok, msg = test_supabase_connection(supa_url_input, supa_key_input)
                            if ok:
                                save_supabase_credentials(supa_url_input, supa_key_input)
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

        st.divider()

        # User Authentication / Switch Profile
        with st.expander(t("profile_title"), expanded=False):
            email_input = st.text_input(t("profile_email"), value=st.session_state["current_user_email"])
            if email_input != st.session_state["current_user_email"]:
                st.session_state["current_user_email"] = email_input.strip().lower()
                st.rerun()

            # Retrieve or create profile
            user = get_or_create_user(st.session_state["current_user_email"])
            st.session_state["current_user_id"] = user["id"]

            st.write(f"**Name:** {user.get('name')}")
            col_u1, col_u2 = st.columns(2)
            with col_u1:
                u_age = st.number_input(t("age"), min_value=10, max_value=120, value=int(user.get("age") or 30))
                u_weight = st.number_input(t("weight"), min_value=30.0, max_value=250.0, value=float(user.get("weight_kg") or 65.0))
            with col_u2:
                u_gender = st.selectbox(t("gender"), ["Male", "Female", "Other"], index=0 if user.get("gender") == "Male" else 1)
                u_height = st.number_input(t("height"), min_value=100.0, max_value=250.0, value=float(user.get("height_cm") or 170.0))

            u_activity = st.selectbox(
                t("activity_level"),
                ["Sedentary", "Lightly active", "Moderately active", "Very active", "Super active"],
                index=2
            )
            u_diet = st.selectbox(
                t("diet_pref"),
                ["Vegetarian", "Non-Vegetarian", "Eggetarian", "Vegan"],
                index=0 if "veg" in str(user.get("dietary_preference", "")).lower() else 1
            )

            if st.button(t("btn_update_profile"), use_container_width=True):
                update_data("users", "id", user["id"], {
                    "age": u_age,
                    "weight_kg": u_weight,
                    "height_cm": u_height,
                    "gender": u_gender,
                    "activity_level": u_activity,
                    "dietary_preference": u_diet
                })
                st.success(t("profile_updated"))
                st.rerun()

        # Ensure user_id is ready
        user = get_or_create_user(st.session_state["current_user_email"])
        user_id = user["id"]
        st.session_state["current_user_id"] = user_id

        # Seed initial demo records if new session
        seed_mock_demo_data(user_id)

        # 3. Main Bilingual Navigation
        st.markdown(f"### 🧭 {t('select_module')}")
        
        current_key = st.session_state["active_module_key"]
        keys_list = [k for (k, _, _, _) in MODULE_DEFS]
        current_idx = keys_list.index(current_key) if current_key in keys_list else 0

        nav_display_options = [f"{icon} {t(trans_key)}" for (k, trans_key, icon, _) in MODULE_DEFS]
        label_to_key = {f"{icon} {t(trans_key)}": k for (k, trans_key, icon, _) in MODULE_DEFS}

        def on_nav_change():
            sel = st.session_state.get("sidebar_nav_radio")
            if sel in label_to_key:
                st.session_state["active_module_key"] = label_to_key[sel]

        selected_label = st.radio(
            t("select_module"),
            nav_display_options,
            index=current_idx,
            key="sidebar_nav_radio",
            on_change=on_nav_change,
            label_visibility="collapsed"
        )
        st.session_state["active_module_key"] = label_to_key.get(selected_label, "dashboard")
        active_key = st.session_state["active_module_key"]

        st.divider()

        # Prominent Emergency Call Button in Sidebar (Ambulance 102)
        st.link_button(
            t("emergency_ambulance_btn"),
            "tel:102",
            type="primary",
            use_container_width=True,
            help="Direct national emergency ambulance dispatch in India (102)."
        )

        st.caption(t("emergency_subtext"))

    # 4. Routing to Selected Module
    active_func = next((func for (k, _, _, func) in MODULE_DEFS if k == active_key), dashboard.show)
    try:
        active_func(user_id)
    except Exception as e:
        st.error(f"An unexpected error occurred in module '{active_key}': {e}")
        st.info("The application caught the issue safely. Please retry or navigate to another module.")

    # 5. Mandatory Universal Footer Disclaimer
    st.markdown(f"""
    <div class="mediguardian-footer">
        <p><strong>{t("disclaimer")}</strong></p>
        <p>{t("footer_copyright")}</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
