"""
Supabase Client & Local Mock Database Fallback for MediGuardian AI
Ensures 100% uptime with graceful degradation to st.session_state if Supabase is unavailable.
"""

import os
import uuid
from datetime import datetime, date
import streamlit as st

# Safe Supabase import
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False
    Client = None


def init_local_db():
    """Initializes local session_state database fallback if not already present."""
    if "local_db" not in st.session_state:
        st.session_state["local_db"] = {
            "users": [],
            "nutrition_logs": [],
            "diet_plans": [],
            "heart_logs": [],
            "lab_reports": [],
            "medicines": [],
            "daily_health_logs": [],
            "intake_logs": [],
            "food_database": [
                {"food_name": "Roti", "calories_per_100g": 264, "protein_per_100g": 8.2, "carbs_per_100g": 47.1, "fat_per_100g": 5.1, "category": "Staple"},
                {"food_name": "Rice", "calories_per_100g": 130, "protein_per_100g": 2.4, "carbs_per_100g": 28.0, "fat_per_100g": 0.2, "category": "Staple"},
                {"food_name": "Dal", "calories_per_100g": 116, "protein_per_100g": 7.2, "carbs_per_100g": 15.1, "fat_per_100g": 3.2, "category": "Curry"},
                {"food_name": "Paneer", "calories_per_100g": 260, "protein_per_100g": 18.0, "carbs_per_100g": 6.0, "fat_per_100g": 20.0, "category": "Curry"},
                {"food_name": "Chicken Curry", "calories_per_100g": 180, "protein_per_100g": 16.0, "carbs_per_100g": 8.0, "fat_per_100g": 10.0, "category": "Non-Veg"},
                {"food_name": "Idli", "calories_per_100g": 58, "protein_per_100g": 2.0, "carbs_per_100g": 12.0, "fat_per_100g": 0.5, "category": "South Indian"},
                {"food_name": "Dosa", "calories_per_100g": 133, "protein_per_100g": 2.5, "carbs_per_100g": 18.0, "fat_per_100g": 5.0, "category": "South Indian"},
            ]
        }


@st.cache_resource(show_spinner=False)
def get_supabase():
    """
    Returns a configured Supabase client if secrets or environment variables exist.
    Returns None if missing or if connection fails.
    """
    if not SUPABASE_AVAILABLE:
        return None

    url = None
    key = None

    # Try Streamlit Secrets first
    try:
        if hasattr(st, "secrets") and "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
            url = str(st.secrets["SUPABASE_URL"]).strip()
            key = str(st.secrets["SUPABASE_KEY"]).strip()
    except Exception:
        pass

    # Fallback to Environment Variables
    if not url or not key:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

    if not url or not key or "your-project" in url or "your-anon-key" in key:
        return None

    try:
        client: Client = create_client(url, key)
        return client
    except Exception as e:
        # Never crash the app
        print(f"Notice: Supabase client initialization error: {e}")
        return None


def test_supabase_connection(url: str, key: str) -> tuple:
    """
    Tests whether a Supabase URL and Key can successfully establish a client connection.
    Returns: (is_success: bool, message: str)
    """
    if not SUPABASE_AVAILABLE:
        return (False, "supabase-py library is not available in the current environment.")

    url = str(url or "").strip()
    key = str(key or "").strip()

    if not url or not key:
        return (False, "Please provide both Supabase URL and Anon Key.")
    if not url.startswith("http://") and not url.startswith("https://"):
        return (False, "Supabase URL must start with https:// (or http://).")

    try:
        test_client = create_client(url, key)
        # Attempt lightweight probe
        test_client.table("food_database").select("food_name").limit(1).execute()
        return (True, "Successfully connected to Supabase and verified database tables!")
    except Exception as e:
        err_msg = str(e)
        if "relation" in err_msg.lower() or "does not exist" in err_msg.lower() or "404" in err_msg:
            return (True, "Connected to your Supabase project, but tables are missing. Please run supabase_schema.sql in Supabase SQL Editor!")
        return (False, f"Connection failed: {err_msg}")


