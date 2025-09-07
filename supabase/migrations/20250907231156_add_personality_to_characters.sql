-- Add personality column to characters table
ALTER TABLE characters 
ADD COLUMN personality TEXT;

-- Add a comment to document the column
COMMENT ON COLUMN characters.personality IS 'Character personality description used for story generation context';