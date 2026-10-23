"""
Health, Nutrition, and Metabolic Calculations for MediGuardian AI
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

from typing import Dict, Any, Tuple

# Comprehensive Indian Food Composition Database (Values per 100 grams)
INDIAN_FOOD_DATABASE: Dict[str, Dict[str, float]] = {
    "Roti / Chapati": {"calories": 264.0, "protein": 8.2, "carbs": 47.1, "fat": 5.1, "category": "Staple"},
    "White Rice (Cooked)": {"calories": 130.0, "protein": 2.4, "carbs": 28.0, "fat": 0.2, "category": "Staple"},
    "Brown Rice (Cooked)": {"calories": 111.0, "protein": 2.6, "carbs": 23.0, "fat": 0.9, "category": "Staple"},
    "Yellow Dal Tadka": {"calories": 116.0, "protein": 7.2, "carbs": 15.1, "fat": 3.2, "category": "Lentils/Curry"},
    "Moong Dal (Cooked)": {"calories": 105.0, "protein": 7.0, "carbs": 16.0, "fat": 1.5, "category": "Lentils/Curry"},
    "Chana Dal": {"calories": 160.0, "protein": 8.5, "carbs": 24.0, "fat": 3.5, "category": "Lentils/Curry"},
    "Rajma Masala (Kidney Beans)": {"calories": 140.0, "protein": 8.0, "carbs": 22.0, "fat": 2.5, "category": "Lentils/Curry"},
    "Chole / Chickpea Curry": {"calories": 165.0, "protein": 7.5, "carbs": 25.0, "fat": 4.2, "category": "Lentils/Curry"},
    "Paneer Butter Masala": {"calories": 260.0, "protein": 12.0, "carbs": 9.0, "fat": 20.0, "category": "Curry"},
    "Palak Paneer": {"calories": 190.0, "protein": 10.0, "carbs": 6.0, "fat": 14.0, "category": "Curry"},
    "Matar Paneer": {"calories": 170.0, "protein": 9.0, "carbs": 11.0, "fat": 10.0, "category": "Curry"},
    "Chicken Curry": {"calories": 180.0, "protein": 16.0, "carbs": 8.0, "fat": 10.0, "category": "Non-Veg"},
    "Chicken Tikka": {"calories": 150.0, "protein": 25.0, "carbs": 3.0, "fat": 4.0, "category": "Non-Veg"},
    "Fish Curry": {"calories": 145.0, "protein": 18.0, "carbs": 4.0, "fat": 6.5, "category": "Non-Veg"},
    "Egg Curry (2 Eggs)": {"calories": 135.0, "protein": 10.0, "carbs": 5.0, "fat": 8.5, "category": "Non-Veg"},
    "Boiled Egg": {"calories": 155.0, "protein": 13.0, "carbs": 1.1, "fat": 11.0, "category": "Non-Veg"},
    "Egg Omelette": {"calories": 180.0, "protein": 12.0, "carbs": 2.0, "fat": 14.0, "category": "Non-Veg"},
    "Idli (Steamed)": {"calories": 58.0, "protein": 2.0, "carbs": 12.0, "fat": 0.5, "category": "South Indian"},
    "Plain Dosa": {"calories": 133.0, "protein": 2.5, "carbs": 18.0, "fat": 5.0, "category": "South Indian"},
    "Masala Dosa": {"calories": 165.0, "protein": 3.0, "carbs": 24.0, "fat": 6.5, "category": "South Indian"},
    "Sambar": {"calories": 65.0, "protein": 3.2, "carbs": 10.0, "fat": 1.5, "category": "South Indian"},
    "Coconut Chutney": {"calories": 185.0, "protein": 2.2, "carbs": 6.0, "fat": 17.0, "category": "South Indian"},
    "Upma (Semolina)": {"calories": 135.0, "protein": 3.0, "carbs": 21.0, "fat": 4.5, "category": "Breakfast"},
    "Poha (Flattened Rice)": {"calories": 130.0, "protein": 2.5, "carbs": 24.0, "fat": 2.8, "category": "Breakfast"},
    "Besan Chilla (Gram Flour Pancake)": {"calories": 160.0, "protein": 7.5, "carbs": 19.0, "fat": 6.0, "category": "Breakfast"},
    "Khichdi (Moong Dal & Rice)": {"calories": 120.0, "protein": 4.5, "carbs": 20.0, "fat": 2.5, "category": "Staple"},
    "Oats Porridge": {"calories": 70.0, "protein": 2.5, "carbs": 12.0, "fat": 1.5, "category": "Breakfast"},
    "Aloo Gobi": {"calories": 115.0, "protein": 2.8, "carbs": 16.0, "fat": 4.5, "category": "Vegetable"},
    "Bhindi Masala (Okra)": {"calories": 95.0, "protein": 2.2, "carbs": 9.0, "fat": 5.5, "category": "Vegetable"},
    "Baingan Bharta": {"calories": 85.0, "protein": 1.8, "carbs": 8.0, "fat": 5.0, "category": "Vegetable"},
    "Mixed Vegetable Curry": {"calories": 90.0, "protein": 2.5, "carbs": 11.0, "fat": 4.0, "category": "Vegetable"},
    "Curd / Dahi": {"calories": 60.0, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "category": "Dairy"},
    "Chaas / Buttermilk (Spiced)": {"calories": 35.0, "protein": 1.8, "carbs": 2.5, "fat": 1.2, "category": "Dairy"},
    "Plain Sweet Lassi": {"calories": 95.0, "protein": 3.0, "carbs": 14.0, "fat": 3.0, "category": "Dairy"},
    "Sprouts Salad (Moong/Chana)": {"calories": 90.0, "protein": 6.5, "carbs": 14.0, "fat": 0.8, "category": "Salad"},
    "Cucumber Tomato Salad": {"calories": 25.0, "protein": 1.0, "carbs": 4.5, "fat": 0.2, "category": "Salad"},
    "Roasted Makhana (Fox Nuts)": {"calories": 110.0, "protein": 3.0, "carbs": 22.0, "fat": 0.5, "category": "Snacks"},
    "Roasted Chana (Bengal Gram)": {"calories": 160.0, "protein": 9.0, "carbs": 24.0, "fat": 3.0, "category": "Snacks"},
    "Samosa (Potato)": {"calories": 260.0, "protein": 4.5, "carbs": 32.0, "fat": 13.0, "category": "Snacks"},
    "Vada Pav": {"calories": 280.0, "protein": 5.5, "carbs": 40.0, "fat": 11.0, "category": "Snacks"},
    "Puri (Deep Fried)": {"calories": 300.0, "protein": 5.5, "carbs": 42.0, "fat": 13.0, "category": "Staple"},
    "Gulab Jamun (1-2 pieces)": {"calories": 320.0, "protein": 4.0, "carbs": 50.0, "fat": 12.0, "category": "Sweets"},
    "Dhokla (Steamed)": {"calories": 150.0, "protein": 6.5, "carbs": 24.0, "fat": 3.0, "category": "Snacks"},
    "Masala Chai (with milk & sugar)": {"calories": 65.0, "protein": 2.0, "carbs": 9.0, "fat": 2.5, "category": "Beverage"},
    "Filter Coffee (with milk & sugar)": {"calories": 70.0, "protein": 2.2, "carbs": 9.5, "fat": 2.6, "category": "Beverage"},
    "Apple (Fresh)": {"calories": 52.0, "protein": 0.3, "carbs": 14.0, "fat": 0.2, "category": "Fruit"},
    "Banana (Fresh)": {"calories": 89.0, "protein": 1.1, "carbs": 23.0, "fat": 0.3, "category": "Fruit"},
    "Papaya (Fresh)": {"calories": 43.0, "protein": 0.5, "carbs": 11.0, "fat": 0.3, "category": "Fruit"},
    "Almonds (Raw)": {"calories": 579.0, "protein": 21.2, "carbs": 21.6, "fat": 49.9, "category": "Nuts"},
    "Walnuts (Raw)": {"calories": 654.0, "protein": 15.2, "carbs": 13.7, "fat": 65.2, "category": "Nuts"},
}


def get_all_food_names() -> list:
    """Returns sorted list of available food item names."""
    return sorted(list(INDIAN_FOOD_DATABASE.keys()))


def calculate_calories(food_name: str, grams: float) -> Dict[str, float]:
    """
    Looks up food in the database and returns nutritional breakdown for specified grams.
    Uses case-insensitive and partial match lookup, falling back to 150 cal/100g if unknown.
    """
    cleaned_query = (food_name or "").strip().lower()
    matched_item = None

    # Exact or substring match
    for name, nutrition in INDIAN_FOOD_DATABASE.items():
        if name.lower() == cleaned_query:
            matched_item = nutrition
            break
        elif cleaned_query in name.lower() or name.lower() in cleaned_query:
            matched_item = nutrition
            break

    # Fallback to standard Indian meal average: 150 cal/100g
    if not matched_item:
        matched_item = {
            "calories": 150.0,
            "protein": 5.0,
            "carbs": 22.0,
            "fat": 5.0
        }

    scale = max(0.0, float(grams)) / 100.0
    return {
        "calories": round(matched_item["calories"] * scale, 1),
        "protein_g": round(matched_item["protein"] * scale, 1),
        "carbs_g": round(matched_item["carbs"] * scale, 1),
        "fat_g": round(matched_item["fat"] * scale, 1)
    }


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculates Basal Metabolic Rate (BMR) using the Mifflin-St Jeor Equation.
    Men: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) + 5
    Women: BMR = (10 × weight in kg) + (6.25 × height in cm) - (5 × age in years) - 161
    """
    try:
        w = float(weight_kg)
        h = float(height_cm)
        a = int(age)
        g = str(gender).strip().lower()

        base = (10.0 * w) + (6.25 * h) - (5.0 * a)
        if g in ["male", "m", "man"]:
            bmr = base + 5.0
        elif g in ["female", "f", "woman"]:
            bmr = base - 161.0
        else:
            # Average baseline for unspecified/other
            bmr = base - 78.0
        return max(800.0, round(bmr, 1))
    except Exception:
        return 1600.0  # Safe default baseline


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculates Total Daily Energy Expenditure (TDEE) based on activity multiplier:
    - Sedentary (little to no exercise): BMR × 1.2
    - Lightly active (light exercise 1-3 days/week): BMR × 1.375
    - Moderately active (moderate exercise 3-5 days/week): BMR × 1.55
    - Very active (hard exercise 6-7 days/week): BMR × 1.725
    - Extra / Super active (physical job or athletic training): BMR × 1.9
    """
    multipliers = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9,
        "super active": 1.9,
    }
    key = str(activity_level or "").strip().lower()
    factor = 1.375  # default to lightly active
    for level_key, mult in multipliers.items():
        if level_key in key:
            factor = mult
            break

    return round(float(bmr) * factor, 1)


def check_bp_category(systolic: int, diastolic: int) -> Tuple[str, str, str]:
    """
    Returns educational guidance on Blood Pressure according to American Heart Association / ESC guidelines.
    Returns: (Category Name, Color/Status, Educational Context)
    NOTE: Educational purpose only. Not medical advice.
    """
    try:
        sys = int(systolic)
        dia = int(diastolic)
    except Exception:
        return ("Invalid Reading", "gray", "Please provide integer values for systolic and diastolic pressure.")

    if sys < 90 or dia < 60:
        return (
            "Low Blood Pressure (Hypotension)",
            "blue",
            "Educational context: Systolic < 90 mmHg or diastolic < 60 mmHg may cause lightheadedness. Consult a healthcare professional if symptomatic."
        )
    elif sys < 120 and dia < 80:
        return (
            "Normal Blood Pressure",
            "green",
            "Educational context: Within the ideal typical physiological range (< 120/80 mmHg). Maintain with balanced nutrition and regular physical activity."
        )
    elif 120 <= sys <= 129 and dia < 80:
        return (
            "Elevated Blood Pressure",
            "gold",
            "Educational context: Systolic 120-129 mmHg with diastolic < 80 mmHg. Lifestyle modifications such as reduced sodium and aerobic movement are often encouraged by clinicians."
        )
    elif (130 <= sys <= 139) or (80 <= dia <= 89):
        return (
            "Stage 1 Hypertension (Educational Classification)",
            "orange",
            "Educational context: Systolic 130-139 mmHg or diastolic 80-89 mmHg. Please schedule a routine review with your physician. Not a diagnosis."
        )
    elif (sys >= 140 and sys <= 180) or (dia >= 90 and dia <= 120):
        return (
            "Stage 2 Hypertension (Educational Classification)",
            "red",
            "Educational context: Systolic ≥ 140 mmHg or diastolic ≥ 90 mmHg. Clinical guidelines recommend medical consultation for blood pressure management."
        )
    else:  # sys > 180 or dia > 120
        return (
            "Hypertensive Crisis (Potential Urgency)",
            "darkred",
            "URGENT EDUCATIONAL ALERT: Systolic > 180 mmHg and/or diastolic > 120 mmHg. If accompanied by chest pain, shortness of breath, numbness or headache, seek immediate medical attention or call 112 in India."
        )
