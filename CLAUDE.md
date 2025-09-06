# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered RPG hackathon project that creates an interactive, first-person narrative game with dynamic AI-generated imagery and narration. The game features branching storylines, consistent character rendering, and voice narration capabilities.

## Tech Stack & Architecture

### Frontend (Next.js + TypeScript)
- **Framework**: Next.js with TypeScript, deployed on Vercel
- **State Management**: Zustand for client-side state
- **Validation**: Zod for type validation
- **Styling**: Tailwind CSS
- **Architecture**: Call backend for all external API operations
- **Standards**: Strict TypeScript and lint rules required

### Backend (FastAPI + Python)
- **Framework**: FastAPI with Pydantic
- **Structure**: `/services`, `/scripts` folders following async patterns
- **Deployment**: Scaleway container

### Database (Supabase)
- **Local Development**: Local Supabase instance managed via migrations only
- **Production**: Single main production database
- **Management**: Use Supabase CLI for all database operations
- **Image Storage**: Character portraits stored in Supabase

### External APIs
- **Gemini 2.5 Pro**: Story generation and narration
- **Nano Banana API**: Character and scene image generation
- **ElevenLabs TTS**: Voice narration

## Development Commands

### Frontend Setup
```bash
cd frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install zod zustand
npm run dev        # Start development server
npm run build      # Build for production
npm run lint       # Run linting
npm run typecheck  # Run type checking
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn pydantic python-dotenv
uvicorn main:app --reload  # Start development server
```

### Supabase Setup
```bash
cd supabase
supabase init
supabase start      # Start local instance
supabase db push    # Push migrations to remote
supabase migration new <name>  # Create new migration
```

## Git Workflow
- **Branches**: `main` (production) and `dev` (development)
- **Merge Policy**: Only merge dev → main when no TypeScript/lint errors
- **Current Branch**: dev

## Game Flow Implementation

### Stage 1: Character Creation
1. Gender selection (male/female)
2. Portrait selection (4 presets per gender) or custom upload
3. Generate 4 full-body character builds in parallel using Nano Banana
4. Save selected build for story image generation

### Core Gameplay Loop
1. Present first-person narration with scene image
2. Display 4 choice options
3. Pre-render 4 branches in parallel (text + images)
4. Instant display on choice selection
5. Update character state (HP, XP, inventory)

## API Integration Patterns

### Nano Banana (Gemini 2.5 Flash Image)
- Model: `gemini-2.5-flash-image-preview`
- Use for character generation and scene composition
- Support multiple input images for consistent character rendering
- Example available in: `nano-banana-hackathon-kit/examples/javascript-getting-started.md`

### Parallel Processing
- Always generate 4 story branches simultaneously
- Pre-render images for all possible choices
- Minimize user wait time through async operations

## Code Principles
- **DRY**: Don't repeat yourself - use services and modular components
- **Simplicity**: MVP for hackathon - avoid overcomplication
- **Scalability**: Structure for easy future expansion
- **Clean Code**: Modular, service-based architecture

## Planning & Documentation
- Use `plan.md` for major feature planning with checkpoints
- Track progress systematically
- Focus on MVP features first, then stretch goals

## API Limits & Notes
- Gemini API: 100 requests per project per day (free tier)
- Use free tier API key for hackathon
- Paid keys will incur charges for all usage

## Specialized Agents

### Available Agents (call by name):
- **Babcia/Babcia Stasia**: DevOps agent for verifying configurations, service connections, API keys, and environment setups
- **Chuck Norris**: Complex coding challenges, debugging, and elegant refactoring solutions
- **Robert**: Database operations specialist for Supabase queries, migrations, and schema management
- **Kasia**: API documentation collector for external API integration docs
- **Sun Tzu**: Strategic planning for code changes, refactoring, and architectural decisions