-- Run this in your Supabase project: SQL Editor → New Query

create table if not exists documents (
    id              uuid primary key default gen_random_uuid(),
    user_id         uuid references auth.users(id) on delete set null,
    title           text not null,
    document_type   text not null,
    topic           text not null,
    style           text not null default 'professional',
    file_name       text not null unique,
    storage_url     text not null,
    file_size       integer not null,
    created_at      timestamptz not null default now()
);

-- Index for fetching a user's documents quickly
create index if not exists documents_user_id_idx on documents(user_id);

-- Row-level security: users can only read their own documents
alter table documents enable row level security;

create policy "Users can read own documents"
    on documents for select
    using (auth.uid() = user_id);

create policy "Service role can insert"
    on documents for insert
    with check (true);
