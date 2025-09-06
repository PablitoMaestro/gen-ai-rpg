# Nano Banana API Test Suite

This test suite provides comprehensive testing for the Nano Banana (Gemini 2.5 Flash Image) API integration and other services in the AI-powered RPG backend.

## 🚀 Quick Start

### 1. Set up your API key
```bash
export GEMINI_API_KEY='your-api-key-here'
export ELEVENLABS_API_KEY='your-elevenlabs-key-here'  # Optional
```

### 2. Run quick test (no images, no API credits)
```bash
cd backend/tests
./run_tests.sh --quick
```

### 3. Start the backend
```bash
cd backend
uvicorn main:app --reload
```

### 4. Open test UI
Open `backend/tests/test_ui.html` in your browser or visit http://localhost:8000/docs

## 📦 Available Test Scripts

### `quick_test.py`
Minimal test script for quick validation:
```bash
python quick_test.py           # Test story generation only (free)
python quick_test.py --image   # Include image generation (1 API credit)
```

### `test_services.py`
Comprehensive test suite with all features:
```bash
python test_services.py                    # Run all tests
python test_services.py --feature story    # Test specific feature
python test_services.py --quick           # Quick tests only
```

Available features:
- `story` - Gemini text story generation
- `character` - Nano Banana character generation
- `scene` - Nano Banana scene generation
- `branches` - Parallel story branch generation
- `tts` - ElevenLabs text-to-speech
- `db` - Supabase connection

### `run_tests.sh`
Shell script wrapper with colored output:
```bash
./run_tests.sh --help          # Show help
./run_tests.sh --quick         # Quick test
./run_tests.sh --feature story # Test specific feature
./run_tests.sh --image         # Include image test
./run_tests.sh                 # Full test suite (prompts for confirmation)
```

## 🌐 API Test Endpoints

When running in development mode, test endpoints are available at `/api/test`:

### Health Check
```bash
curl http://localhost:8000/api/test/health
```

### Story Generation
```bash
curl -X POST http://localhost:8000/api/test/story \
  -H "Content-Type: application/json" \
  -d '{"character_description": "A brave warrior"}'
```

### Character Generation
```bash
curl -X POST http://localhost:8000/api/test/character \
  -H "Content-Type: application/json" \
  -d '{"gender": "male", "build_type": "warrior", "use_test_image": true}'
```

### Scene Generation
```bash
curl -X POST http://localhost:8000/api/test/scene \
  -H "Content-Type: application/json" \
  -d '{"scene_description": "A dark forest", "use_test_character": true}'
```

### Story Branches (Parallel)
```bash
curl -X POST http://localhost:8000/api/test/branches
```

### Text-to-Speech
```bash
curl -X POST http://localhost:8000/api/test/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome, adventurer!"}'
```

### All Character Builds
```bash
curl -X POST http://localhost:8000/api/test/character-builds
```

### API Status Check
```bash
curl http://localhost:8000/api/test/api-status
```

## 🖥️ Browser Test UI

Open `test_ui.html` in your browser for an interactive test interface:

1. Make sure backend is running (`uvicorn main:app --reload`)
2. Open `test_ui.html` in a browser
3. Click buttons to test different features
4. View generated images and listen to TTS output directly

Features:
- Visual test interface with live results
- Image preview for generated content
- Audio playback for TTS
- API status indicator
- Configurable backend URL

## 📁 Test Output

Test results are saved to `test_results/` directory:
- `test_summary.json` - Complete test results
- `story_generation.json` - Story test output
- `character_*.png` - Generated character images
- `scene_*.png` - Generated scene images
- `branch_*.png` - Story branch images
- `narration.mp3` - TTS audio output

## ⚠️ API Usage Warning

**Free Tier Limits (Hackathon):**
- 100 requests per day per project
- Resets at midnight UTC
- Each image generation = 1 request

**Test Suite Usage:**
- Quick test: 0 credits (text only)
- Single image test: 1 credit
- Full test suite: ~10-15 credits
- All character builds: 4 credits

**Cost After Free Tier:**
- $0.039 per image
- Text generation: minimal cost

## 🔧 Troubleshooting

### API Key Not Found
```bash
export GEMINI_API_KEY='your-key-here'
```

### Module Not Found
```bash
pip install pillow google-generativeai
```

### Rate Limit Exceeded
Wait until midnight UTC for free tier reset or use a different API key.

### Image Generation Fails
- Check API key is valid
- Verify you have credits remaining
- Ensure model name is correct: `gemini-2.5-flash-image-preview`

### Backend Connection Failed
- Ensure backend is running: `uvicorn main:app --reload`
- Check URL in test UI (default: http://localhost:8000)
- Verify CORS settings if testing from different port

## 📊 Expected Results

### Successful Test Output
```
✅ Story generation successful. Narration length: 523
   Choices: ['Enter the cave', 'Search for another way', ...]
✅ Character generated: warrior - 125632 bytes
✅ Scene generated: 98234 bytes
✅ Branches generated: 4/4 successful
✅ TTS generation successful: 45632 bytes
✅ Supabase connection successful

Total: 6 tests
Passed: 6
Failed: 0
```

### Test Images
- Character images: Full-body RPG characters in different classes
- Scene images: Characters integrated into environments
- Branch images: Different story path visualizations

## 🚦 Next Steps

After successful tests:

1. **Review Documentation**
   - `backend/docs/gemini/` - Complete API documentation
   - `RPG_INTEGRATION_GUIDE.md` - Game-specific patterns

2. **Implement Game Features**
   - Character creation flow
   - Scene generation system
   - Story branching logic
   - Combat visualization

3. **Optimize Performance**
   - Implement caching
   - Add pre-rendering
   - Set up rate limiting
   - Monitor API usage

4. **Production Setup**
   - Configure environment variables
   - Set up error handling
   - Implement logging
   - Add monitoring

## 📝 Notes

- Test images are simple placeholders to avoid using API credits
- Real images require valid portraits and use Nano Banana API
- All tests respect rate limits with delays
- Test endpoints only available in development mode
- Results saved locally for debugging