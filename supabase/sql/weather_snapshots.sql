create table if not exists public.weather_snapshots (
    id uuid default gen_random_uuid() primary key,
    location text not null,
    captured_at timestamptz not null,
    temperature_c numeric,
    relative_humidity numeric,
    windspeed_kmh numeric,
    winddirection_deg numeric,
    precipitation_mm numeric,
    previous_temperature_c numeric,
    temperature_change numeric,
    temperature_change_percent numeric,
    source text not null default 'open-meteo',
    metadata jsonb,
    created_at timestamptz not null default now()
);

create index if not exists weather_snapshots_location_time_idx
    on public.weather_snapshots (location, captured_at desc);
