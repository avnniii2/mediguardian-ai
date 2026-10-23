"""
Emergency Assistant & Rapid First-Response Module for MediGuardian AI
CRITICAL SAFETY MODULE - STRICTLY ZERO AI / ZERO EXTERNAL API DEPENDENCY.
Instant triage checklist, direct dial 112 link, and browser GPS coordinates locator.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

import streamlit as st
import streamlit.components.v1 as components
from utils.translations import t, get_current_language


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    # High-impact Emergency Header Banner
    st.markdown(f"""
    <div style="background-color: #fee2e2; border: 2px solid #ef4444; border-radius: 10px; padding: 18px; margin-bottom: 20px;">
        <h2 style="color: #b91c1c; margin: 0 0 8px 0;">{t("emergency_title")}</h2>
        <p style="color: #7f1d1d; font-size: 16px; font-weight: 600; margin: 0;">
            {t("emergency_banner_sub")}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Universal Medical Disclaimer
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    # Primary Action Buttons
    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1, 1])

    with c_btn1:
        st.link_button(
            t("btn_call_102"),
            "tel:102",
            type="primary",
            use_container_width=True,
            help="Directly dials 102 National Ambulance Emergency Service in India."
        )

    with c_btn2:
        st.link_button(
            t("btn_call_112"),
            "tel:112",
            use_container_width=True,
            help="Dials 112 National Unified Emergency Service."
        )

    with c_btn3:
        st.link_button(
            t("btn_call_1075"),
            "tel:1075",
            use_container_width=True,
            help="National Health Portal Helpline India."
        )

    st.divider()

    # Interactive Emergency Tools: SOS Audio Siren & GPS Dispatcher
    col_siren, col_gps = st.columns([1, 1.2], gap="medium")

    with col_siren:
        st.markdown(f"### {t('siren_title')}")
        st.caption(t("siren_desc"))

        btn_sound_txt = "🔊 " + ("आपातकालीन सायरन बजाएं" if is_hi else "SOUND EMERGENCY SIREN")
        btn_stop_txt = "⏹️ " + ("सायरन बंद करें" if is_hi else "STOP SIREN")
        status_off_txt = "सायरन बंद है। अलार्म बजाने के लिए क्लिक करें।" if is_hi else "Siren is off. Click to sound alarm."
        status_on_txt = "🚨 सायरन सक्रिय! उच्च तीव्रता का अलार्म बज रहा है।" if is_hi else "🚨 SIREN ACTIVE! Emitting high-decibel pulsing alarm."

        siren_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fff1f2; border: 2px solid #f43f5e; border-radius: 10px; padding: 16px; text-align: center;">
            <div id="siren-icon" style="font-size: 40px; margin-bottom: 8px; transition: transform 0.15s ease;">🚨</div>
            <button id="siren-btn" onclick="toggleSiren()" style="background-color: #e11d48; color: white; border: none; padding: 12px 24px; font-size: 15px; font-weight: bold; border-radius: 25px; cursor: pointer; box-shadow: 0 4px 6px -1px rgba(225,29,72,0.3);">
                {btn_sound_txt}
            </button>
            <p id="siren-status" style="font-size: 12px; color: #9f1239; margin-top: 10px; font-weight: 600;">{status_off_txt}</p>
        </div>

        <script>
        let sirenActive = false;
        let sirenAudioCtx = null;
        let sirenOsc = null;
        let sirenInterval = null;

        function toggleSiren() {{
            const btn = document.getElementById("siren-btn");
            const status = document.getElementById("siren-status");
            const icon = document.getElementById("siren-icon");

            if (!sirenActive) {{
                sirenActive = true;
                btn.innerHTML = "{btn_stop_txt}";
                btn.style.backgroundColor = "#1e293b";
                status.innerText = "{status_on_txt}";

                sirenAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
                let freq = 700;
                let direction = 1;

                sirenOsc = sirenAudioCtx.createOscillator();
                const gain = sirenAudioCtx.createGain();
                gain.gain.setValueAtTime(0.4, sirenAudioCtx.currentTime);

                sirenOsc.type = "sawtooth";
                sirenOsc.frequency.setValueAtTime(freq, sirenAudioCtx.currentTime);
                sirenOsc.connect(gain);
                gain.connect(sirenAudioCtx.destination);
                sirenOsc.start();

                sirenInterval = setInterval(() => {{
                    freq += 80 * direction;
                    if (freq > 1100) direction = -1;
                    if (freq < 600) direction = 1;
                    if (sirenOsc) {{
                        sirenOsc.frequency.setValueAtTime(freq, sirenAudioCtx.currentTime);
                    }}
                    icon.style.transform = (direction === 1) ? "scale(1.25)" : "scale(1.0)";
                }}, 50);
            }} else {{
                sirenActive = false;
                btn.innerHTML = "{btn_sound_txt}";
                btn.style.backgroundColor = "#e11d48";
                status.innerText = "{status_off_txt}";
                icon.style.transform = "scale(1.0)";

                if (sirenInterval) clearInterval(sirenInterval);
                if (sirenOsc) {{
                    sirenOsc.stop();
                    sirenOsc.disconnect();
                }}
            }}
        }}
        </script>
        """
        components.html(siren_html, height=190)

    with col_gps:
        # Browser GPS Location Finder & WhatsApp Dispatcher
        st.markdown(f"### {t('gps_title')}")
        st.caption(t("gps_desc"))

        btn_gps_txt = t("btn_locate_gps")
        gps_init_txt = "स्थान अभी प्राप्त नहीं किया गया। 102/112 को भेजने के लिए ऊपर क्लिक करें।" if is_hi else "Location not requested yet. Click button above when ready to share with 102/112 dispatch."
        gps_loading_txt = "⏳ जीपीएस निर्देशांक प्राप्त हो रहे हैं..." if is_hi else "⏳ Retrieving accurate GPS coordinates from device..."
        maps_btn_txt = "🗺️ गूगल मैप्स खोलें" if is_hi else "🗺️ Open Google Maps"
        wa_btn_txt = "📲 व्हाट्सएप पर भेजें" if is_hi else "📲 Send Location via WhatsApp"
        wa_emergency_txt = "🚨 मेडिकल इमरजेंसी! मुझे तुरंत एम्बुलेंस सहायता चाहिए। मेरी लाइव जीपीएस स्थिति है:" if is_hi else "🚨 MEDICAL EMERGENCY! I need immediate ambulance assistance. My current GPS location is:"

        location_html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 16px;">
            <button onclick="getLocation()" style="background-color: #dc2626; color: white; border: none; padding: 10px 18px; font-size: 14px; font-weight: bold; border-radius: 6px; cursor: pointer;">
                {btn_gps_txt}
            </button>
            <div id="location-result" style="margin-top: 10px; font-size: 13.5px; color: #1e293b;">
                {gps_init_txt}
            </div>
        </div>

        <script>
        function getLocation() {{
            const out = document.getElementById("location-result");
            if (navigator.geolocation) {{
                out.innerHTML = "{gps_loading_txt}";
                navigator.geolocation.getCurrentPosition(showPosition, showError, {{
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }});
            }} else {{
                out.innerHTML = "❌ Geolocation is not supported by this browser.";
            }}
        }}

        function showPosition(position) {{
            const lat = position.coords.latitude.toFixed(6);
            const lon = position.coords.longitude.toFixed(6);
            const acc = position.coords.accuracy.toFixed(1);
            const mapsUrl = `https://www.google.com/maps?q=${{lat}},${{lon}}`;
            const waMsg = encodeURIComponent(`{wa_emergency_txt} ${{mapsUrl}} (~${{acc}}m accuracy). Please call 102 or dispatch help!`);
            const waUrl = `https://api.whatsapp.com/send?text=${{waMsg}}`;
            
            const out = document.getElementById("location-result");
            out.innerHTML = `
                <div style="background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 10px; margin-top: 8px; border-radius: 4px;">
                    <p style="margin: 0 0 6px 0;"><strong>Coordinates:</strong> ${{lat}}, ${{lon}} (~${{acc}}m accuracy)</p>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 6px;">
                        <a href="${{mapsUrl}}" target="_blank" style="background: #2563eb; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: bold;">{maps_btn_txt}</a>
                        <a href="${{waUrl}}" target="_blank" style="background: #22c55e; color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: bold;">{wa_btn_txt}</a>
                    </div>
                </div>
            `;
        }}

        function showError(error) {{
            const out = document.getElementById("location-result");
            switch(error.code) {{
                case error.PERMISSION_DENIED:
                    out.innerHTML = "⚠️ Location permission denied by user. Please enable browser location permissions.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    out.innerHTML = "⚠️ Location information is temporarily unavailable.";
                    break;
                case error.TIMEOUT:
                    out.innerHTML = "⚠️ Location request timed out. Please try again.";
                    break;
                default:
                    out.innerHTML = "⚠️ An unknown error occurred while retrieving GPS.";
                    break;
            }}
        }}
        </script>
        """
        components.html(location_html, height=190)

    st.divider()

    # 2-Column Core Layout: Left Symptoms Checklist vs Right Immediate Actions
    col_sym, col_act = st.columns([1, 1], gap="large")

    with col_sym:
        st.markdown(f"### {t('symptoms_checklist_title')}")
        st.markdown("*लक्षणों की जांच करें:*" if is_hi else "*Check any symptoms currently observed in the individual:*")

        s1 = st.checkbox(t("sym_chest_pain"))
        s2 = st.checkbox(t("sym_radiating_pain"))
        s3 = st.checkbox(t("sym_shortness_breath"))
        s4 = st.checkbox(t("sym_cold_sweats"))
        s5 = st.checkbox(t("sym_fast_stroke"))
        s6 = st.checkbox(t("sym_unresponsive"))

        checked_count = sum([s1, s2, s3, s4, s5, s6])
        if checked_count >= 1:
            st.error(
                f"🚨 **{checked_count} {t('sym_warning_checked')}**"
            )

    with col_act:
        st.markdown(f"### {t('immediate_actions_title')}")

        if is_hi:
            st.markdown("""
            1. **सबसे पहले 102 एम्बुलेंस पर कॉल करें:**
               आसपास के किसी व्यक्ति से कहें कि वह स्पीकरफ़ोन पर 102 (या 112) मिलाए और पीड़ित के साथ रहे।
            
            2. **तुरंत आराम से बैठ जाएं:**
               सभी प्रकार का चलना-फिरना या परिश्रम रोक दें। व्यक्ति को फर्श पर पीठ दीवार से टिकाकर घुटने मोड़कर बैठाएं (*W-पोजीशन*)। इससे हृदय पर दबाव कम होता है।
            
            3. **तंग कपड़े ढीले करें:**
               शर्ट के कॉलर, टाई, बेल्ट या तंग कपड़े तुरंत ढीले करें ताकि सांस लेने में आसानी हो।
            
            4. **स्वयं वाहन बिल्कुल न चलाएं:**
               मरीज को निजी वाहन से ले जाने या खुद गाड़ी चलाने का प्रयास न करें। एम्बुलेंस में ऑक्सीजन, डिफाइब्रिलेटर और प्रशिक्षित पैरामेडिक्स होते हैं।
            
            5. **एस्पिरिन की जानकारी (हार्ट अटैक की आशंका होने पर):**
               यदि वयस्क पूर्ण होश में है और उसे एस्पिरिन से एलर्जी या आंतरिक रक्तस्राव नहीं है, तो आपातकालीन दिशानिर्देश 300mg एस्पिरिन की एक घुलनशील गोली चबाने का सुझाव देते हैं।
            
            6. **प्रवेश द्वार खुला रखें:**
               घर या कार्यालय का मुख्य दरवाजा तुरंत खोल दें ताकि एम्बुलेंस कर्मी बिना देरी के अंदर आ सकें।
            """)
        else:
            st.markdown("""
            1. **DIAL 102 AMBULANCE FIRST:**
               Ask someone nearby to call 102 (or 112) immediately on speakerphone while staying with the individual.
            
            2. **REST & SIT DOWN IMMEDIATELY:**
               Stop all exertion. Have the person sit on the floor, leaning their back against a solid wall with knees bent (*W-position* / *Semi-Fowler's position*). This minimizes cardiac workload.
            
            3. **LOOSEN TIGHT ATTIRE:**
               Unbutton shirt collars, ties, tight belts, or restrictive clothing to ease pulmonary expansion.
            
            4. **NEVER DRIVE YOURSELF:**
               Do NOT attempt to drive yourself or the patient in a private vehicle if an ambulance is accessible. Emergency medical service (EMS) vehicles have defibrillators, oxygen, and trained paramedics on board.
            
            5. **ASPIRIN AWARENESS (If Suspected Heart Attack):**
               If the adult is fully conscious, not allergic to aspirin, and has no active internal bleeding or doctor contraindication, standard emergency guidelines recommend chewing one adult 300mg soluble Aspirin tablet.
            
            6. **PREPARE ENTRYWAY:**
               Unlock the main entrance door so paramedics can enter without delays.
            """)

    st.divider()

    # Rapid First-Aid Protocols Accordion
    st.markdown(f"### {t('rapid_first_aid_title')}")

    c_p1, c_p2 = st.columns(2)
    with c_p1:
        with st.expander(t("fast_stroke_title")):
            if is_hi:
                st.markdown("""
                - **F - Face (चेहरा):** व्यक्ति से मुस्कुराने को कहें। क्या चेहरे का एक हिस्सा लटक रहा है?
                - **A - Arms (भुजाएं):** व्यक्ति से दोनों हाथ ऊपर उठाने को कहें। क्या एक हाथ नीचे गिर रहा है?
                - **S - Speech (आवाज):** व्यक्ति से एक सरल वाक्य बोलने को कहें। क्या आवाज लड़खड़ा रही है?
                - **T - Time (समय):** इनमें से कोई भी लक्षण दिखने पर बिना देर किए 102 / 112 डायल करें।
                """)
            else:
                st.markdown("""
                - **F - Face:** Ask the person to smile. Does one side of the face droop?
                - **A - Arms:** Ask the person to raise both arms. Does one arm drift downward?
                - **S - Speech:** Ask the person to repeat a simple phrase. Is speech slurred or strange?
                - **T - Time to call 102/112:** If you observe any of these signs, call 102/112 immediately and note the exact time symptoms began.
                """)

        with c_p2:
            with st.expander(t("choking_title")):
                if is_hi:
                    st.markdown("""
                    - यदि व्यक्ति जोर से खांस पा रहा है, तो उसे खांसने के लिए प्रोत्साहित करें।
                    - यदि बोल या सांस नहीं ले पा रहा (गले को पकड़ना चोकिंग का सार्वभौमिक संकेत है):
                      1. व्यक्ति के पीछे खड़े हों, एक हाथ से छाती को सहारा दें और आगे की ओर झुकाएं।
                      2. दोनों कंधों के बीच हथेली के निचले हिस्से से **5 बार मजबूती से थपथपाएं (Back blows)**।
                      3. यदि फिर भी सांस न आए, तो नाभि के ठीक ऊपर **5 त्वरित पेट के झटके (Heimlich maneuver)** दें।
                      4. जब तक वस्तु बाहर न निकल जाए या एम्बुलेंस न आ जाए, चक्र जारी रखें।
                    """)
                else:
                    st.markdown("""
                    - If the person can cough forcibly, encourage coughing.
                    - If cannot speak or breathe (universal choking sign clutching neck):
                      1. Stand behind them, support their chest with one hand, and lean them forward.
                      2. Deliver up to **5 firm back blows** between shoulder blades with heel of hand.
                      3. If still blocked, perform **5 quick upward abdominal thrusts** (Heimlich maneuver).
                      4. Repeat cycle until object dislodges or emergency help arrives.
                    """)