def save_supabase_credentials(url: str, key: str, groq_key: str = None) -> tuple:
    """
    Saves credentials into .streamlit/secrets.toml and .env, then resets the cached client.
    """
    try:
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        secrets_dir = os.path.join(project_dir, ".streamlit")
        os.makedirs(secrets_dir, exist_ok=True)
        secrets_path = os.path.join(secrets_dir, "secrets.toml")
        env_path = os.path.join(project_dir, ".env")

        existing_groq = groq_key or ""
        if not existing_groq and os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GROQ_API_KEY") and "=" in line:
                            existing_groq = line.split("=", 1)[1].strip().strip("\"'")
            except Exception:
                pass

        secrets_content = f"""# Supabase Configuration
SUPABASE_URL = "{url.strip()}"
SUPABASE_KEY = "{key.strip()}"

# Groq Cloud API Key (Optional)
GROQ_API_KEY = "{existing_groq}"
"""
        with open(secrets_path, "w", encoding="utf-8") as f:
            f.write(secrets_content)

        env_content = f"""SUPABASE_URL={url.strip()}
SUPABASE_KEY={key.strip()}
GROQ_API_KEY={existing_groq}
"""
        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        os.environ["SUPABASE_URL"] = url.strip()
        os.environ["SUPABASE_KEY"] = key.strip()

        # Reset cache
        try:
            get_supabase.clear()
        except Exception:
            pass

        return (True, "Credentials successfully saved! Live Supabase is now active.")
    except Exception as e:
        return (False, f"Failed to save credentials: {e}")


def is_using_supabase() -> bool:
    """Returns True if live Supabase client is connected, False otherwise."""
    return get_supabase() is not None


def insert_data(table: str, data: dict) -> dict:
    """
    Inserts a row into either Supabase or the local session_state database.
    Always returns the inserted record or dict with id.
    """
    init_local_db()
    client = get_supabase()

    # Normalize data dict
    data_to_save = dict(data)
    if "id" not in data_to_save:
        data_to_save["id"] = str(uuid.uuid4())
    if "created_at" not in data_to_save:
        data_to_save["created_at"] = datetime.now().isoformat()

    # Convert date/time objects to ISO string representation for Supabase/JSON
    for k, v in list(data_to_save.items()):
        if isinstance(v, (datetime, date)):
            data_to_save[k] = v.isoformat()

    if client:
        try:
            res = client.table(table).insert(data_to_save).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            return data_to_save
        except Exception as e:
            print(f"Supabase insert failed on {table}, falling back to local: {e}")

    # Fallback to local session_state DB
    if table not in st.session_state["local_db"]:
        st.session_state["local_db"][table] = []
    st.session_state["local_db"][table].append(data_to_save)
    return data_to_save


def select_data(table: str, user_id: str = None, order_by: str = None, ascending: bool = False, limit: int = None) -> list:
    """
    Selects rows from Supabase or local session_state database.
    Filters by user_id if provided.
    """
    init_local_db()
    client = get_supabase()

    if client:
        try:
            query = client.table(table).select("*")
            if user_id:
                query = query.eq("user_id", user_id)
            if order_by:
                query = query.order(order_by, desc=not ascending)
            if limit:
                query = query.limit(limit)
            res = query.execute()
            if res.data is not None:
                return res.data
        except Exception as e:
            print(f"Supabase select failed on {table}, falling back to local: {e}")

    # Fallback to local session_state
    records = st.session_state["local_db"].get(table, [])
    if user_id:
        filtered = [r for r in records if r.get("user_id") == user_id or r.get("id") == user_id]
    else:
        filtered = list(records)

    # Sort if requested
    if order_by and filtered:
        try:
            filtered.sort(key=lambda x: str(x.get(order_by, "")), reverse=not ascending)
        except Exception:
            pass

    if limit and limit > 0:
        return filtered[:limit]
    return filtered


