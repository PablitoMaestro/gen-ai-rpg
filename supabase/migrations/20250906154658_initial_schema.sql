-- Enable required extensions
create extension if not exists "uuid-ossp";

-- Create characters table
create table if not exists public.characters (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  gender text not null check (gender in ('male', 'female')),
  portrait_url text not null,
  full_body_url text not null,
  stats jsonb default '{"hp": 100, "xp": 0, "level": 1}'::jsonb,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- Create character_portraits table for preset portraits
create table if not exists public.character_portraits (
  id uuid primary key default uuid_generate_v4(),
  gender text not null check (gender in ('male', 'female')),
  portrait_url text not null,
  is_preset boolean default true not null,
  created_at timestamptz default now() not null
);

-- Create game_sessions table
create table if not exists public.game_sessions (
  id uuid primary key default uuid_generate_v4(),
  character_id uuid not null references public.characters(id) on delete cascade,
  current_scene jsonb default '{}'::jsonb,
  choices_made jsonb[] default array[]::jsonb[],
  hp integer default 100 not null,
  xp integer default 0 not null,
  inventory jsonb default '[]'::jsonb,
  created_at timestamptz default now() not null,
  updated_at timestamptz default now() not null
);

-- Create indexes for better performance
create index if not exists idx_characters_user_id on public.characters(user_id);
create index if not exists idx_character_portraits_gender on public.character_portraits(gender);
create index if not exists idx_game_sessions_character_id on public.game_sessions(character_id);

-- Create updated_at trigger function
create or replace function public.handle_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- Add updated_at triggers
create trigger handle_characters_updated_at
  before update on public.characters
  for each row
  execute function public.handle_updated_at();

create trigger handle_game_sessions_updated_at
  before update on public.game_sessions
  for each row
  execute function public.handle_updated_at();

-- Enable Row Level Security (RLS)
alter table public.characters enable row level security;
alter table public.character_portraits enable row level security;
alter table public.game_sessions enable row level security;

-- RLS Policies for characters table
-- Users can only see their own characters
create policy "Users can view own characters" on public.characters
  for select using (auth.uid() = user_id);

-- Users can only insert their own characters
create policy "Users can insert own characters" on public.characters
  for insert with check (auth.uid() = user_id);

-- Users can only update their own characters
create policy "Users can update own characters" on public.characters
  for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Users can only delete their own characters
create policy "Users can delete own characters" on public.characters
  for delete using (auth.uid() = user_id);

-- RLS Policies for character_portraits table
-- Everyone can view preset portraits
create policy "Anyone can view preset portraits" on public.character_portraits
  for select using (is_preset = true);

-- Only service role can insert portraits (for admin use)
create policy "Service role can insert portraits" on public.character_portraits
  for insert with check (false);

-- RLS Policies for game_sessions table
-- Users can only view sessions for their own characters
create policy "Users can view own game sessions" on public.game_sessions
  for select using (
    exists (
      select 1 from public.characters
      where characters.id = game_sessions.character_id
      and characters.user_id = auth.uid()
    )
  );

-- Users can only insert sessions for their own characters
create policy "Users can insert own game sessions" on public.game_sessions
  for insert with check (
    exists (
      select 1 from public.characters
      where characters.id = game_sessions.character_id
      and characters.user_id = auth.uid()
    )
  );

-- Users can only update sessions for their own characters
create policy "Users can update own game sessions" on public.game_sessions
  for update using (
    exists (
      select 1 from public.characters
      where characters.id = game_sessions.character_id
      and characters.user_id = auth.uid()
    )
  ) with check (
    exists (
      select 1 from public.characters
      where characters.id = game_sessions.character_id
      and characters.user_id = auth.uid()
    )
  );

-- Users can only delete sessions for their own characters
create policy "Users can delete own game sessions" on public.game_sessions
  for delete using (
    exists (
      select 1 from public.characters
      where characters.id = game_sessions.character_id
      and characters.user_id = auth.uid()
    )
  );

-- Create storage bucket for character images
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'character-images',
  'character-images',
  false,
  52428800, -- 50MB
  array['image/jpeg', 'image/png', 'image/webp']
) on conflict (id) do nothing;

-- Storage RLS Policies
-- Allow authenticated users to upload their own character images
create policy "Users can upload character images" on storage.objects
  for insert to authenticated
  with check (
    bucket_id = 'character-images' and
    (storage.foldername(name))[1] = auth.uid()::text
  );

-- Allow authenticated users to view their own character images
create policy "Users can view own character images" on storage.objects
  for select to authenticated
  using (
    bucket_id = 'character-images' and
    (storage.foldername(name))[1] = auth.uid()::text
  );

-- Allow authenticated users to update their own character images
create policy "Users can update own character images" on storage.objects
  for update to authenticated
  using (
    bucket_id = 'character-images' and
    (storage.foldername(name))[1] = auth.uid()::text
  ) with check (
    bucket_id = 'character-images' and
    (storage.foldername(name))[1] = auth.uid()::text
  );

-- Allow authenticated users to delete their own character images
create policy "Users can delete own character images" on storage.objects
  for delete to authenticated
  using (
    bucket_id = 'character-images' and
    (storage.foldername(name))[1] = auth.uid()::text
  );