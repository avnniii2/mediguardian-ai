-- ==============================================================================
-- MediGuardian AI - Supabase Database Schema
-- Run this script in your Supabase SQL Editor:
-- Project Dashboard -> SQL Editor -> New Query -> Paste and Click Run
-- ==============================================================================

create extension if not exists "uuid-ossp";

create table public.users (
    id uuid primary key references auth.users(id) on delete cascade,
    email text unique not null,
    name text,
    age int,
    gender text,
    weight_kg numeric,
    height_cm numeric,
    activity_level text,
    dietary_preference text,
    allergies text,
    consent_given boolean default false,
    created_at timestamptz default now()
);

create table public.nutrition_logs (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) on delete cascade not null,
    log_date date default current_date,
    meal_type text,
    food_name text not null,
    portion_grams numeric not null,
    calories numeric,
    protein_g numeric,
    carbs_g numeric,
    fat_g numeric,
    water_ml numeric,
    meal_time time,
    created_at timestamptz default now()
);

create table public.diet_plans (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) not null,
    goal text,
    target_calories numeric,
    breakfast text,
    lunch text,
    dinner text,
    snacks text,
    is_editable boolean default true,
    created_at timestamptz default now()
);

create table public.heart_logs (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) not null,
    log_date date default current_date,
    systolic int,
    diastolic int,
    resting_hr int,
    cholesterol_total numeric,
    blood_glucose numeric,
    smoking boolean default false,
    activity_min int,
    notes text,
    created_at timestamptz default now()
);

create table public.lab_reports (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) not null,
    upload_date timestamptz default now(),
    file_name text,
    test_name text not null,
    test_value text not null,
    test_value_numeric numeric,
    unit text,
    ref_range text,
    is_outside_range boolean default false,
    is_verified boolean default false,
    ocr_confidence numeric,
    created_at timestamptz default now()
);

create table public.medicines (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) not null,
    medicine_name text not null,
    batch_id text,
    schedule_morning time,
    schedule_afternoon time,
    schedule_evening time,
    schedule_night time,
    expiry_date date,
    quantity_left int,
    is_active boolean default true,
    created_at timestamptz default now()
);

create table public.daily_health_logs (
    id uuid primary key default uuid_generate_v4(),
    user_id uuid references public.users(id) not null,
    log_date date default current_date,
    water_liters numeric,
    sleep_hours numeric,
    exercise_min int,
    symptoms text,
    mood text,
    created_at timestamptz default now()
);

create table public.intake_logs (
    id uuid primary key default uuid_generate_v4(),
    medicine_id uuid references public.medicines(id) on delete cascade not null,
    user_id uuid references public.users(id) not null,
    scheduled_time timestamptz,
    taken_time timestamptz,
    status text default 'TAKEN',
    created_at timestamptz default now()
);

create table public.food_database (
    food_name text primary key,
    calories_per_100g numeric,
    protein_per_100g numeric,
    carbs_per_100g numeric,
    fat_per_100g numeric,
    category text
);

insert into public.food_database values 
('Roti', 264, 8.2, 47.1, 5.1, 'Staple'),
('Rice', 130, 2.4, 28, 0.2, 'Staple'),
('Dal', 116, 7.2, 15.1, 3.2, 'Curry'),
('Paneer', 260, 18, 6, 20, 'Curry'),
('Chicken Curry', 180, 16, 8, 10, 'Non-Veg'),
('Idli', 58, 2, 12, 0.5, 'South Indian'),
('Dosa', 133, 2.5, 18, 5, 'South Indian')
on conflict (food_name) do nothing;

-- Row Level Security (RLS)
alter table public.users enable row level security;
alter table public.nutrition_logs enable row level security;
alter table public.diet_plans enable row level security;
alter table public.heart_logs enable row level security;
alter table public.lab_reports enable row level security;
alter table public.medicines enable row level security;
alter table public.daily_health_logs enable row level security;
alter table public.intake_logs enable row level security;

-- Policies for Row Level Security
create policy "Users manage own data" on public.users for all using (auth.uid() = id);
create policy "Users manage own nutrition" on public.nutrition_logs for all using (auth.uid() = user_id);
create policy "Users manage own diet" on public.diet_plans for all using (auth.uid() = user_id);
create policy "Users manage own heart" on public.heart_logs for all using (auth.uid() = user_id);
create policy "Users manage own lab" on public.lab_reports for all using (auth.uid() = user_id);
create policy "Users manage own meds" on public.medicines for all using (auth.uid() = user_id);
create policy "Users manage own daily" on public.daily_health_logs for all using (auth.uid() = user_id);
create policy "Users manage own intake" on public.intake_logs for all using (auth.uid() = user_id);
