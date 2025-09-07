-- Seed data for development and testing
-- Since character_portraits table no longer exists, portraits are now handled in code

-- Create a test user in auth.users for development (if needed)
-- Note: This is optional and only for local development
DO $$
BEGIN
  -- Check if test user already exists
  IF NOT EXISTS (
    SELECT 1 FROM auth.users 
    WHERE email = 'test@example.com'
  ) THEN
    -- Insert test user (password: testpassword123)
    INSERT INTO auth.users (
      id,
      email,
      encrypted_password,
      email_confirmed_at,
      created_at,
      updated_at,
      raw_app_meta_data,
      raw_user_meta_data
    ) VALUES (
      '00000000-0000-0000-0000-000000000001',
      'test@example.com',
      crypt('testpassword123', gen_salt('bf')),
      now(),
      now(),
      now(),
      '{"provider": "email", "providers": ["email"]}',
      '{}'
    );
  END IF;
END $$;

-- Sample characters for testing (with flattened stats)
INSERT INTO public.characters (
  id,
  user_id,
  name,
  gender,
  portrait_url,
  full_body_url,
  build_type,
  hp,
  xp,
  level
) VALUES 
  (
    '11111111-1111-1111-1111-111111111111',
    '00000000-0000-0000-0000-000000000001',
    'Aragorn the Brave',
    'male',
    'https://placehold.co/400x400/2c3e50/ecf0f1?text=Aragorn',
    'https://placehold.co/800x1200/2c3e50/ecf0f1?text=Aragorn+Full',
    'warrior',
    120,
    250,
    3
  ),
  (
    '22222222-2222-2222-2222-222222222222',
    '00000000-0000-0000-0000-000000000001',
    'Lyra Moonwhisper',
    'female',
    'https://placehold.co/400x400/9b59b6/ecf0f1?text=Lyra',
    'https://placehold.co/800x1200/9b59b6/ecf0f1?text=Lyra+Full',
    'mage',
    85,
    180,
    2
  )
ON CONFLICT (id) DO NOTHING;

-- Sample game session for testing
INSERT INTO public.game_sessions (
  id,
  character_id,
  current_scene,
  choices_made,
  inventory
) VALUES (
  '33333333-3333-3333-3333-333333333333',
  '11111111-1111-1111-1111-111111111111',
  '{"scene_id": "forest_entrance", "description": "You stand at the edge of a dark forest"}',
  ARRAY[
    '{"choice": "enter_forest", "timestamp": "2025-01-06T10:00:00Z"}',
    '{"choice": "follow_path", "timestamp": "2025-01-06T10:05:00Z"}'
  ]::jsonb[],
  '["sword", "health_potion", "torch"]'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- Note: Portrait presets are now defined in backend/models.py as PRESET_PORTRAITS constant
-- This approach is simpler and doesn't require database queries for static data

-- Character builds seed data
-- Generated from existing builds in the database
-- This ensures all 8 preset portraits have their 4 builds each (32 total)

-- Clear existing builds to avoid conflicts
DELETE FROM character_builds WHERE portrait_id IN ('m1', 'm2', 'm3', 'm4', 'f1', 'f2', 'f3', 'f4');

-- Insert character builds
INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f1',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f1_mage_20250907_023922_cbe7c703.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f1',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f1_ranger_20250907_023922_27fbe57a.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f1',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f1_rogue_20250907_023922_878f2e6b.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f1',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f1_warrior_20250907_023923_256b0779.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f2',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f2_mage_20250907_023933_0ae8a49c.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f2',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f2_ranger_20250907_023933_32fea843.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f2',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f2_rogue_20250907_023934_ee522aa4.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f2',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f2_warrior_20250907_023931_0015b718.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f3',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f3_mage_20250907_024221_084a6bd4.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f3',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f3_ranger_20250907_024221_973e6898.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f3',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f3_rogue_20250907_024222_b541f2c5.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f3',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f3_warrior_20250907_024220_53f7ef26.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f4',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f4_mage_20250907_024233_daaa031b.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f4',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f4_ranger_20250907_024232_b2cfee2f.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f4',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f4_rogue_20250907_024232_90de3bea.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'f4',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_f4_warrior_20250907_024233_06d4b97d.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm1',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m1_mage_20250907_024144_8e414d68.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm1',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m1_ranger_20250907_024142_ea6e70c9.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm1',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m1_rogue_20250907_024143_37f72966.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm1',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m1_warrior_20250907_024142_85e0dec8.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm2',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m2_mage_20250907_023943_25e10942.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm2',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m2_ranger_20250907_023945_65252b3e.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm2',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m2_rogue_20250907_023945_d66dda7d.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm2',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m2_warrior_20250907_023943_4ff18609.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm3',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m3_mage_20250907_024154_cfe233b8.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm3',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m3_ranger_20250907_024159_d1ca16d6.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm3',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m3_rogue_20250907_024155_503c76fc.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm3',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m3_warrior_20250907_024153_08491dff.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm4',
    'mage',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m4_mage_20250907_024209_94feb291.png',
    'Frustrated scholar with mediocre magical talent and worn robes',
    '{"agility": 10, "strength": 8, "intelligence": 15}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm4',
    'ranger',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m4_ranger_20250907_024209_d42ec46f.png',
    'Simple tracker with weather-beaten gear and humble skills',
    '{"agility": 13, "strength": 12, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm4',
    'rogue',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m4_rogue_20250907_024209_55bcd01a.png',
    'Common street thief with nervous demeanor and patched leathers',
    '{"agility": 15, "strength": 10, "intelligence": 10}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

INSERT INTO character_builds (
    portrait_id, 
    build_type, 
    image_url, 
    description, 
    stats_preview
) VALUES (
    'm4',
    'warrior',
    'http://127.0.0.1:54331/storage/v1/object/public/character-images/00000000-0000-0000-0000-000000000000/preset_build_m4_warrior_20250907_024209_010fe2f6.png',
    'Weary soldier in patched mail armor, struggling to make ends meet',
    '{"agility": 10, "strength": 15, "intelligence": 8}'::jsonb
) ON CONFLICT (portrait_id, build_type) DO UPDATE SET
    image_url = EXCLUDED.image_url,
    description = EXCLUDED.description,
    stats_preview = EXCLUDED.stats_preview,
    updated_at = NOW();

-- Verify all builds are present
DO $$
DECLARE
    build_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO build_count FROM character_builds;
    RAISE NOTICE 'Total character builds: %', build_count;
    IF build_count < 32 THEN
        RAISE WARNING 'Expected 32 builds but found %', build_count;
    END IF;
END $$;