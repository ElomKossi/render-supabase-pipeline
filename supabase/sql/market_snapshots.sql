create table if not exists public.market_snapshots (
    id uuid default gen_random_uuid() primary key,
    symbol text not null,
    captured_at timestamptz not null,
    interval text not null,
    price numeric not null,
    open numeric,
    high numeric,
    low numeric,
    volume numeric,
    previous_close numeric,
    change numeric,
    change_percent numeric,
    source text not null default 'alphavantage',
    metadata jsonb,
    created_at timestamptz not null default now()
);

create index if not exists market_snapshots_symbol_time_idx
    on public.market_snapshots (symbol, captured_at desc);
