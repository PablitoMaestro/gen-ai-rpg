#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Supabase Database & Storage Reset Script ===${NC}"
echo ""

# Navigate to supabase directory
cd "$(dirname "$0")/../supabase" || exit 1

# Step 1: Reset the database
echo -e "${YELLOW}Step 1: Resetting database...${NC}"
supabase db reset

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database reset completed successfully${NC}"
else
    echo -e "${RED}✗ Database reset failed${NC}"
    exit 1
fi

echo ""

# Step 2: Seed storage buckets
echo -e "${YELLOW}Step 2: Seeding storage buckets from local files...${NC}"
echo -e "${YELLOW}Uploading files from ./character-images/ to storage...${NC}"

supabase seed buckets

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Storage buckets seeded successfully${NC}"
    
    # Count uploaded files
    PRESET_COUNT=$(find character-images/presets -type f 2>/dev/null | wc -l | tr -d ' ')
    BUILD_COUNT=$(find character-images/builds -type f 2>/dev/null | wc -l | tr -d ' ')
    
    echo -e "${GREEN}✓ Uploaded:${NC}"
    echo -e "  - ${GREEN}$PRESET_COUNT${NC} preset images"
    echo -e "  - ${GREEN}$BUILD_COUNT${NC} build images"
else
    echo -e "${RED}✗ Storage seeding failed${NC}"
    echo -e "${YELLOW}Note: Make sure you have files in supabase/character-images/ directory${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Reset Complete ===${NC}"
echo -e "${GREEN}Database and storage have been reset and reseeded successfully!${NC}"
echo ""
echo -e "${YELLOW}You can now access:${NC}"
echo -e "  - Supabase Studio: http://localhost:54323"
echo -e "  - Storage browser: http://localhost:54323/project/default/storage/buckets"