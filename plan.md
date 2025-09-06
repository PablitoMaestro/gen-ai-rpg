# AI Hero's Journey - Development Plan

## Summary
**Project**: AI-powered first-person RPG with dynamic story generation and character imagery  
**Status**: 🟢 Phase 1 Complete + Model Architecture Simplified  
**Current Phase**: Character Creation System  
**Last Updated**: 2025-01-06  

### Progress Overview
- [x] Phase 1: Project Setup & Infrastructure ✅
- [x] Phase 1.5: Model Architecture Simplification ✅
- [ ] Phase 2: Character Creation System (In Progress)
- [ ] Phase 3: Core Game Loop
- [ ] Phase 4: API Integrations
- [ ] Phase 5: Polish & Deployment

---

## Phase 1: Project Setup & Infrastructure ✅

### 1.1 Repository Structure ✅
- [x] Create folder structure
- [x] Initialize git with main/dev branches
- [x] Create CLAUDE.md for AI guidance
- [x] Create plan.md with detailed roadmap

### 1.2 Frontend Setup ✅
- [x] Initialize Next.js in `/frontend` with TypeScript template
- [x] Install core dependencies (zod, zustand, tailwind)
- [x] Configure strict TypeScript settings
- [x] Set up ESLint with strict rules
- [x] Create base folder structure:
  - `/components` - Reusable UI components
  - `/services` - API communication layer
  - `/store` - Zustand state management
  - `/types` - TypeScript definitions
  - `/utils` - Helper functions
  - `/hooks` - Custom React hooks
- [x] Configure Tailwind for dark fantasy theme
- [x] Set up environment variables structure

### 1.3 Backend Setup ✅
- [x] Initialize FastAPI project in `/backend`
- [x] Create folder structure:
  - `/services` - Business logic
  - `/models` - Pydantic models
  - `/api` - Route handlers
  - `/scripts` - Utility scripts
  - `/config` - Configuration management
- [x] Set up async support throughout
- [x] Configure CORS for frontend communication
- [x] Set up environment variables handling
- [x] Create health check endpoint

### 1.4 Database Setup ✅
- [x] Initialize Supabase in `/supabase` folder
- [x] Start local Supabase instance with Docker
- [x] Create initial migration for:
  - `characters` table (id, user_id, name, gender, portrait_url, full_body_url, stats)
  - `character_portraits` table (id, gender, portrait_url, is_preset)
  - `game_sessions` table (id, character_id, current_scene, choices_made, created_at)
- [x] Set up storage bucket for character images
- [x] Configure RLS policies
- [x] Create seed data with 8 preset portraits (4 male, 4 female)
- [x] Set up environment variables (.env.example and .env.local)

### 1.5 Development Environment ✅
- [x] Create `.env.example` files for all services
- [x] Set up development scripts (npm run dev in each folder)
- [x] Configure TypeScript and ESLint settings
- [x] Document setup in CLAUDE.md

---

## Phase 1.5: Model Architecture Simplification ✅

### Simplified Backend Models (2025-01-06)
- [x] Flattened database schema - removed JSONB stats column
- [x] Created single `models.py` file (down from 6 files)
- [x] Eliminated mapper functions completely
- [x] Direct model usage everywhere (no conversion layers)
- [x] Removed `character_portraits` table (using constants)
- [x] Applied database migration successfully
- [x] Verified all endpoints work with new models
- [x] **Result**: 70% less complexity, 20% less code

---

## Phase 2: Character Creation System (Current)

### 2.1 Portrait Management
- [ ] Upload 4 male and 4 female preset portraits to Supabase
- [ ] Create API endpoint to fetch preset portraits by gender
- [ ] Implement portrait selection UI component
- [ ] Add custom portrait upload functionality
- [ ] Validate and process uploaded images

