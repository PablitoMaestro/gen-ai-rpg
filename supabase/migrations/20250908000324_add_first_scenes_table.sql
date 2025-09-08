-- Create first_scenes table for pre-generated opening scenes
-- Each combination of portrait_id and build_type gets one pre-generated scene

CREATE TABLE public.first_scenes (
    portrait_id TEXT NOT NULL,
    build_type TEXT NOT NULL,
    narration TEXT NOT NULL,
    visual_scene TEXT NOT NULL,
    image_url TEXT,
    audio_url TEXT,
    choices JSONB NOT NULL DEFAULT '[]'::jsonb,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    retry_count INT DEFAULT 0,
    last_error TEXT,
    is_successful BOOLEAN DEFAULT FALSE,
    
    -- Composite primary key for portrait + build combination
    PRIMARY KEY (portrait_id, build_type),
    
    -- Check constraints for valid values
    CONSTRAINT valid_build_type CHECK (build_type IN ('warrior', 'mage', 'rogue', 'ranger')),
    CONSTRAINT valid_portrait_id CHECK (portrait_id ~ '^[mf][1-4]$'),
    CONSTRAINT non_negative_retry_count CHECK (retry_count >= 0)
);

-- Add RLS policies for security
ALTER TABLE public.first_scenes ENABLE ROW LEVEL SECURITY;

-- Allow read access for authenticated users
CREATE POLICY "Allow read access to first scenes for authenticated users" 
    ON public.first_scenes FOR SELECT 
    TO authenticated 
    USING (true);

-- Allow insert/update for service role (for pre-generation script)
CREATE POLICY "Allow insert/update for service role" 
    ON public.first_scenes FOR ALL 
    TO service_role 
    USING (true);

-- Create index for performance
CREATE INDEX idx_first_scenes_success ON public.first_scenes (is_successful, portrait_id, build_type);
CREATE INDEX idx_first_scenes_generated_at ON public.first_scenes (generated_at);