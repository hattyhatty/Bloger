create table if not exists public.workbench_sync (
  user_id uuid primary key references auth.users(id) on delete cascade,
  account text,
  user_name text,
  data jsonb not null,
  updated_at timestamptz not null default now()
);

alter table public.workbench_sync enable row level security;

drop policy if exists "users can read own workbench" on public.workbench_sync;
drop policy if exists "users can insert own workbench" on public.workbench_sync;
drop policy if exists "users can update own workbench" on public.workbench_sync;

create policy "users can read own workbench"
on public.workbench_sync
for select
to authenticated
using (auth.uid() = user_id);

create policy "users can insert own workbench"
on public.workbench_sync
for insert
to authenticated
with check (auth.uid() = user_id);

create policy "users can update own workbench"
on public.workbench_sync
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);
