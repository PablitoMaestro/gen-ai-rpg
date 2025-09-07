-- Add voice_id column to characters table for ElevenLabs voice integration

-- Add voice_id column to store ElevenLabs generated voice IDs
ALTER TABLE characters 
ADD COLUMN voice_id TEXT;

-- Add comment explaining the column
COMMENT ON COLUMN characters.voice_id IS 'ElevenLabs voice ID for character-specific narration';

-- Create index for voice_id lookups (optional, for performance)
CREATE INDEX IF NOT EXISTS idx_characters_voice_id ON characters(voice_id) WHERE voice_id IS NOT NULL;