### 2.2 Character Builder UI
- [ ] Design full-screen character creation interface
- [ ] Implement gender selection screen
- [ ] Create portrait selection grid (4 presets + upload option)
- [ ] Add loading states and animations
- [ ] Implement dark fantasy visual theme

### 2.3 Nano Banana Integration
- [ ] Set up Nano Banana API client in backend
- [ ] Create character generation endpoint
- [ ] Implement parallel generation of 4 full-body variants
- [ ] Add request queuing and rate limiting
- [ ] Handle API errors gracefully

### 2.4 Character Selection & Storage
- [ ] Display 4 generated character builds
- [ ] Implement selection interface with preview
- [ ] Save selected character to database
- [ ] Store character images in Supabase storage
- [ ] Create character confirmation screen

---

## Phase 3: Core Game Loop

### 3.1 Story Engine
- [ ] Integrate Gemini 2.5 Pro API
- [ ] Create story generation service
- [ ] Implement first-person narrative generation
- [ ] Structure scene descriptions for image generation
- [ ] Create branching logic for 4 choices

### 3.2 Scene Rendering
- [ ] Implement scene image generation with character
- [ ] Create scene composition service
- [ ] Handle character + environment merging
- [ ] Optimize image loading and caching

### 3.3 Choice System
- [ ] Design choice UI (4 options layout)
- [ ] Implement pre-rendering for all branches
- [ ] Create smooth transition animations
- [ ] Add choice history tracking
- [ ] Implement state updates (HP, XP, inventory)

### 3.4 Game State Management
- [ ] Design Zustand store structure
- [ ] Implement character state management
- [ ] Create scene navigation system
- [ ] Add save/load functionality
- [ ] Handle offline state persistence

---

## Phase 4: API Integrations

### 4.1 Parallel Processing
- [ ] Implement async branch generation
- [ ] Create job queue system
- [ ] Add progress tracking
- [ ] Optimize API call batching
- [ ] Handle concurrent request limits

### 4.2 ElevenLabs Integration
- [ ] Set up TTS API client
- [ ] Create narration generation service
- [ ] Implement audio playback system
- [ ] Add voice selection options
- [ ] Create audio caching strategy

### 4.3 Error Handling
- [ ] Implement retry logic for API failures
- [ ] Create fallback mechanisms
- [ ] Add user-friendly error messages
- [ ] Set up error logging and monitoring

---

## Phase 5: Polish & Deployment

### 5.1 Testing
- [ ] Write unit tests for critical functions
- [ ] Create integration tests for APIs
- [ ] Implement E2E tests for game flow
- [ ] Performance testing and optimization

### 5.2 Deployment Preparation
- [ ] Configure Vercel for frontend
- [ ] Set up Scaleway container for backend
- [ ] Configure production Supabase
- [ ] Set up environment variables
- [ ] Create deployment scripts

### 5.3 MVP Features
- [ ] Opening scene implementation (wake in woods)
- [ ] Complete one full decision loop
- [ ] XP counter system
- [ ] Basic combat mechanics (stretch)
- [ ] Inventory system (stretch)

### 5.4 Demo Preparation
- [ ] Create demo script for judges
- [ ] Prepare character presets
- [ ] Ensure smooth demo flow
- [ ] Create backup plans for failures

---

## Stretch Goals (Post-MVP)
- [ ] Combat system with stats
- [ ] Weapon progression system
- [ ] Dynamic day/night cycle
- [ ] Voice input for choices
- [ ] Multiplayer co-op mode
- [ ] Achievement system
- [ ] Character customization expansion

---

## Notes & Decisions
- Focus on MVP for hackathon submission
- Prioritize visual impact and smooth UX
- Keep architecture simple but scalable
- Document API usage for judges
- Prepare impressive demo scenarios

---

## Daily Checklist
- [ ] Update plan.md with completed tasks
- [ ] Review and adjust priorities
- [ ] Test latest changes
- [ ] Commit code with clear messages
- [ ] Document any blockers or changes