# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered RPG hackathon project that creates an interactive, first-person narrative game with dynamic AI-generated imagery and narration. The game features branching storylines, consistent character rendering, and voice narration capabilities.

## Tech Stack & Architecture

### Frontend (Next.js + TypeScript) ✅
- **Framework**: Next.js 15.5.2 with TypeScript, deployed on Vercel
- **State Management**: Zustand v5 for client-side state
- **Validation**: Zod v4 for type validation
- **Styling**: Tailwind CSS v3.4 (stable, not v4)
- **Architecture**: Call backend for all external API operations
- **Standards**: Strict TypeScript and ESLint rules configured
- **Theme**: Dark fantasy with custom colors and animations

### Backend (FastAPI + Python) ✅
- **Framework**: FastAPI with Pydantic
- **Models**: Single `models.py` file with unified models (simplified architecture)
- **Database Service**: Direct model usage, no mappers needed
- **Deployment**: Scaleway container
- **Status**: Fully configured with simplified model architecture

### Database (Supabase) ✅
- **Local Development**: Local Supabase instance running with Docker
- **Production**: Deployed to Supabase Cloud (mvwotulkyowfuqoounix)
- **Schema**: Flattened tables with direct columns (no JSONB stats)
- **Tables**: `characters`, `game_sessions`, `character_builds`
- **Storage**: Character images bucket with automatic seeding after reset
- **Management**: Use Supabase CLI for all database operations
- **MCP Integration**: Supabase MCP available for read operations (search_docs working)
- **Status**: Migration applied to both local and production, simplified schema active

### External APIs
- **Gemini 2.5 Pro**: Story generation and narration
- **Nano Banana API**: Character and scene image generation
- **ElevenLabs TTS**: Voice narration

## Development Commands

### Quick Start with Makefile
```bash
make runl        # Start all services (frontend, backend, Supabase)
make stop        # Stop all services
make status      # Check service status
make commitq     # Quick commit and push to current branch
make install     # Install all dependencies
make resetdb     # Reset database and reseed storage buckets
make seed-storage # Reseed storage buckets without database reset
```

### Frontend Setup
```bash
cd frontend
npm install        # Install dependencies
npm run dev        # Start development server (http://localhost:3000)
npm run build      # Build for production
npm run lint       # Run ESLint
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
supabase db reset   # Reset database (use 'make resetdb' for storage preservation)
supabase seed buckets # Seed storage buckets from local files
```

### Storage Management
- **Local Files**: Stored in `supabase/character-images/`
- **Auto-seeding**: Configured in `supabase/config.toml` under `[storage.buckets]`
- **Reset Behavior**: `supabase db reset` clears storage metadata
- **Restoration**: Use `make resetdb` or `supabase seed buckets` to re-upload files

## Project Status
- **Phase 1**: ✅ Complete (All infrastructure set up)
- **Phase 1.5**: ✅ Complete (Model architecture simplified - 70% less complexity)
- **Phase 2**: ✅ Complete (Character Creation System)
- **Phase 3**: ✅ Complete (Core Game Loop)
- **Phase 4**: 🟡 In Progress (Advanced Features & Polish)
- **Frontend**: Running on http://localhost:3000
- **Backend**: Running on http://localhost:8000
- **Database**: Local Supabase with simplified schema
- **Status**: ✅ Core game flow fully working (character creation → game session → story generation)

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

### plan.md Best Practices
- **Update Frequency**: Update after completing each task or at end of each work session
- **Status Tracking**: Use emojis (🔴 Not Started, 🟡 In Progress, 🟢 Complete)
- **Date Updates**: Always update "Last Updated" date when making changes
- **Checkboxes**: Use `- [ ]` for tasks, mark with `- [x]` when complete
- **Phase Management**: Only detail current and next phase, keep future phases high-level
- **Blockers**: Document any blockers in Notes section immediately
- **Progress Overview**: Keep summary section current with overall project status

### Planning Guidelines
- Use `plan.md` for major feature planning with checkpoints
- Track progress systematically
- Focus on MVP features first, then stretch goals
- Break complex tasks into smaller, actionable items
- Review and adjust priorities daily

## API Limits & Notes
- Gemini API: 100 requests per project per day (free tier)
- Use free tier API key for hackathon
- Paid keys will incur charges for all usage

## Visual Development & Testing

### MCP Playwright Integration
- **Purpose**: Visual feedback and frontend development verification
- **Usage**: ALWAYS use Playwright when working on frontend components or UI
- **Workflow**: 
  1. Make frontend changes
  2. Use `mcp__playwright__playwright_navigate` to open http://localhost:3000
  3. Use `mcp__playwright__playwright_screenshot` to capture current state
  4. Analyze screenshot for UI correctness, layout, and styling
  5. Iterate based on visual feedback
- **Benefits**: Immediate visual validation of changes, catch UI regressions, verify responsive design

### Frontend Development Protocol
1. **Before Changes**: Take baseline screenshot of current UI
2. **After Changes**: Take updated screenshot to compare
3. **Analysis**: Review both screenshots to ensure improvements
4. **Testing**: Use Playwright to interact with UI elements and verify functionality

## Specialized Agents

### Agent Usage Guidelines
- **Frequency**: Use specialized agents OFTEN - they are optimized for specific tasks
- **Parallel Execution**: Launch multiple agents simultaneously when tasks are independent
- **Proactive Usage**: Don't wait for explicit requests - use agents whenever their expertise applies
- **Examples of Parallel Usage**:
  - Launch Robert for DB queries + Chuck Norris for code debugging simultaneously
  - Run Babcia for DevOps checks + Kasia for API docs in parallel
  - Deploy Sun Tzu for planning while Robert checks database schema

### Available Agents (call by name):
- **Babcia/Babcia Stasia**: DevOps agent for verifying configurations, service connections, API keys, and environment setups
  - Use for: Environment variables, API key validation, deployment issues, service connections
- **Chuck Norris**: Complex coding challenges, debugging, and elegant refactoring solutions
  - Use for: Difficult bugs, performance optimization, complex algorithms, DRY refactoring
- **Robert**: Database operations specialist for Supabase queries, migrations, and schema management
  - Use for: All database operations, migrations, schema validation, data consistency checks
- **Kasia**: API documentation collector for external API integration docs
  - Use for: Gemini API, Nano Banana API, ElevenLabs integration, any external service docs
- **Sun Tzu**: Strategic planning for code changes, refactoring, and architectural decisions
  - Use for: Major features, complex refactoring, architectural changes, implementation strategies

### When to Use Agents in Parallel
1. **Multi-aspect debugging**: Chuck Norris (code) + Robert (database) + Babcia (environment)
2. **Feature implementation**: Sun Tzu (planning) + Kasia (API docs) simultaneously
3. **System verification**: Babcia (configs) + Robert (DB health) in parallel
4. **Documentation gathering**: Multiple Kasia instances for different APIs