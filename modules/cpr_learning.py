"""
CPR & Resuscitation Learning Interactive Module for MediGuardian AI
Includes 5-step CPR guide, AED walkthrough, 110 BPM WebAudio metronome, and interactive knowledge quiz.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
from utils.translations import t, get_current_language


def show(user_id: str):
    is_hi = get_current_language() == "हिंदी"

    st.markdown(f"## {t('cpr_title')}")
    st.caption(t("cpr_subtitle"))

    # Educational Disclaimer Banner
    st.info(f"ℹ️ **{t('disclaimer')}**", icon="🛡️")

    tab_learn, tab_aed, tab_metronome, tab_quiz = st.tabs([
        t("tab_cpr_steps"),
        t("tab_aed_guide"),
        t("tab_metronome"),
        t("tab_quiz")
    ])

    # ---------------- TAB 1: 5-STEP CPR GUIDE ----------------
    with tab_learn:
        st.markdown("### 🖐️ Hands-Only CPR: 5 Critical Life-Saving Steps")
        st.markdown("""
        Sudden cardiac arrest is a time-critical emergency. Brain tissue begins experiencing irreversible damage 
        within **3 to 4 minutes** without blood circulation. Immediate bystander CPR can double or triple survival chances!
        """)

        # Illustration image from Unsplash (Medical / CPR training)
        st.image(
            "https://images.unsplash.com/photo-1516574187841-cb9cc2ca948b?auto=format&fit=crop&w=1200&q=80",
            caption="Cardiopulmonary Resuscitation (CPR) Training & Practice (Photo: Unsplash)",
            use_container_width=True
        )

        with st.expander("Step 1: Check Scene Safety & Responsiveness", expanded=True):
            st.markdown("""
            - **Assess Surroundings:** Ensure the scene is safe from traffic, electrical hazards, fire, or falling debris.
            - **Check Response:** Tap both shoulders firmly and shout loudly: *"Are you okay? Can you hear me?"*
            - **No response?** Immediately proceed to Step 2.
            """)

        with st.expander("Step 2: Call Ambulance 102 / Emergency 112 & Request an AED", expanded=True):
            st.markdown("""
            - **Call Ambulance 102 or 112 Immediately:** If someone is nearby, point directly at them: *"You in the red shirt, call 102 for an ambulance and bring an AED!"*
            - If you are alone, put your phone on speakerphone, dial 102/112, and start compressions while speaking to the dispatcher.
            """)

        with st.expander("Step 3: Check for Normal Breathing", expanded=False):
            st.markdown("""
            - Quickly look at the chest and face for **no more than 10 seconds**.
            - Look for chest rise and fall.
            - **Important:** Occasional gasping or snorting (known as *agonal gasps*) is NOT normal breathing—it is a reflex sign of cardiac arrest. Treat as unresponsive and not breathing.
            """)

        with st.expander("Step 4: High-Quality Chest Compressions (Hard & Fast)", expanded=True):
            st.markdown("""
            - **Hand Placement:** Place the heel of one hand in the center of the chest (lower half of the sternum). Place the other hand on top and interlock your fingers.
            - **Body Position:** Lock your elbows straight and position your shoulders directly above your hands.
            - **Compression Depth:** Push down firmly at least **5 to 6 cm (2 to 2.4 inches)** into the adult chest.
            - **Rate:** Compress at **100 to 120 compressions per minute** (approx 2 beats per second).
            - **Chest Recoil:** Allow the chest to return to its natural resting position between each push. Do not lean your body weight on the chest.
            """)

        with st.expander("Step 5: Continue Until Medical Help Arrives", expanded=False):
            st.markdown("""
            - **Bystander Hands-Only CPR:** Maintain continuous chest compressions without stopping.
            - Do not stop until:
              1. An AED arrives and is ready to analyze.
              2. Paramedics / Emergency responders take over.
              3. The person shows obvious signs of consciousness (movement, regular breathing, speaking).
              4. You are too physically exhausted to continue and can switch with another bystander.
            """)

    # ---------------- TAB 2: AED GUIDE ----------------
    with tab_aed:
        st.markdown("### ⚡ What is an Automated External Defibrillator (AED)?")
        st.markdown("""
        An **AED** is a lightweight, portable electronic device that diagnoses life-threatening cardiac arrhythmias 
        (such as Ventricular Fibrillation) and delivers an electrical shock (*defibrillation*) to help the heart re-establish an effective rhythm.
        """)

        st.image(
            "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?auto=format&fit=crop&w=1200&q=80",
            caption="Automated External Defibrillator (AED) in Public Spaces (Photo: Unsplash)",
            use_container_width=True
        )

        st.markdown("#### 🛠️ Step-by-Step Instructions to Use an AED:")
        st.markdown("""
        1. **Turn on the AED immediately:** Press the power button or simply open the lid (many models power on automatically).
        2. **Follow Spoken Voice Prompts:** The AED will speak clear step-by-step instructions in voice and on screen.
        3. **Expose the Bare Chest:** Tear or cut clothing if necessary. Wipe the chest dry if wet or sweaty.
        4. **Attach Adhesive Pads:**
           - Pad 1: Place on the patient's upper right chest, just below the collarbone.
           - Pad 2: Place on the patient's lower left chest, on the ribs below the armpit.
        5. **Plug in Pad Connector:** If not pre-connected, insert the pad cable into the flashing socket on the AED unit.
        6. **STAND CLEAR for Heart Rhythm Analysis:**
           - Shout: *"STAND CLEAR! NO ONE TOUCH THE PATIENT!"*
           - Ensure nobody is in physical contact with the patient while the machine analyzes the ECG rhythm.
        7. **Deliver Shock if Advised:**
           - If a shock is advised, ensure everyone remains clear, then press the flashing orange/red shock button.
           - (Fully automatic AEDs will give a warning countdown and shock automatically).
        8. **Resume Compressions Immediately:**
           - Right after the shock (or if no shock is advised), immediately resume chest compressions. Do not remove the pads.
        """)

    # ---------------- TAB 3: 110 BPM CPR METRONOME ----------------
    with tab_metronome:
        st.markdown("### 🎵 Interactive CPR Rhythm Metronome (110 BPM)")
        st.markdown("""
        The recommended compression rate is **100 to 120 beats per minute**. 
        110 BPM is the optimal midpoint. Use this audio-visual metronome to internalize the exact rhythm!
        
        *Tip: Famous songs matching this life-saving tempo include **"Stayin' Alive"** by the Bee Gees (103 BPM), 
        **"Baby Shark"** (115 BPM), and **"Crazy In Love"** by Beyoncé (110 BPM).*
        """)

        # Clean HTML5 Web Audio API Metronome (zero dependencies, works on any modern browser)
        metronome_html = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; background: #f0fdf4; border: 2px solid #22c55e; border-radius: 12px; padding: 20px; max-width: 600px; margin: 0 auto;">
            <div id="visual-heart" style="font-size: 60px; margin-bottom: 8px; transition: transform 0.08s ease;">🫀</div>
            <h2 style="color: #15803d; margin: 0 0 6px 0; font-size: 22px;">110 Beats Per Minute Metronome</h2>
            <p style="color: #166534; font-size: 13.5px; margin: 0 0 14px 0;">Optimal Target Cadence for Bystander Chest Compressions</p>
            
            <button id="toggle-btn" onclick="toggleMetronome()" style="background-color: #16a34a; color: white; border: none; padding: 12px 28px; font-size: 16px; font-weight: bold; border-radius: 30px; cursor: pointer; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                ▶️ Start 110 BPM Metronome
            </button>
            <p id="status-text" style="color: #4b5563; font-size: 13px; margin-top: 10px;">Audio is currently stopped.</p>
        </div>

        <script>
        let isRunning = false;
        let timer = null;
        let audioCtx = null;

        function playBeep() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = "sine";
            osc.frequency.setValueAtTime(880, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.08);

            const heart = document.getElementById("visual-heart");
            heart.style.transform = "scale(1.25)";
            setTimeout(() => { heart.style.transform = "scale(1.0)"; }, 90);
        }

        function toggleMetronome() {
            const btn = document.getElementById("toggle-btn");
            const status = document.getElementById("status-text");
            if (isRunning) {
                clearInterval(timer);
                isRunning = false;
                btn.innerHTML = "▶️ Start 110 BPM Metronome";
                btn.style.backgroundColor = "#16a34a";
                status.innerText = "Audio paused.";
            } else {
                isRunning = true;
                btn.innerHTML = "⏸️ Pause Metronome";
                btn.style.backgroundColor = "#dc2626";
                status.innerText = "Playing at 110 BPM (545ms interval). Practice pushing on each beat!";
                playBeep();
                timer = setInterval(playBeep, 545);
            }
        }
        </script>
        """
        components.html(metronome_html, height=230)

        st.divider()

        # Interactive CPR Tap-Pacing Simulator
        st.markdown(f"#### {t('cadence_trainer_title')}")
        st.caption(t("cadence_trainer_desc"))

        btn_tap_txt = t("btn_push_tap")
        feedback_init = "अपनी अनुमानित गति से 3-4 बार टैप करके बीपीएम मापें।" if is_hi else "Tap 3-4 times at your estimated CPR pace to measure your BPM."
        target_txt = "लक्ष्य: 100 से 120 कम्प्रेशन प्रति मिनट" if is_hi else "Target: 100 to 120 compressions per minute"

        tap_sim_html = """
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; text-align: center; background: #eff6ff; border: 2px solid #3b82f6; border-radius: 12px; padding: 22px; max-width: 600px; margin: 0 auto;">
            <button id="tap-btn" onclick="registerTap()" style="background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border: none; padding: 20px 40px; font-size: 20px; font-weight: bold; border-radius: 40px; cursor: pointer; box-shadow: 0 4px 12px rgba(37,99,235,0.3); transition: transform 0.08s ease;">
                __BTN_TAP_TXT__
            </button>
            <div id="tap-feedback" style="margin-top: 16px; font-size: 18px; font-weight: bold; color: #1e3a8a;">
                __FEEDBACK_INIT__
            </div>
            <div id="tap-bpm" style="margin-top: 6px; font-size: 28px; font-weight: 800; color: #2563eb;">
                -- BPM
            </div>
            <p style="font-size: 13px; color: #64748b; margin-top: 8px;">__TARGET_TXT__</p>
        </div>

        <script>
        let tapTimes = [];
        let tapTimer = null;

        function registerTap() {
            const now = Date.now();
            tapTimes.push(now);

            // Keep only last 5 taps
            if (tapTimes.length > 5) {
                tapTimes.shift();
            }

            const btn = document.getElementById("tap-btn");
            btn.style.transform = "scale(0.95)";
            setTimeout(() => { btn.style.transform = "scale(1.0)"; }, 80);

            if (tapTimes.length >= 2) {
                const intervals = [];
                for (let i = 1; i < tapTimes.length; i++) {
                    intervals.push(tapTimes[i] - tapTimes[i - 1]);
                }
                const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
                const bpm = Math.round(60000 / avgInterval);

                const fb = document.getElementById("tap-feedback");
                const bpmEl = document.getElementById("tap-bpm");
                bpmEl.innerText = bpm + " BPM";

                if (bpm >= 100 && bpm <= 120) {
                    fb.innerHTML = "🎉 <span style='color: #16a34a;'>PERFECT CADENCE! (" + bpm + " BPM) - Optimal organ perfusion!</span>";
                    btn.style.background = "linear-gradient(135deg, #16a34a, #15803d)";
                } else if (bpm < 100) {
                    fb.innerHTML = "⚠️ <span style='color: #d97706;'>PUSH FASTER! (Current: " + bpm + " BPM | Target: 100-120)</span>";
                    btn.style.background = "linear-gradient(135deg, #f59e0b, #d97706)";
                } else {
                    fb.innerHTML = "⚠️ <span style='color: #dc2626;'>SLOW DOWN SLIGHTLY! (Current: " + bpm + " BPM | Allow chest recoil)</span>";
                    btn.style.background = "linear-gradient(135deg, #ef4444, #dc2626)";
                }
            }

            clearTimeout(tapTimer);
            tapTimer = setTimeout(() => {
                tapTimes = [];
            }, 3000);
        }
        </script>
        """.replace("__BTN_TAP_TXT__", btn_tap_txt).replace("__FEEDBACK_INIT__", feedback_init).replace("__TARGET_TXT__", target_txt)
        components.html(tap_sim_html, height=260)

    # ---------------- TAB 4: QUIZ & CERTIFICATE ----------------
    with tab_quiz:
        st.markdown("### 🎯 CPR & Emergency First-Response Knowledge Quiz")
        st.caption("Test your readiness and earn an educational CPR Awareness Badge.")

        with st.form("cpr_quiz_form"):
            q1 = st.radio(
                "1. What is the recommended chest compression rate for an adult in cardiac arrest?",
                ["60 to 80 compressions per minute", "80 to 100 compressions per minute", "100 to 120 compressions per minute", "140 to 160 compressions per minute"],
                index=None
            )

            q2 = st.radio(
                "2. What is the correct compression depth for an adult chest during CPR?",
                ["At least 5 to 6 cm (2 to 2.4 inches)", "1 to 2 cm (0.5 inch)", "8 to 10 cm (4 inches)", "As shallow as possible to avoid hurting the ribs"],
                index=None
            )

            q3 = st.radio(
                "3. Before beginning CPR on an unresponsive person, what is the VERY FIRST action you must take?",
                ["Begin rescue breathing immediately", "Check the scene for danger/safety hazards", "Pour cold water on the person's face", "Try to stand them up"],
                index=None
            )

            q4 = st.radio(
                "4. If you are an untrained bystander witnessing a sudden collapse, what CPR technique is recommended by resuscitation councils?",
                ["Hands-Only CPR (continuous, uninterrupted chest compressions)", "Rescue breaths only without touching the chest", "Wait quietly for the ambulance without providing any physical aid", "Perform abdominal Heimlich thrusts"],
                index=None
            )

            q5 = st.radio(
                "5. What critical safety command must be shouted before an AED delivers an electrical shock?",
                ["'Hold the patient tightly!'", "'Stand clear! Nobody touch the patient!'", "'Start chest compressions immediately!'", "'Check the patient's pulse now!'"],
                index=None
            )

            quiz_submitted = st.form_submit_button("Submit Quiz Answers", type="primary")

        if quiz_submitted:
            score = 0
            feedback = []

            # Q1
            if q1 == "100 to 120 compressions per minute":
                score += 1
                feedback.append("✅ Q1 Correct: 100-120 BPM maintains vital organ perfusion.")
            else:
                feedback.append("❌ Q1 Incorrect: Target is 100 to 120 compressions per minute.")

            # Q2
            if q2 == "At least 5 to 6 cm (2 to 2.4 inches)":
                score += 1
                feedback.append("✅ Q2 Correct: 5 to 6 cm depth ensures sufficient ventricular ejection fraction.")
            else:
                feedback.append("❌ Q2 Incorrect: Recommended adult depth is 5 to 6 cm (2 to 2.4 inches).")

            # Q3
            if q3 == "Check the scene for danger/safety hazards":
                score += 1
                feedback.append("✅ Q3 Correct: Never become a second victim. Always ensure personal safety first.")
            else:
                feedback.append("❌ Q3 Incorrect: First assess scene safety before approaching.")

            # Q4
            if q4 == "Hands-Only CPR (continuous, uninterrupted chest compressions)":
                score += 1
                feedback.append("✅ Q4 Correct: Hands-Only CPR is standard and highly effective for untrained bystanders.")
            else:
                feedback.append("❌ Q4 Incorrect: Hands-Only CPR (push hard and fast) is strongly recommended.")

            # Q5
            if q5 == "'Stand clear! Nobody touch the patient!'":
                score += 1
                feedback.append("✅ Q5 Correct: Everyone must stand clear so current is not transferred to bystanders.")
            else:
                feedback.append("❌ Q5 Incorrect: Always ensure everyone stands completely clear before a shock.")

            st.divider()
            st.markdown(f"### 🏆 Quiz Results: **{score} / 5**")
            for fb in feedback:
                st.write(fb)

            if score >= 4:
                st.balloons()
                st.success("🎉 Excellent! You demonstrated strong awareness of life-saving CPR protocols.")

                cert_text = f"""
================================================================================
                    MEDIGUARDIAN AI - CERTIFICATE OF RECOGNITION
                           CPR & Resuscitation Awareness
================================================================================
This verifies that the learner has demonstrated foundational awareness of
Bystander Hands-Only Cardiopulmonary Resuscitation (CPR) and AED safety protocols
on {datetime.now().strftime('%B %d, %Y')}.

Achieved Score: {score}/5 Questions Correct
Topics Verified: 100-120 BPM Cadence, 5-6 cm Depth, Scene Safety, AED Protocol.

Educational Purpose Only. Encourage in-person certified BLS/ACLS training.
In medical emergencies in India, always dial 102 (Ambulance) / 112 immediately.
================================================================================
                """
                st.text_area("📜 Your Certificate Text (Copy or Save)", value=cert_text.strip(), height=240)
            else:
                st.warning("Review the 5-Step CPR Guide and AED instructions above, then retry the quiz to earn your certificate.")
