-- Storage bucket setup for character images
-- This ensures the bucket exists and has proper configuration after reset

-- Create the character-images bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'character-images',
  'character-images', 
  true,
  52428800, -- 50MB in bytes
  ARRAY['image/png', 'image/jpeg', 'image/webp']::text[]
)
ON CONFLICT (id) DO UPDATE SET
  public = EXCLUDED.public,
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- Note: RLS policies for storage.objects are managed by Supabase internally
-- The bucket's public setting above controls access

-- Important: After running 'supabase db reset', you must run 'supabase seed buckets'
-- to re-upload the files from the local filesystem to storage.
-- The files are stored in supabase/character-images/ directory.
-- 
-- You can use one of these commands:
--   make resetdb         # Resets DB and automatically seeds storage
--   make seed-storage    # Only seeds storage without resetting DB
--   supabase seed buckets # Direct command to seed storage