"""
LLM Helper Utility using Groq Cloud API with Graceful Educational Fallback
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

import os
import streamlit as st

# Safe Groq import
GROQ_AVAILABLE = False
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    GROQ_AVAILABLE = False


# Pre-computed curated educational reference for medical terminology (fallback when no API key)
EDUCATIONAL_TERMINOLOGY_MAP = {
    "hemoglobin": "Hemoglobin (Hb) is the iron-containing protein in red blood cells that transports oxygen from your lungs throughout the body. Healthy levels sustain vitality and energy metabolism.",
    "fasting blood sugar": "Fasting Blood Sugar (FBS) measures blood glucose after an overnight fast (8-10 hours). It is a key biomarker for assessing metabolic health and insulin sensitivity.",
    "hba1c": "HbA1c (Glycated Hemoglobin) reflects the average blood glucose concentration over the past 2 to 3 months by measuring glucose bound to hemoglobin. Useful for long-term glucose regulation awareness.",
    "total cholesterol": "Total Cholesterol represents the aggregate amount of lipids (fats) in blood, including LDL, HDL, and VLDL. Balanced levels support healthy vascular function.",
    "ldl": "Low-Density Lipoprotein (LDL) is often nicknamed 'bad cholesterol' because excessive circulating particles can deposit in arterial walls. Aerobic exercise and fiber intake support healthy levels.",
    "hdl": "High-Density Lipoprotein (HDL) is often called 'good cholesterol' as it aids in reverse cholesterol transport, carrying excess cholesterol back to the liver for clearance.",
    "triglycerides": "Triglycerides are the primary storage form of dietary fat circulating in blood. High levels are often linked to excess refined carbohydrate or alcohol intake.",
    "serum creatinine": "Creatinine is a normal metabolic byproduct of muscular breakdown, filtered from the bloodstream by kidneys. It serves as a benchmark for renal filtration efficiency.",
    "uric acid": "Uric acid is produced during the metabolic breakdown of purines found in certain foods and cellular recycling. Clinicians monitor it for gout and renal health awareness.",
    "wbc": "White Blood Cells (Leukocytes) form the primary cellular defense mechanism of the immune system against infections and inflammatory stressors.",
    "platelet": "Platelets (thrombocytes) are specialized blood cell fragments essential for normal blood clotting and vascular repair after injury.",
    "tsh": "Thyroid Stimulating Hormone (TSH) is secreted by the pituitary gland to regulate metabolic rate by controlling thyroid hormone production."
}


def get_ai_summary(prompt: str, system_prompt: str = None) -> str:
    """
    Sends a prompt to Groq Cloud API using model 'llama-3.1-8b-instant'.
    If GROQ_API_KEY is not in secrets or fails, returns educational fallback or None.
    NEVER crashes.
    """
    if not prompt or not prompt.strip():
        return ""

    api_key = None
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            api_key = str(st.secrets["GROQ_API_KEY"]).strip()
    except Exception:
        pass

    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")

    if GROQ_AVAILABLE and api_key and "optional" not in api_key.lower():
        try:
            client = Groq(api_key=api_key)
            system_msg = system_prompt or (
                "You are an educational preventive health science assistant in the MediGuardian AI platform. "
                "Always emphasize: This is for educational purposes only and is not medical advice or diagnostic evaluation. "
                "In case of emergency in India call 112. Explain medical and nutritional terms clearly in simple, accessible language."
            )
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=600,
            )
            if completion.choices and completion.choices[0].message:
                return completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Notice: Groq API call failed: {e}")

    # Fallback to local educational knowledge if key is absent or API fails
    prompt_lower = prompt.lower()
    fallback_matches = []
    for term, explanation in EDUCATIONAL_TERMINOLOGY_MAP.items():
        if term in prompt_lower:
            fallback_matches.append(f"**{term.title()}**: {explanation}")

    if fallback_matches:
        return (
            "*(Educational Knowledge Base - Offline Mode)*\n\n"
            + "\n\n".join(fallback_matches)
            + "\n\n*Educational purpose only. Not medical advice. For emergency in India call 112.*"
        )

    return (
        "Educational Insight: Laboratory parameters reflect biological markers that clinicians interpret alongside physical exams and clinical history. "
        "Normal reference intervals may vary by testing laboratory, age, and biological sex. Always consult a licensed healthcare practitioner for diagnostic guidance."
    )
