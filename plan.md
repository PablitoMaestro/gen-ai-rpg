# AI Hero's Journey - Development Plan

## Summary
**Project**: AI-powered first-person RPG with dynamic story generation and character imagery  
**Status**: 🔴 Not Started  
**Current Phase**: Project Setup  
**Last Updated**: 2025-01-06  

### Progress Overview
- [ ] Phase 1: Project Setup & Infrastructure
- [ ] Phase 2: Character Creation System  
- [ ] Phase 3: Core Game Loop
- [ ] Phase 4: API Integrations
- [ ] Phase 5: Polish & Deployment

---

## Phase 1: Project Setup & Infrastructure (Current)

### 1.1 Repository Structure ✅
- [x] Create folder structure
- [x] Initialize git with main/dev branches
- [x] Create CLAUDE.md for AI guidance
- [x] Create plan.md with detailed roadmap

### 1.2 Frontend Setup
- [ ] Initialize Next.js in `/frontend` with TypeScript template
- [ ] Install core dependencies (zod, zustand, tailwind)
- [ ] Configure strict TypeScript settings
- [ ] Set up ESLint with strict rules
- [ ] Create base folder structure:
  - `/components` - Reusable UI components
  - `/services` - API communication layer
  - `/store` - Zustand state management
  - `/types` - TypeScript definitions
  - `/utils` - Helper functions
  - `/hooks` - Custom React hooks
- [ ] Configure Tailwind for dark fantasy theme
- [ ] Set up environment variables structure

### 1.3 Backend Setup
- [ ] Initialize FastAPI project in `/backend`
- [ ] Create folder structure:
  - `/services` - Business logic
  - `/models` - Pydantic models
  - `/api` - Route handlers
  - `/scripts` - Utility scripts
  - `/config` - Configuration management
- [ ] Set up async support throughout
- [ ] Configure CORS for frontend communication
- [ ] Set up environment variables handling
- [ ] Create health check endpoint

### 1.4 Database Setup
- [ ] Initialize Supabase in `/supabase` folder
- [ ] Start local Supabase instance with Docker (follow official Supabase commands, use Kasia to check via Ref MCP for Supabase docs)
- [ ] Create initial migration for:
  - `characters` table (id, user_id, name, gender, portrait_url, full_body_url, stats)
  - `character_portraits` table (id, gender, portrait_url, is_preset)
  - `game_sessions` table (id, character_id, current_scene, choices_made, created_at)
- [ ] Set up storage bucket for character images
- [ ] Configure RLS policies

### 1.5 Development Environment
- [ ] Create `.env.example` files for all services
- [ ] Set up development scripts in root package.json
- [ ] Configure VS Code workspace settings
- [ ] Document local development setup

---

## Phase 2: Character Creation System

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