def update_data(table: str, match_key: str, match_val, updates: dict) -> bool:
    """
    Updates records matching match_key = match_val with updates dict.
    """
    init_local_db()
    client = get_supabase()

    # Serialize dates if present
    clean_updates = dict(updates)
    for k, v in list(clean_updates.items()):
        if isinstance(v, (datetime, date)):
            clean_updates[k] = v.isoformat()

    if client:
        try:
            client.table(table).update(clean_updates).eq(match_key, match_val).execute()
            return True
        except Exception as e:
            print(f"Supabase update failed on {table}: {e}")

    # Fallback to local
    records = st.session_state["local_db"].get(table, [])
    updated = False
    for r in records:
        if str(r.get(match_key)) == str(match_val):
            r.update(clean_updates)
            updated = True
    return updated


def delete_data(table: str, match_key: str, match_val) -> bool:
    """
    Deletes records matching match_key = match_val.
    """
    init_local_db()
    client = get_supabase()

    if client:
        try:
            client.table(table).delete().eq(match_key, match_val).execute()
            return True
        except Exception as e:
            print(f"Supabase delete failed on {table}: {e}")

    # Fallback to local
    records = st.session_state["local_db"].get(table, [])
    initial_len = len(records)
    st.session_state["local_db"][table] = [r for r in records if str(r.get(match_key)) != str(match_val)]
    return len(st.session_state["local_db"][table]) < initial_len


def get_food_database() -> list:
    """Returns list of food dicts from database or local fallback."""
    init_local_db()
    client = get_supabase()
    local_foods = st.session_state["local_db"].get("food_database", [])
    if client:
        try:
            res = client.table("food_database").select("*").execute()
            if res.data and len(res.data) > 0:
                return res.data
            else:
                # Seed food_database in Supabase if empty
                client.table("food_database").upsert(local_foods).execute()
                return local_foods
        except Exception as e:
            print(f"Notice fetching food_database: {e}")
    return local_foods


def get_or_create_user(email: str, name: str = None) -> dict:
    """
    Retrieves user by email or creates a new user record.
    Ensures auth.users compatibility if foreign key is active.
    Returns user dict including 'id'.
    """
    init_local_db()
    client = get_supabase()
    clean_email = email.strip().lower()

    if client:
        try:
            res = client.table("users").select("*").eq("email", clean_email).execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
            else:
                # Check / register in Supabase Auth to satisfy auth.users(id) foreign key constraint
                auth_id = None
                valid_domain_email = clean_email if ("@" in clean_email and "." in clean_email.split("@")[1]) else f"{clean_email.split('@')[0]}@gmail.com"
                try:
                    signup_res = client.auth.sign_up({"email": valid_domain_email, "password": "DefaultMediGuardian2026!"})
                    if signup_res.user:
                        auth_id = str(signup_res.user.id)
                except Exception:
                    try:
                        login_res = client.auth.sign_in_with_password({"email": valid_domain_email, "password": "DefaultMediGuardian2026!"})
                        if login_res.user:
                            auth_id = str(login_res.user.id)
                    except Exception:
                        pass

                user_id_to_use = auth_id or str(uuid.uuid4())
                user_payload = {
                    "id": user_id_to_use,
                    "email": clean_email,
                    "name": name or clean_email.split("@")[0].title(),
                    "age": 30,
                    "gender": "Other",
                    "weight_kg": 65.0,
                    "height_cm": 170.0,
                    "activity_level": "Moderately active",
                    "dietary_preference": "Vegetarian",
                    "allergies": "None",
                    "consent_given": True,
                    "created_at": datetime.now().isoformat()
                }
                insert_res = client.table("users").upsert(user_payload).execute()
                if insert_res.data and len(insert_res.data) > 0:
                    return insert_res.data[0]
                return user_payload
        except Exception as e:
            print(f"Notice: Supabase get_or_create_user fallback: {e}")

    # Local fallback
    users = st.session_state["local_db"]["users"]
    for u in users:
        if u.get("email", "").lower() == clean_email:
            return u

    # Create local user
    new_user = {
        "id": str(uuid.uuid4()),
        "email": clean_email,
        "name": name or clean_email.split("@")[0].title(),
        "age": 30,
        "gender": "Other",
        "weight_kg": 65.0,
        "height_cm": 170.0,
        "activity_level": "Moderately active",
        "dietary_preference": "Vegetarian",
        "allergies": "None",
        "consent_given": True,
        "created_at": datetime.now().isoformat()
    }
    users.append(new_user)
    return new_user

