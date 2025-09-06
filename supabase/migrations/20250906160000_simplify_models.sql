-- Simplify model architecture by flattening stats columns

-- Drop the character_portraits table (we'll use constants in code)
DROP TABLE IF EXISTS public.character_portraits CASCADE;

-- Add direct stat columns to characters table
ALTER TABLE public.characters 
  ADD COLUMN IF NOT EXISTS build_type text DEFAULT 'warrior' CHECK (build_type IN ('warrior', 'mage', 'rogue', 'ranger')),
  ADD COLUMN IF NOT EXISTS hp integer DEFAULT 100 NOT NULL,
  ADD COLUMN IF NOT EXISTS xp integer DEFAULT 0 NOT NULL,
  ADD COLUMN IF NOT EXISTS level integer DEFAULT 1 NOT NULL;

-- Migrate existing stats data to new columns if stats column exists
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns 
             WHERE table_name = 'characters' AND column_name = 'stats') THEN
    UPDATE public.characters 
    SET 
      hp = COALESCE((stats->>'hp')::integer, 100),
      xp = COALESCE((stats->>'xp')::integer, 0),
      level = COALESCE((stats->>'level')::integer, 1),
      build_type = COALESCE(stats->>'build_type', 'warrior')
    WHERE stats IS NOT NULL;
  END IF;
END $$;

-- Drop the stats JSONB column
ALTER TABLE public.characters DROP COLUMN IF EXISTS stats;

-- Simplify game_sessions by removing redundant hp/xp columns (keep in characters)
-- Keep inventory in sessions as it's session-specific
ALTER TABLE public.game_sessions 
  DROP COLUMN IF EXISTS hp,
  DROP COLUMN IF EXISTS xp;

-- Create a simplified view for active game sessions with character data
CREATE OR REPLACE VIEW public.active_sessions AS
SELECT 
  gs.id AS session_id,
  gs.character_id,
  c.name AS character_name,
  c.gender,
  c.portrait_url,
  c.full_body_url,
  c.build_type,
  c.hp,
  c.xp,
  c.level,
  gs.current_scene,
  gs.choices_made,
  gs.inventory,
  gs.created_at AS session_started,
  gs.updated_at AS last_played
FROM public.game_sessions gs
JOIN public.characters c ON c.id = gs.character_id
WHERE gs.updated_at > now() - interval '7 days';

-- Add RLS policy for the view
ALTER VIEW public.active_sessions SET (security_invoker = true);

-- Create function to get character with active session
CREATE OR REPLACE FUNCTION public.get_character_with_session(p_character_id uuid)
RETURNS TABLE (
  character_id uuid,
  user_id uuid,
  name text,
  gender text,
  portrait_url text,
  full_body_url text,
  build_type text,
  hp integer,
  xp integer,
  level integer,
  session_id uuid,
  current_scene jsonb,
  choices_made jsonb[],
  inventory jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  RETURN QUERY
  SELECT 
    c.id,
    c.user_id,
    c.name,
    c.gender,
    c.portrait_url,
    c.full_body_url,
    c.build_type,
    c.hp,
    c.xp,
    c.level,
    gs.id,
    gs.current_scene,
    gs.choices_made,
    gs.inventory
  FROM public.characters c
  LEFT JOIN public.game_sessions gs ON gs.character_id = c.id
  WHERE c.id = p_character_id
    AND c.user_id = auth.uid()
  ORDER BY gs.created_at DESC
  LIMIT 1;
END;
$$;

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION public.get_character_with_session TO authenticated;

-- Add index for build_type for better query performance
CREATE INDEX IF NOT EXISTS idx_characters_build_type ON public.characters(build_type);