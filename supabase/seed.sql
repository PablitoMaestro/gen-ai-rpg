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