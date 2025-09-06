# AI-Powered RPG Game

An interactive, first-person narrative RPG game with dynamic AI-generated imagery and narration. Built for a hackathon, featuring branching storylines, consistent character rendering, and voice narration capabilities.

## Features

- **Dynamic Story Generation**: AI-powered narrative that adapts to player choices
- **Character Creation**: Custom character portraits and builds
- **Visual Storytelling**: AI-generated scene images for immersive gameplay
- **Voice Narration**: Text-to-speech narration for story elements
- **Branching Paths**: Multiple story branches with pre-rendered content for instant responses
- **Character Progression**: Track HP, XP, and inventory throughout the adventure

## Tech Stack

- **Frontend**: Next.js 15.5 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Database**: Supabase (PostgreSQL)
- **AI Services**: 
  - Gemini 2.5 Pro (story generation)
  - Nano Banana API (image generation)
  - ElevenLabs (voice synthesis)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- Docker (for Supabase local development)
- Supabase CLI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gen-ai-rpg.git
cd gen-ai-rpg
```

2. Install all dependencies:
```bash
make install
```

3. Set up environment variables:
```bash
# Copy example env files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

4. Configure your API keys in the `.env` files:
- Gemini API key
- Nano Banana API key
- ElevenLabs API key
- Supabase credentials

### Running the Application

Start all services with one command:
```bash
make runl
```

This will start:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Supabase Studio: http://localhost:54323

To stop all services:
```bash
make stop
```

## Development

### Available Make Commands

```bash
make runl        # Start all services locally
make stop        # Stop all services
make status      # Check service status
make commitq     # Quick commit and push
make install     # Install dependencies
```

### Manual Service Start

**Frontend:**
```bash
cd frontend
npm run dev
```

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

**Database:**
```bash
cd supabase
supabase start
```

## Game Flow

### Character Creation
1. Select gender (male/female)
2. Choose from 4 preset portraits or upload custom
3. Generate 4 full-body character builds
4. Select final character for the adventure

### Gameplay Loop
1. View first-person narration with scene image
2. Choose from 4 action options
3. Experience immediate response (pre-rendered)
4. Track character progression (HP, XP, inventory)

## Project Structure

```
gen-ai-rpg/
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/# React components
│   │   └── services/  # API services
├── backend/           # FastAPI server
│   ├── api/          # API endpoints
│   ├── services/     # Business logic
│   └── models.py     # Pydantic models
├── supabase/         # Database
│   └── migrations/   # SQL migrations
└── Makefile          # Development commands
```

## API Limits

- **Gemini API**: 100 requests/day (free tier)
- **Nano Banana**: Check hackathon kit for limits
- **ElevenLabs**: Based on subscription tier

## Contributing

1. Create a feature branch from `dev`
2. Make your changes
3. Ensure no TypeScript/lint errors
4. Submit a pull request to `dev`

## Deployment

- **Frontend**: Deployed on Vercel
- **Backend**: Deployed on Scaleway
- **Database**: Supabase cloud

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.