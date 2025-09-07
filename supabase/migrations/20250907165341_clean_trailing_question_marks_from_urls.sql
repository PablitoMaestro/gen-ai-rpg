-- Clean trailing '?' from all URLs in character_builds table
UPDATE character_builds
SET image_url = RTRIM(image_url, '?')
WHERE image_url LIKE '%?';

-- Optional: Clean any future occurrences in characters table if needed
UPDATE characters
SET 
  portrait_url = RTRIM(portrait_url, '?'),
  full_body_url = RTRIM(full_body_url, '?')
WHERE portrait_url LIKE '%?' OR full_body_url LIKE '%?';