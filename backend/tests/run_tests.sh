#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Nano Banana API Test Suite${NC}"
echo "========================================"

# Check if virtual environment exists in parent directory
if [ ! -d "../venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    cd ..
    python3 -m venv venv
    cd tests
fi

# Activate virtual environment
source ../venv/bin/activate

# Parse arguments first (for --help)
FEATURE=""
QUICK=false
IMAGE=false
SHOW_HELP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help)
            SHOW_HELP=true
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Show help and exit early if requested
if [ "$SHOW_HELP" = true ]; then
    echo "Usage: ./run_tests.sh [options]"
    echo ""
    echo "Options:"
    echo "  --quick         Run quick tests only (no image generation)"
    echo "  --image         Include image generation test"
    echo "  --feature NAME  Test specific feature:"
    echo "                  story, character, scene, branches, tts, db"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh --quick           # Quick test without images"
    echo "  ./run_tests.sh --feature story   # Test story generation only"
    echo "  ./run_tests.sh --image           # Full test with images"
    exit 0
fi

# Install dependencies if needed
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q pillow 2>/dev/null

# Check for API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ Error: GEMINI_API_KEY not set${NC}"
    echo "Please set your API key:"
    echo "  export GEMINI_API_KEY='your-key-here'"
    exit 1
fi

echo -e "${GREEN}✅ API Key found${NC}"
echo ""

# Parse remaining arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --feature)
            FEATURE="$2"
            shift
            shift
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --image)
            IMAGE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run appropriate test
if [ "$QUICK" = true ]; then
    echo -e "${YELLOW}Running quick tests (no image generation)...${NC}"
    echo ""
    python quick_test.py
elif [ ! -z "$FEATURE" ]; then
    echo -e "${YELLOW}Testing feature: $FEATURE${NC}"
    echo ""
    python test_services.py --feature "$FEATURE"
elif [ "$IMAGE" = true ]; then
    echo -e "${YELLOW}Running quick test with image generation...${NC}"
    echo ""
    python quick_test.py --image
else
    echo -e "${YELLOW}Running full test suite...${NC}"
    echo -e "${RED}⚠️  This will use API credits!${NC}"
    read -p "Continue? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python test_services.py
    else
        echo "Aborted."
        exit 0
    fi
fi

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start backend: uvicorn main:app --reload"
    echo "2. Visit API docs: http://localhost:8000/docs"
    echo "3. Test endpoints: http://localhost:8000/api/test/health"
else
    echo ""
    echo -e "${RED}❌ Tests failed${NC}"
    echo "Please check the error messages above."
fi