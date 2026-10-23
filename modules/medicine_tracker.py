"""
Medicine Adherence, Expiry Sentinel & Daily Wellness Module for MediGuardian AI
Tracks medication schedules, alerts for expiring batches, records intake logs, and logs daily lifestyle biomarkers.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 102 (Ambulance) or 112.
"""

from datetime import datetime, date, time, timedelta
import streamlit as st
import pandas as pd

from utils.supabase_client import insert_data, select_data, update_data, delete_data
from utils.translations import t, get_current_language


def check_and_trigger_reminders(medicines: list, is_hi: bool):
    """
    Checks if current local time is within 30 minutes of any scheduled medication time.
    Triggers Streamlit toast notifications.
    """
    now = datetime.now()
    now_time = now.time()
    now_minutes = now_time.hour * 60 + now_time.minute

    period_names = {
        "Morning": "सुबह (Morning)" if is_hi else "Morning",
        "Afternoon": "दोपहर (Afternoon)" if is_hi else "Afternoon",
        "Evening": "शाम (Evening)" if is_hi else "Evening",
        "Night": "रात (Night)" if is_hi else "Night"
    }

    for med in medicines:
        if not med.get("is_active", True):
            continue
        med_name = med.get("medicine_name", "Medication")

        schedules = [
            ("Morning", med.get("schedule_morning")),
            ("Afternoon", med.get("schedule_afternoon")),
            ("Evening", med.get("schedule_evening")),
            ("Night", med.get("schedule_night"))
        ]

        for period, t_val in schedules:
            if t_val:
                try:
                    parts = str(t_val).split(":")
                    h = int(parts[0])
                    m = int(parts[1]) if len(parts) > 1 else 0
                    sched_minutes = h * 60 + m
                    diff = abs(now_minutes - sched_minutes)
                    if diff <= 30:
                        p_label = period_names.get(period, period)
                        toast_msg = f"🔔 {'दवा अनुस्मारक: समय हो गया है' if is_hi else 'Dose Reminder: Time for'} **{med_name}** ({p_label} {t_val})!"
                        st.toast(toast_msg, icon="💊")
                except Exception:
                    pass


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    st.markdown(f"## {t('med_title')}")
    st.caption(t("med_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # Fetch active medicines
    medicines = select_data("medicines", user_id=user_id, order_by="created_at", ascending=False)

    # Check for schedule reminders
    check_and_trigger_reminders(medicines, is_hi)

    tab_meds, tab_daily, tab_history = st.tabs([
        t("tab_active_meds"),
        t("tab_daily_log"),
        t("tab_adherence_history")
    ])

    # ---------------- TAB 1: MEDICINES & INVENTORY ----------------
    with tab_meds:
        # 1. Add Medicine Form
        with st.expander(t("add_med_title"), expanded=False):
            with st.form("add_med_form", clear_on_submit=True):
                col_m1, col_m2 = st.columns([2, 1])
                with col_m1:
                    med_name = st.text_input(
                        t("med_name_label"),
                        placeholder="उदा. Metformin 500mg, Atorvastatin 10mg" if is_hi else "e.g. Metformin 500mg, Atorvastatin 10mg"
                    )
                    batch_id = st.text_input(
                        t("batch_id_label"),
                        placeholder="उदा. BT-2024-91" if is_hi else "e.g. BT-2024-91"
                    )
                with col_m2:
                    qty = st.number_input(t("pills_remaining"), min_value=1, max_value=500, value=30, step=5)
                    exp_date = st.date_input(t("expiry_date_label"), value=date.today() + timedelta(days=180))

                st.markdown("**" + ("खुराक समय सारणी:" if is_hi else "Dose Schedule Timings:") + "**")
                sc1, sc2, sc3, sc4 = st.columns(4)
                with sc1:
                    has_morning = st.checkbox("सुबह (Morning)" if is_hi else "Morning", value=True)
                    t_morning = st.time_input("सुबह का समय" if is_hi else "Morning Time", value=time(9, 0)) if has_morning else None
                with sc2:
                    has_noon = st.checkbox("दोपहर (Afternoon)" if is_hi else "Afternoon", value=False)
                    t_noon = st.time_input("दोपहर का समय" if is_hi else "Afternoon Time", value=time(13, 0)) if has_noon else None
                with sc3:
                    has_evening = st.checkbox("शाम (Evening)" if is_hi else "Evening", value=False)
                    t_eve = st.time_input("शाम का समय" if is_hi else "Evening Time", value=time(18, 0)) if has_evening else None
                with sc4:
                    has_night = st.checkbox("रात (Night)" if is_hi else "Night", value=True)
                    t_night = st.time_input("रात का समय" if is_hi else "Night Time", value=time(21, 0)) if has_night else None

                btn_add_med = st.form_submit_button(t("btn_save_med"), type="primary")

                if btn_add_med:
                    if not med_name.strip():
                        st.error("कृपया एक मान्य दवा का नाम दर्ज करें।" if is_hi else "Please enter a valid medication name.")
                    else:
                        payload = {
                            "user_id": user_id,
                            "medicine_name": med_name.strip(),
                            "batch_id": batch_id.strip() if batch_id else None,
                            "schedule_morning": t_morning.strftime("%H:%M:%S") if t_morning else None,
                            "schedule_afternoon": t_noon.strftime("%H:%M:%S") if t_noon else None,
                            "schedule_evening": t_eve.strftime("%H:%M:%S") if t_eve else None,
                            "schedule_night": t_night.strftime("%H:%M:%S") if t_night else None,
                            "expiry_date": exp_date.isoformat(),
                            "quantity_left": int(qty),
                            "is_active": True,
                            "created_at": datetime.now().isoformat()
                        }
                        try:
                            insert_data("medicines", payload)
                            st.success(f"{med_name} {'सक्रिय दवाइयों में जोड़ी गई।' if is_hi else 'added to active medications.'}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"{'दवा जोड़ने में विफल' if is_hi else 'Failed to add medicine'}: {e}")

        st.markdown(f"### {t('inventory_sentinel_title')}")

        if medicines:
            today = date.today()

            for med in medicines:
                med_id = med.get("id")
                name = med.get("medicine_name", "Unknown Medicine")
                qty = int(med.get("quantity_left") or 0)
                exp_str = str(med.get("expiry_date", ""))[:10]

                # Parse expiry date
                is_expired = False
                days_left = 999
                try:
                    exp_d = datetime.strptime(exp_str, "%Y-%m-%d").date()
                    days_left = (exp_d - today).days
                    is_expired = days_left < 0
                except Exception:
                    pass

                # Expiry status card
                if is_expired:
                    border_color = "#ef4444"
                    badge_bg = "#fee2e2"
                    badge_text = f"🚨 समाप्त / EXPIRED ({abs(days_left)} {'दिन पहले' if is_hi else 'days ago'}) - {'सेवन न करें' if is_hi else 'DO NOT CONSUME'}"
                    badge_color = "#b91c1c"
                elif days_left <= 30:
                    border_color = "#f59e0b"
                    badge_bg = "#fef3c7"
                    badge_text = f"⚠️ जल्द समाप्त होने वाली ({days_left} {'दिन शेष' if is_hi else 'days left'}) - {'नई दवा लें' if is_hi else 'Refill advised'}"
                    badge_color = "#b45309"
                else:
                    border_color = "#10b981"
                    badge_bg = "#d1fae5"
                    badge_text = f"✅ {'मान्य तिथि' if is_hi else 'Valid until'} {exp_str} ({days_left} {'दिन शेष' if is_hi else 'days left'})"
                    badge_color = "#047857"

                m_lbl = "सुबह" if is_hi else "Morning"
                a_lbl = "दोपहर" if is_hi else "Afternoon"
                e_lbl = "शाम" if is_hi else "Evening"
                n_lbl = "रात" if is_hi else "Night"

                sched_str = " ".join(filter(None, [
                    f"{m_lbl}: {med.get('schedule_morning')[:5]}" if med.get('schedule_morning') else "",
                    f"{a_lbl}: {med.get('schedule_afternoon')[:5]}" if med.get('schedule_afternoon') else "",
                    f"{e_lbl}: {med.get('schedule_evening')[:5]}" if med.get('schedule_evening') else "",
                    f"{n_lbl}: {med.get('schedule_night')[:5]}" if med.get('schedule_night') else ""
                ])) or ("लचीला (Flexible)" if is_hi else "Flexible")

                batch_label = "बैच (Batch)" if is_hi else "Batch"
                stock_label = "बचा हुआ स्टॉक" if is_hi else "Remaining Stock"
                sched_label = "समय सारणी" if is_hi else "Schedule"
                pills_unit = "गोलियां" if is_hi else "pills"

                card_html = (
                    f'<div style="border-left: 6px solid {border_color}; background-color: #f8fafc; border-radius: 6px; padding: 14px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">'
                    f'<span style="font-size: 17px; font-weight: bold; color: #1e293b;">{name}</span>'
                    f'<span style="background-color: {badge_bg}; color: {badge_color}; padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 600;">{badge_text}</span>'
                    f'</div>'
                    f'<div style="font-size: 14px; color: #475569;">'
                    f'<strong>{batch_label}:</strong> {med.get("batch_id") or "N/A"} &nbsp;|&nbsp; '
                    f'<strong>{stock_label}:</strong> <span style="font-weight: bold; color: {"#dc2626" if qty < 5 else "#0f172a"};">{qty} {pills_unit}</span> &nbsp;|&nbsp; '
                    f'<strong>{sched_label}:</strong> {sched_str}'
                    f'</div></div>'
                )

                with st.container():
                    st.markdown(card_html, unsafe_allow_html=True)

                    btn_c1, btn_c2, btn_c3 = st.columns([1.5, 1, 2])
                    with btn_c1:
                        if st.button(t("btn_mark_taken"), key=f"take_{med_id}", type="primary"):
                            # 1. Log in intake_logs
                            intake_payload = {
                                "medicine_id": med_id,
                                "user_id": user_id,
                                "scheduled_time": datetime.now().isoformat(),
                                "taken_time": datetime.now().isoformat(),
                                "status": "TAKEN",
                                "created_at": datetime.now().isoformat()
                            }
                            insert_data("intake_logs", intake_payload)

                            # 2. Decrement quantity left
                            new_qty = max(0, qty - 1)
                            update_data("medicines", "id", med_id, {"quantity_left": new_qty})
                            st.success(f"{name} {'की खुराक दर्ज की गई। शेष स्टॉक:' if is_hi else 'dose recorded. Remaining inventory:'} {new_qty} {pills_unit}.")
                            st.rerun()

                    with btn_c2:
                        btn_del_label = "🗑️ हटाएं" if is_hi else "🗑️ Remove"
                        if st.button(btn_del_label, key=f"del_{med_id}", type="secondary"):
                            delete_data("medicines", "id", med_id)
                            st.success(f"{name} {'हटा दी गई।' if is_hi else 'removed.'}")
                            st.rerun()

                    st.write("")
        else:
            st.info("कोई दवा पंजीकृत नहीं है। अपनी दवाएं ट्रैक करने के लिए ऊपर 'नई दवा शेड्यूल में जोड़ें' पर क्लिक करें।" if is_hi else "No medications registered. Click 'Add New Medication to Schedule' above to track your prescriptions.")

    # ---------------- TAB 2: DAILY HEALTH LOG ----------------
    with tab_daily:
        st.markdown("### 💧 " + ("दैनिक जीवनशैली एवं स्वास्थ्य मार्कर दर्ज करें" if is_hi else "Log Daily Lifestyle & Well-being Biomarkers"))
        st.caption("स्वास्थ्य के सूक्ष्म पैटर्न समझने हेतु पानी का सेवन, नींद की अवधि, व्यायाम और लक्षणों को दर्ज करें।" if is_hi else "Record water consumption, sleep duration, exercise, and symptoms to surface subtle wellness patterns.")

        with st.form("daily_health_form"):
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                water_liters = st.number_input("पानी का सेवन (लीटर)" if is_hi else "Water Intake (Liters)", min_value=0.0, max_value=10.0, value=2.5, step=0.25)
                sleep_hours = st.number_input("नींद की अवधि (घंटे)" if is_hi else "Sleep Duration (Hours)", min_value=0.0, max_value=20.0, value=7.5, step=0.5)
            with col_d2:
                exercise_min = st.number_input("व्यायाम / चलना (मिनट)" if is_hi else "Exercise / Walking (Minutes)", min_value=0, max_value=300, value=30, step=5)
                mood_options = (
                    ["उत्साही (Energetic)", "शांत (Calm)", "सामान्य (Neutral)", "थका हुआ (Tired / Fatigued)", "तनावग्रस्त (Stressed / Anxious)"]
                    if is_hi else
                    ["Energetic", "Calm", "Neutral", "Tired / Fatigued", "Stressed / Anxious"]
                )
                mood = st.selectbox("मनःस्थिति / ऊर्जा स्तर" if is_hi else "General Mood / Energy", mood_options)
            with col_d3:
                symptoms = st.text_input(
                    "लक्षण (यदि कोई हों)" if is_hi else "Symptoms (if any)",
                    placeholder="उदा. हल्का सिरदर्द, एसिडिटी, कोई नहीं" if is_hi else "e.g. Mild headache, Acidity, None"
                )
                log_date_val = st.date_input("प्रविष्टि दिनांक" if is_hi else "Date of Entry", value=date.today())

            submit_daily = st.form_submit_button(
                "दैनिक स्वास्थ्य लॉग दर्ज करें" if is_hi else "Record Daily Health Log",
                type="primary",
                use_container_width=True
            )

            if submit_daily:
                daily_payload = {
                    "user_id": user_id,
                    "log_date": log_date_val.isoformat(),
                    "water_liters": float(water_liters),
                    "sleep_hours": float(sleep_hours),
                    "exercise_min": int(exercise_min),
                    "symptoms": symptoms.strip() if symptoms else ("कोई नहीं" if is_hi else "None"),
                    "mood": mood,
                    "created_at": datetime.now().isoformat()
                }
                try:
                    insert_data("daily_health_logs", daily_payload)
                    st.success("✅ दैनिक स्वास्थ्य बायोमार्कर सफलतापूर्वक दर्ज किए गए!" if is_hi else "✅ Daily wellness biomarkers successfully recorded!")
                except Exception as e:
                    st.error(f"{'दैनिक लॉग दर्ज करने में विफल' if is_hi else 'Failed to record daily log'}: {e}")

        # Show recent daily logs
        st.divider()
        st.markdown("#### 📅 " + ("हालिया दैनिक स्वास्थ्य लॉग" if is_hi else "Recent Daily Health Logs"))
        daily_logs = select_data("daily_health_logs", user_id=user_id, order_by="created_at", ascending=False, limit=7)
        if daily_logs:
            df_daily = pd.DataFrame(daily_logs)
            cols_to_show = ["log_date", "water_liters", "sleep_hours", "exercise_min", "mood", "symptoms"]
            available_cols = [c for c in cols_to_show if c in df_daily.columns]
            st.dataframe(df_daily[available_cols], use_container_width=True)
        else:
            st.info("अभी कोई दैनिक लॉग दर्ज नहीं हैं।" if is_hi else "No daily logs recorded yet.")

    # ---------------- TAB 3: ADHERENCE & INTAKE HISTORY ----------------
    with tab_history:
        st.markdown("### 📊 " + ("दवा सेवन इतिहास" if is_hi else "Medication Intake History"))
        intake_logs = select_data("intake_logs", user_id=user_id, order_by="created_at", ascending=False)
        if intake_logs:
            # Map medicine id to name
            med_map = {m.get("id"): m.get("medicine_name") for m in medicines}
            display_intake = []
            for item in intake_logs:
                m_name = med_map.get(item.get("medicine_id")) or ("दवा" if is_hi else "Medication")
                status_raw = item.get("status", "TAKEN")
                status_val = ("ली गई (TAKEN)" if is_hi and status_raw == "TAKEN" else status_raw)
                display_intake.append({
                    "दवा (Medicine)" if is_hi else "Medicine": m_name,
                    "स्थिति (Status)" if is_hi else "Status": status_val,
                    "दर्ज समय (Logged Time)" if is_hi else "Logged Time": str(item.get("taken_time") or item.get("created_at", ""))[:19].replace("T", " ")
                })
            st.dataframe(pd.DataFrame(display_intake), use_container_width=True)
        else:
            st.info("अभी कोई सेवन इतिहास दर्ज नहीं है। जब आप कोई दवा लें, तो पहले टैब में 'खुराक ले ली' पर क्लिक करें।" if is_hi else "No intake history recorded yet. When you take a medication, click 'Mark Dose as Taken' in Tab 1.")
