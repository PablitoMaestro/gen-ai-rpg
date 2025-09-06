-- Seed data for character_portraits table
-- Male preset portraits (4 presets)
insert into public.character_portraits (gender, portrait_url, is_preset)
values 
  ('male', 'https://placehold.co/400x400/2c3e50/ecf0f1?text=Male+Warrior', true),
  ('male', 'https://placehold.co/400x400/34495e/ecf0f1?text=Male+Mage', true),
  ('male', 'https://placehold.co/400x400/1a252f/ecf0f1?text=Male+Rogue', true),
  ('male', 'https://placehold.co/400x400/16a085/ecf0f1?text=Male+Ranger', true);

-- Female preset portraits (4 presets)
insert into public.character_portraits (gender, portrait_url, is_preset)
values 
  ('female', 'https://placehold.co/400x400/8e44ad/ecf0f1?text=Female+Warrior', true),
  ('female', 'https://placehold.co/400x400/9b59b6/ecf0f1?text=Female+Mage', true),
  ('female', 'https://placehold.co/400x400/e74c3c/ecf0f1?text=Female+Rogue', true),
  ('female', 'https://placehold.co/400x400/c0392b/ecf0f1?text=Female+Ranger', true);

-- Note: These are placeholder images for development.
-- In production, replace with actual character portrait images stored in Supabase Storage.