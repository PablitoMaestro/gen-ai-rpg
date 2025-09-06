-- Create character_builds table for storing pre-generated character builds
CREATE TABLE IF NOT EXISTS character_builds (
  id UUID DEFAULT extensions.uuid_generate_v4() PRIMARY KEY,
  portrait_id TEXT NOT NULL, -- Links to preset portrait IDs (m1, m2, f1, f2, etc.) or custom IDs
  build_type TEXT NOT NULL CHECK (build_type IN ('warrior', 'mage', 'rogue', 'ranger')),
  image_url TEXT NOT NULL, -- Generated full-body character image URL
  description TEXT NOT NULL, -- Build description for UI
  stats_preview JSONB NOT NULL DEFAULT '{"strength": 10, "intelligence": 10, "agility": 10}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Ensure we have one build per portrait_id + build_type combination
  UNIQUE(portrait_id, build_type)
);

-- Add RLS (Row Level Security)
ALTER TABLE character_builds ENABLE ROW LEVEL SECURITY;

-- Add policy to allow read access to all authenticated users
CREATE POLICY "character_builds_select_policy" ON character_builds
  FOR SELECT
  USING (TRUE);

-- Add policy to allow insert/update for service role (for pre-generation scripts)
CREATE POLICY "character_builds_insert_policy" ON character_builds
  FOR INSERT
  WITH CHECK (TRUE);

CREATE POLICY "character_builds_update_policy" ON character_builds
  FOR UPDATE
  USING (TRUE);

-- Create index for fast lookups by portrait_id
CREATE INDEX IF NOT EXISTS idx_character_builds_portrait_id ON character_builds (portrait_id);

-- Create index for build_type queries
CREATE INDEX IF NOT EXISTS idx_character_builds_build_type ON character_builds (build_type);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_character_builds_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_character_builds_updated_at_trigger
  BEFORE UPDATE ON character_builds
  FOR EACH ROW
  EXECUTE FUNCTION update_character_builds_updated_at();