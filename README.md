# AI Hero's Journey – The First True AI-Illustrated RPG with Persistent Characters

> **A new era of RPGs: illustrated, immersive, and uniquely yours.**

*🏆 Nano Banana Hackathon Submission • September 2025*

AI-Illustrated RPGs have always struggled with one core problem: **character consistency across scenes**. Traditional solutions rely on costly custom art or generic assets where every player looks the same. Standard AI generators break immersion, producing characters that look completely different from one scene to the next.

**Our project changes that.** With Gemini 2.5 Flash Image and Nano Banana, we use multi-image fusion to establish a hero's "visual DNA." A single portrait is combined in real time with weapons, armor, and environments—so your hero's exact face persists seamlessly across taverns, forests, castles, and battles.

## Core Innovation

**Gemini 2.5 Flash Image** powers this breakthrough through:

- **Multi-image composition** – fusing portraits with equipment, poses, and classes
- **Scene generation** – integrating characters into dynamic story environments  
- **Real-time consistency** – maintaining visual identity across narrative branches

We extend this with **ElevenLabs** for immersive dialogue, with the potential for dynamic music and sound effects. Together, visuals and audio merge into a fully personalized experience: **one portrait, one voice, infinite consistent variations.**

*This isn't an incremental step—it's the first time players can live a truly personalized, persistent AI-Illustrated RPG adventure across both sight and sound.*

## Features

- **🎭 Persistent Character Rendering**: Your hero's exact face appears consistently across all scenes and story branches
- **🗣️ Character-Specific Voice Narration**: 8 unique character voices with personality-driven dialogue delivery
- **⚡ Real-Time Story Generation**: AI-powered narrative with 4-branch pregeneration for instant responses
- **🎚️ Dual Audio Control System**: Separate volume controls for music and narration with elegant UI
- **🎨 Visual DNA Technology**: Multi-image fusion creates consistent character appearance across scenarios
- **📖 Immersive First-Person Narrative**: Experience the story through your character's eyes and voice
- **⚔️ Dynamic Character Builds**: Generate 4 unique character classes (Warrior, Mage, Rogue, Ranger) with stat previews
- **🔄 Scene Pregeneration**: Intelligent content preparation with retry logic and safety handling

## Tech Stack

- **Frontend**: Next.js 15.5.2 + TypeScript + Tailwind CSS + Zustand
- **Backend**: FastAPI + Python + Pydantic
- **Database**: Supabase (PostgreSQL) with simplified schema
- **AI Services**: 
  - **Gemini 2.0 Flash Exp** (story generation and narrative)
  - **Gemini 2.5 Flash Image** (character rendering and scene composition)
  - **Nano Banana API** (multi-image fusion and visual consistency)
  - **ElevenLabs** (character-specific voice synthesis and narration)
- **Audio**: Dual audio system with music and narration controls
- **Storage**: Supabase Storage with automated seeding for character images

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

## Game Experience

### Visual DNA Character Creation
1. **Gender Selection**: Choose male or female archetype
2. **Portrait Selection**: Choose from 8 preset portraits (4 per gender) or upload custom image
3. **Character Name & Backstory**: Define your hero's identity and background
4. **Build Generation**: AI generates 4 unique character builds with distinct classes and stats
5. **Visual DNA Establishment**: Your selected portrait becomes the consistent "face" across all scenes

### Immersive Gameplay Loop
1. **Voiced First-Person Narrative**: Experience rich storytelling with character-specific voice narration
2. **Consistent Visual Scenes**: See your exact character rendered in dynamic environments  
3. **Four-Choice Decision Points**: Each choice instantly loads pre-generated content
4. **Character Progression**: Track HP, XP, level, and inventory with real-time updates
5. **Audio Controls**: Adjust music and narration volumes independently during gameplay

### The Visual DNA Advantage
- **Same Face, Every Scene**: Your character's exact appearance persists from taverns to battlefields
- **Dynamic Equipment**: Watch armor, weapons, and poses change while maintaining facial consistency
- **Environmental Integration**: Character seamlessly appears in forests, castles, dungeons, and towns
- **Voice Consistency**: Character-matched voice narration maintains immersion throughout the adventure

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

## Project Status

### 🚀 Hackathon Ready
- **Core Game Loop**: ✅ Complete - Full character creation to story progression
- **Voice System**: ✅ Complete - 8 character voices with ElevenLabs integration  
- **Visual DNA**: ✅ Complete - Persistent character rendering across all scenes
- **Audio Controls**: ✅ Complete - Dual volume system with elegant UI
- **Scene Pregeneration**: ✅ Complete - Intelligent content preparation with retry logic
- **Character Builds**: ✅ Complete - 32 pregenerated combinations (8 portraits × 4 classes)

### 🎯 What Makes This Special
- **First True Persistent AI Characters**: Breakthrough in character consistency using multi-image fusion
- **Immersive Voice Experience**: Character-specific narration that matches personality and appearance
- **Real-Time Responsiveness**: Pre-generated content ensures instant story progression
- **Production Ready**: Complete system from character creation through gameplay with voice narration

### 🔄 Next Steps  
- **Save/Load System**: Persist game progress across sessions
- **Production Deployment**: Launch on Vercel (frontend) and Scaleway (backend)
- **Mobile Optimization**: Enhanced responsive design for mobile gameplay

## API Limits & Development

- **Gemini 2.0 Flash Exp**: 100 requests/day (free tier) - story generation
- **Gemini 2.5 Flash Image**: Used for character rendering and scene composition
- **Nano Banana**: Hackathon tier - multi-image fusion capabilities
- **ElevenLabs**: Subscription-based voice synthesis with custom character voices

## Hackathon Innovation

This project represents a fundamental breakthrough in AI-RPGs: **solving the character consistency problem** that has plagued AI-generated games. By establishing visual DNA through multi-image fusion, we've created the first truly personalized, persistent AI-illustrated RPG experience.

**Key Innovation**: One portrait + AI composition = infinite consistent character variations across any scenario.

## Contributing

1. Create a feature branch from `dev` 
2. Follow the development setup in CLAUDE.md
3. Ensure all tests pass and no TypeScript/lint errors
4. Submit a pull request with clear description

## License

MIT - Built for Nano Banana Hackathon 2025