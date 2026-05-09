# RECREATE PROMPT — AI-Illustrated RPG (Nano Banana Hackathon Edition, Improved)

> **How to use this file:** Paste this whole document into a strong coding model (Claude Opus, GPT-5, Gemini 2.5 Pro, etc.) and ask it to "build this game from scratch but better." The first half is a copy-pasteable PROMPT. The second half is a TECHNICAL APPENDIX with exact tables, prompts, IDs, and constants the model will need.

---

## SECTION A — THE PROMPT (paste this into your AI)

### 0. Mission

Build a single-player AI-illustrated branching narrative RPG called **"AI Hero's Journey."** It is a dark medieval-fantasy choose-your-own-adventure where every scene's image, narration text, and voice audio are generated on demand by AI, while the protagonist's **face stays visually consistent across every scene** ("Visual DNA"). The player picks a portrait, names their character, picks a class build, and then plays through a branching first-person narrative driven by 4 choices per scene.

The original is a hackathon prototype. **Recreate it with production-quality polish:** smoother animations, better audio mixing, real save/load, robust error handling, mobile-first responsive design, and a cleaner state model. Keep the core innovation (Visual DNA via Gemini image fusion) intact — that's the soul of the game.

### 1. High-level architecture (keep it three-tier)

```
┌──────────────────┐  HTTPS  ┌──────────────────┐  HTTPS  ┌─────────────────┐
│  Next.js 15 SPA  │◄───────►│  FastAPI Backend │◄───────►│  Supabase       │
│  (Vercel)        │         │  (Scaleway/Fly)  │         │  Postgres+Storage│
└──────────────────┘         └──────────────────┘         └─────────────────┘
                                      │
                              ┌───────┴────────┬─────────────┐
                              ▼                ▼             ▼
                       Gemini 2.5 Flash   Gemini 2.0     ElevenLabs
                       Image (images)     Flash (text)   (voice TTS)
```

**Hard rules:**
- The frontend NEVER calls Gemini or ElevenLabs directly. All AI calls go through the backend so API keys stay server-side and rate limits are centrally managed.
- Models are defined in **one Pydantic file** on the backend (`backend/models.py`) and mirrored in **one TypeScript types file** on the frontend (`frontend/src/types/index.ts`). No DTO/entity split.
- All scene generation must be **async + parallelizable** (`asyncio.gather`). FastAPI is async — never introduce sync I/O in request paths.

### 2. Tech stack (use these exact versions or newer)

**Frontend** — Next.js 15 (App Router) + React 19 + TypeScript 5 (strict) + Tailwind CSS 3.4 + Zustand 5 (state) + Zod 4 (runtime validation). No external component library — hand-rolled with Tailwind. Fonts: Cinzel + Uncial Antiqua + Metamorphous + Geist Sans/Mono.

**Backend** — FastAPI 0.115 + Pydantic 2.10 + httpx 0.27 (async HTTP) + supabase-py 2.10 + google-generativeai 0.8 + Pillow 11. Python 3.11+. Strict mypy + Ruff (line-length 100, rules I/B/UP).

**Database** — Supabase (Postgres + Storage + Auth). Migration-driven schema. RLS on every user-owned table. Storage bucket `character-images` (public, 50 MB limit, image/png|jpeg|webp).

**AI services** —
- **Google Gemini API** (`google-generativeai` SDK)
  - Text: `gemini-2.0-flash-exp` for narration + choices
  - Image: `gemini-2.5-flash-image-preview` (codename "Nano Banana") for character + scene fusion
- **ElevenLabs API** (raw HTTPS, no SDK needed)
  - Narration: `eleven_monolingual_v1` (or upgrade to `eleven_turbo_v2_5` for latency)
  - Voice design: `eleven_ttv_v3` for per-character custom voices

### 3. The Visual DNA pipeline (the core feature — get this right)

This is what makes the game special. The player's hero has a face that never changes, even though every scene image is freshly generated.

**Step 1 — Portrait selection.** Ship 8 hand-picked portraits (4 male `m1-m4`, 4 female `f1-f4`) stored in Supabase Storage. Each portrait has **hardcoded character traits** (age, expression, eye color, skin tone, hair, clothing) — see Appendix B for the exact dictionary. These traits are injected as text into every downstream image-generation prompt to anchor consistency.

**Step 2 — Pre-generated builds.** Before a single user logs in, run a batch script that generates all **32 portrait × class combinations** (8 portraits × 4 classes: warrior / mage / rogue / ranger). Each combination produces a full-body image where the portrait's face is fused with that class's armor/weapons. Store these in a `character_builds` table keyed by `(portrait_id, build_type)`. This means class selection is instantaneous — no waiting for image generation.

**Step 3 — Pre-generated first scenes.** Also pre-generate the **32 opening scenes** (one per portrait+build combo) in a `first_scenes` table. Each contains narration text, image URL, audio URL, and 4 choices. Story prompt premise: protagonist wakes up unconscious in a forest after a bandit attack with amnesia (this hook is amnesia-driven on purpose — it explains the player not knowing context).

**Step 4 — Live branching with parallel pre-generation.** Once gameplay starts, the player sees a scene with 4 choices. The moment that scene loads, the backend kicks off **4 parallel scene generations in the background** — one per choice — using `asyncio.gather`. Results stream back into a `Map<choiceId, Scene>` on the client. When the user clicks a choice, the next scene is already cached and renders instantly. If a generation failed (safety filter, rate limit), fall back to live generation on click. Each scene generation includes:
- Narration text (Gemini text)
- Scene image (Gemini image, fed the character's full-body URL + scene description)
- Voice narration audio (ElevenLabs, character-specific voice ID)

**Improve over the original:**
- Add a **scene cache** keyed by `(character_id, scene_hash)` so revisits are free.
- Stream narration text token-by-token to the client (SSE) instead of waiting for full response.
- Use a **prompt-cached system message** for Gemini that contains the world bible + character description, so each call is shorter and cheaper.

### 4. Gameplay loop

1. **Landing page (`/`)** — Hero title "AI Hero's Journey" over a video/image background. Two CTAs: "Begin Your Quest" and "Resume Adventure" (loads from save).
2. **Character creation (`/character/create`)** — Pick gender → pick portrait from horizontal scroller (8 presets + "upload custom" option) → name (max 50 chars) → personality blurb (max 500 chars). Tapping a preset portrait plays a short ElevenLabs-voiced intro line ("Quick fingers, quicker wit…") so the player can hear the voice before committing.
3. **Build selection (`/character/builds`)** — Show 4 class cards (warrior/mage/rogue/ranger), each with the pre-generated full-body image, description, and stats preview (STR/INT/AGI). Selecting one creates the character record in DB and assigns the matching ElevenLabs voice ID.
4. **Game start (`/game/start`)** — Recap card: portrait, name, class, level 1, HP 100. "Begin Your Adventure" button calls the backend `/api/stories/first-scene/{portrait_id}/{build_type}` which returns the cached opening scene instantly.
5. **Game loop (`/game/[sessionId]`)** — Full-screen scene image (70vh) with vignette + dark gradient overlay. Narration appears in a translucent box at the bottom with a typewriter effect (30 ms/char). Audio plays automatically (respect autoplay policy — mute by default if blocked, show un-mute prompt). Below the narration: 4 choice cards styled as colored thought bubbles (red=aggressive, purple=reckless, blue=strategic, orange=defensive). Each card has a green dot when its branch is pre-generated. A persistent HUD top-left shows HP/XP bars + character avatar; bottom-right has volume controls.
6. **Endings & checkpoints** — Scenes carry `is_combat`, `is_checkpoint`, `is_final` flags. Improve over the original: actually use these flags to (a) trigger a dice-roll combat overlay on `is_combat`, (b) auto-save game state on `is_checkpoint`, (c) show a stylized epilogue + "share your story" card on `is_final`.

### 5. UI / design system

**Aesthetic:** dark medieval candlelit chamber. Muted brown-black backgrounds with warm amber accents and selective splashes of blood-red (tension), royal purple (magic), forest green (nature), celestial blue (mystical).

**Typography hierarchy:**
- Hero titles: `font-manuscript` (Uncial Antiqua) with gold gradient + glow text-shadow
- Headers: `font-fantasy` (Cinzel) — classic medieval serif
- Body: `font-sans` (Geist Sans)
- Numbers/stats: `font-mono` (Geist Mono)

**Animation language:** slow, deliberate, atmospheric. Pulses (3–4s), gentle floats (8s), shimmering gold streaks across buttons (3s), heartbeat scales (1.05x), critical-HP red flicker. **No jarring transitions, no bouncy springs.** Hover states amplify glow shadows; active states use `scale-95` for tactile feedback.

**Color tokens** (use these as Tailwind extends — see Appendix C for full palette):
- `primary` = amber scale (#fffef7 → #451a03)
- `gold` = #FFB800 / #FCD34D / #F59E0B (most-used)
- `blood` = red scale, narration accents + danger
- `royal` = purple scale, magic indicators
- Body bg: `linear-gradient(180deg, #0a0a0a 0%, #1a1410 40%, #2d1b00 70%, #1a2f1a 100%)` plus radial glow overlays at 20%/20% (gold) and 80%/80% (green).

**Custom Tailwind shadows:** `glow`, `golden`, `golden-lg`, `ember`, `celestial`, `nature`, `hope`, `blood`. These give every button/card a candlelight halo.

**Component primitives to build:**
- `Button` (variants: primary | secondary | ghost | danger)
- `LoadingSpinner` (sm/md/lg/xl, gold theme)
- `StoryDisplay` (image + narration + audio player + typewriter)
- `ChoiceSelector` (4-card grid, thought-bubble shapes, green-dot ready indicator)
- `GameStats` (fixed HUD with HP/XP/level)
- `VolumeControl` (dual vertical sliders for music + narration)
- `MuteToggle`, `HeroPortraitPreview` (ornate corner-decorated frame)
- `BackgroundLayout` (video bg + dark overlay + magical light effects)

### 6. State management

**Frontend (Zustand):**
- `gameStore`: `character`, `session`, `currentScene`, `sceneHistory[]` (last 10), `choiceHistory[]` (last 20), `pregeneratedBranches: Map<choiceId, Scene>`. Persist to localStorage as `game-save`.
- `audioStore`: `masterMuted`, `musicMuted`, `narrationVolume`, `musicVolume`.

**Backend** keeps no in-memory session state (stateless FastAPI). All state persists in Supabase tables.

### 7. Improve over the original

The original is a hackathon MVP. Your job is to ship a polished version. Specifically:

- **Real auth.** The original has a hardcoded test user. Wire up Supabase Auth (email magic link + Google OAuth). RLS policies are already designed for `auth.uid() = user_id`.
- **Real save/load.** Currently localStorage-only. Add `game_sessions` row updates on every choice + a `/saves` page that lists past adventures with thumbnail.
- **Streaming narration.** Use SSE or WebSockets to stream Gemini text token-by-token. The current typewriter effect fakes streaming on already-loaded text.
- **Smarter caching.** Add a Redis (or Supabase KV) layer in front of `character_builds` and `first_scenes`. Add a `(character_id, scene_hash)` cache for live branches.
- **Combat scenes.** When `is_combat=true`, overlay a stylized 3D dice roll (Three.js + cannon-es) that resolves to a number, then feed the number back into the next prompt.
- **Mobile-first.** The original is desktop-leaning. Use container queries, touch-friendly hit areas (≥44px), and a bottom sheet pattern for choices on mobile.
- **Telemetry.** Add PostHog or similar to capture which choices are popular per scene — this data can later train a finetune.
- **Cost guardrails.** Show the player a soft credit meter (Gemini free tier is 100 req/day). Pre-generation should be capped per session.
- **Accessibility.** Add full keyboard navigation, ARIA labels, focus rings, captions for narration audio (use Whisper or send the text).
- **Better safety retry.** Original has 3 retries with hardcoded swaps ("blood" → "red marks"). Improve with an LLM-based rewriter that preserves narrative tone.

### 8. Folder structure

```
/frontend
  /src/app           → Next.js routes (page.tsx per route)
  /src/components    → UI components (PortraitSelector, StoryDisplay, ChoiceSelector, GameStats, ...)
  /src/store         → Zustand stores
  /src/services      → apiService (single fetch wrapper), audio manager
  /src/types         → mirrors backend/models.py (Character, Scene, Choice, ...)

/backend
  /api               → routers: health, characters, stories, images, test (dev-only)
  /services          → gemini.py, elevenlabs.py, supabase.py, scene_pregenerator.py,
                        image_processor.py, content_sanitizer.py, voice_design.py,
                        portrait_dialogue.py
  /scripts           → generate_all_builds.py, generate_first_scenes.py, seed_voices.py
  /tests             → pytest, with /test/* endpoints auto-mounted only in dev
  models.py          → ALL Pydantic models live here, plus PRESET_PORTRAITS + PORTRAIT_CHARACTERISTICS

/supabase
  /migrations        → numbered SQL migrations (timestamps prefixed)
  /character-images  → seeded preset portraits + builds
  seed.sql           → test users + sample characters
```

### 9. Required environment variables

See **Section C — Required user-provided assets** below for the full list and where to obtain each.

### 10. Acceptance criteria

The recreate is "done" when:
- A new user can land → create character → pick build → play 5 scenes → save → reload → resume from scene 5, all without touching the dev console.
- All 32 first-scenes load in **< 200 ms** (cache hit).
- Branch pre-generation completes in **< 8 s** for all 4 choices in parallel.
- TypeScript + Python typecheck pass with strict settings. ESLint + Ruff pass clean.
- Lighthouse mobile score ≥ 90 on the landing page.
- A 30-second gameplay video can be recorded with no visible loading spinners between choices.

---

## SECTION B — TECHNICAL APPENDIX (data the model needs to build it correctly)

### Appendix A — Database schema (Postgres / Supabase)

```sql
-- Migration 1: characters
CREATE TABLE characters (
  id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id     UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name        TEXT NOT NULL CHECK (char_length(name) BETWEEN 1 AND 50),
  gender      TEXT CHECK (gender IN ('male','female')),
  portrait_url TEXT NOT NULL,
  full_body_url TEXT NOT NULL,
  build_type  TEXT CHECK (build_type IN ('warrior','mage','rogue','ranger')) DEFAULT 'warrior',
  voice_id    TEXT,                     -- ElevenLabs voice id
  personality TEXT,
  hp          INT  DEFAULT 100 CHECK (hp BETWEEN 0 AND 200),
  xp          INT  DEFAULT 0,
  level       INT  DEFAULT 1 CHECK (level BETWEEN 1 AND 100),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE characters ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own characters" ON characters FOR ALL USING (auth.uid() = user_id);

-- Migration 2: game_sessions
CREATE TABLE game_sessions (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  character_id  UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
  current_scene JSONB DEFAULT '{}',
  choices_made  JSONB[] DEFAULT ARRAY[]::JSONB[],
  inventory     JSONB DEFAULT '[]',
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Migration 3: character_builds (32 rows total: 8 portraits × 4 classes)
CREATE TABLE character_builds (
  id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  portrait_id  TEXT NOT NULL,
  build_type   TEXT NOT NULL CHECK (build_type IN ('warrior','mage','rogue','ranger')),
  image_url    TEXT NOT NULL,
  description  TEXT NOT NULL,
  stats_preview JSONB DEFAULT '{"strength":10,"intelligence":10,"agility":10}',
  UNIQUE(portrait_id, build_type)
);

-- Migration 4: first_scenes (32 rows total — one opening per portrait×build)
CREATE TABLE first_scenes (
  portrait_id   TEXT NOT NULL CHECK (portrait_id ~ '^[mf][1-4]$'),
  build_type    TEXT NOT NULL CHECK (build_type IN ('warrior','mage','rogue','ranger')),
  narration     TEXT NOT NULL,
  visual_scene  TEXT NOT NULL,
  image_url     TEXT,
  audio_url     TEXT,
  choices       JSONB DEFAULT '[]',
  generated_at  TIMESTAMPTZ DEFAULT NOW(),
  retry_count   INT DEFAULT 0 CHECK (retry_count >= 0),
  last_error    TEXT,
  is_successful BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (portrait_id, build_type)
);
```

Storage bucket: `character-images` — public, 50 MB limit, MIME `image/png,image/jpeg,image/webp`. Storage RLS: users can write only under `{user_id}/...`.

### Appendix B — `PORTRAIT_CHARACTERISTICS` (paste verbatim into `backend/models.py`)

These traits are injected into every Gemini image prompt to enforce face consistency. **Do not edit them lightly** — the visual coherence depends on these exact phrases.

| ID | Age | Expression | Eyes | Skin | Hair | Clothing |
|----|-----|------------|------|------|------|----------|
| m1 | early twenties | manic euphoria with wide eyes and unsettling grin | brown eyes gleaming with fervor | weathered skin flushed | dark brown hair disheveled, stubble | brown tunic |
| m2 | around 40 | deep melancholic sorrow with tears welling | brown eyes filled with grief | weathered skin | dark brown beard with gray | brown leather |
| m3 | late twenties | burning rage with clenched jaw and flared nostrils | gray-brown eyes blazing with fury | pale skin tense | dark brown unkempt hair, scar through eyebrow, stubble | gray-brown cloak |
| m4 | in sixties | profound terror with wide fearful eyes and parted lips | gray eyes showing panic | wrinkled skin pale with dread | gray-white hair, gray beard | dark brown robe |
| f1 | early twenties | ecstatic revelation with eyes wide in wonder | brown eyes sparkling with awe | fair skin with freckles glowing | dark brown hair with simple coif | beige dress |
| f2 | around 35 | bitter contempt with narrowed eyes and curled lip | brown eyes cold with disdain | weathered skin | dark brown hair with veil | brown wool |
| f3 | late twenties | desperate anguish with trembling lips, eyes brimming with tears | gray-brown eyes showing deep pain | pale skin with scars | dark brown unkempt hair | gray-brown torn fabric |
| f4 | in sixties | sinister amusement with knowing smirk and glinting eyes | gray eyes with cataracts showing dark humor | wrinkled weathered skin | gray hair under wimple | dark brown shawl |

### Appendix C — Tailwind theme tokens (verbatim from original `tailwind.config.ts`)

```ts
extend: {
  colors: {
    primary: { 50:'#fffef7', 500:'#f59e0b', 900:'#451a03' /* full amber scale */ },
    secondary: { 500:'#22c55e', /* full green scale */ },
    blood:    { 500:'#ef4444', 900:'#7f1d1d', 950:'#450a0a' },
    royal:    { 500:'#a855f7', 900:'#581c87', 950:'#3b0764' },
    gold:     { 300:'#FCD34D', 400:'#FFB800', 500:'#F59E0B' },
    celestial:{ 500:'#0ea5e9' },
    dark:     { /* gray scale 50–950 */ }
  },
  fontFamily: {
    sans: ['var(--font-geist-sans)', 'system-ui', 'sans-serif'],
    mono: ['var(--font-geist-mono)', 'monospace'],
    fantasy:    ['Cinzel','serif'],
    manuscript: ['Uncial Antiqua','serif'],
    ornate:     ['Metamorphous','serif'],
  },
  backgroundImage: {
    'dark-gradient':     'linear-gradient(180deg, #0a0a0a 0%, #1a1410 40%, #2d1b00 70%, #1a2f1a 100%)',
    'medieval-gradient': 'linear-gradient(135deg, #451a03 0%, #664500 25%, #7c3aed 50%, #b45309 75%, #ffb800 100%)',
    'hope-gradient':     'linear-gradient(135deg, #451a03 0%, #92400e 30%, #f59e0b 70%, #fcd34d 100%)',
    'blood-gradient':    'linear-gradient(135deg, #450a0a 0%, #7f1d1d 50%, #991b1b 100%)',
    'royal-gradient':    'linear-gradient(135deg, #3b0764 0%, #581c87 30%, #7c3aed 70%, #a855f7 100%)',
  },
  boxShadow: {
    'glow':       '0 0 20px rgba(245,158,11,0.4)',
    'glow-lg':    '0 0 30px rgba(245,158,11,0.6)',
    'golden':     '0 0 25px rgba(255,215,0,0.5)',
    'golden-lg':  '0 0 40px rgba(255,215,0,0.7)',
    'ember':      '0 0 20px rgba(234,88,12,0.5)',
    'celestial':  '0 0 25px rgba(14,165,233,0.5)',
    'nature':     '0 0 20px rgba(34,197,94,0.4)',
    'blood':      '0 0 25px rgba(220,38,38,0.5)',
  },
  keyframes: {
    float:     { '0%,100%':{transform:'translateY(0)'}, '50%':{transform:'translateY(-20px)'} },
    shimmer:   { '0%':{backgroundPosition:'-200%'}, '100%':{backgroundPosition:'200%'} },
    glowWarm:  { '0%,100%':{transform:'scale(1)'}, '50%':{transform:'scale(1.02)',boxShadow:'0 0 30px rgba(255,215,0,0.6)'} },
    flicker:   { '0%,100%':{opacity:'1'}, '50%':{opacity:'0.8'} },
    fadeIn:    { '0%':{opacity:'0'}, '100%':{opacity:'1'} },
    heartbeat: { '0%,100%':{transform:'scale(1)'}, '50%':{transform:'scale(1.05)'} },
  },
  animation: {
    'float': 'float 6s ease-in-out infinite',
    'shimmer': 'shimmer 3s linear infinite',
    'glow-warm': 'glowWarm 2s ease-in-out infinite',
    'pulse-gentle': 'pulse 4s ease-in-out infinite',
    'float-gentle': 'float 8s ease-in-out infinite',
    'flicker': 'flicker 1.5s ease-in-out infinite',
    'fade-in': 'fadeIn 0.5s ease-out',
    'heartbeat': 'heartbeat 1.2s ease-in-out infinite',
  }
}
```

### Appendix D — Gemini prompt templates

**Story generation (text)** — model `gemini-2.0-flash-exp`. Prompt premise (initial scene): protagonist wakes up unconscious in a forest after a bandit attack, head pain, blurry vision, robbed. First-person internal monologue with extreme emotional states (terrified, determined, confused, desperate, cautiously optimistic). The model is instructed to output labeled sections:

```
NARRATION: <250-400 words, first-person internal monologue>
VISUAL_SCENE: <150-250 words, third-person scene description for image gen>
CHOICE_1: <aggressive option, 1 sentence>
CHOICE_2: <reckless option, 1 sentence>
CHOICE_3: <strategic option, 1 sentence>
CHOICE_4: <defensive option, 1 sentence>
```

Parse with regex `^(?:.*?):\s*(.+?)(?=\n(?:VISUAL_SCENE|CHOICE_\d):|\Z)`.

Apply **safety settings** with all categories `BLOCK_ONLY_HIGH` (or `BLOCK_NONE` if your account allows — many medieval-fantasy scenes will trip default safety).

**Character image generation** — model `gemini-2.5-flash-image-preview`. Pass the portrait image bytes as input. Prompt template per build:

```
Create a realistic full-body {gender} {build_type} based on this portrait.
Person {age}, {eye_color}, {skin}, {hair}.
{build-specific armor/weapon line}.
{build-specific stance line}.
Photorealistic style.
```

Build-specific lines (verbatim from original):
- **warrior** — "Worn, patched mail armor with weathered surface, simple iron sword and dented wooden shield. Average build, adapting portrait expression to show determination, confident posture from training."
- **mage** — "Faded, patched robes with worn fabric, simple wooden staff with crystal. Thin build, scholarly focus, upright posture."
- **rogue** — "Patched leather armor with visible repairs, simple iron daggers. Wiry build, alertness and confidence, ready stance."
- **ranger** — "Worn leather and rough cloth, simple hunting bow with weathered string. Lean build, cautious alertness."

**Scene image generation** — same image model, fed two images: the full-body character image + a generated background. Prompt template: "Place the character {character_description} into this scene: {visual_scene}. Maintain face, body, and clothing exactly. Photorealistic medieval fantasy style."

### Appendix E — ElevenLabs configuration

**Narration** (`POST /v1/text-to-speech/{voice_id}`):
```json
{
  "text": "<narration text>",
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.75,
    "similarity_boost": 0.75,
    "style": 0.5,
    "use_speaker_boost": true
  }
}
```
Output: MP3 binary. HTTP timeout 30 s. Default fallback voice = Rachel (`21m00Tcm4TlvDq8ikWAM`).

**Voice design** (`POST /v1/convert/text-to-voice`, model `eleven_ttv_v3`):
```json
{
  "voice_description": "<extreme-trait description per portrait, see below>",
  "text": "<sample dialogue>",
  "output_format": "mp3_44100_192",
  "guidance_scale": 5.0,
  "seed": <hash(character_id) % 100000>   // reproducible per character
}
```

**Default portrait→voice mapping** (replace with your own custom-cloned voices for higher quality):
| Portrait | Default ElevenLabs voice ID | Voice descriptor |
|----------|------------------------------|-----------|
| m1 | `TxGEqnHWrfWFTfGW9XjX` (Josh)    | mischievous young thief, high-pitched, nasal cocky undertones |
| m2 | `D38z5RcWu1voky8WS1ja` (Ethan)   | battle-worn middle-aged warrior, deep gravelly, trembling sorrow |
| m3 | `IKne3meq5aSn9XLyUdCD` (Charlie) | aggressive young fighter, raspy growling fury |
| m4 | `onwK4e9ZLuTAKqWW03F9` (Daniel)  | ancient wise elder, mystical gravelly, long pauses |
| f1 | `AZnzlk1XvdvUeBnXmlld` (Domi)    | wide-eyed wonder, light, breathless awe |
| f2 | `EXAVITQu4vr4xnSDxMaL` (Sarah)   | bitter middle-aged contempt, narrow cold tone |
| f3 | `oWAxZDx7w5VEj9dCyTzz` (Grace)   | desperate anguish, trembling, broken |
| f4 | `VruXhdG8YF3HISipY3rg` (custom)  | sinister grandmother, cackling knowing |

### Appendix F — Class definitions

| Class | Description | Stats {STR/INT/AGI} | HP per level |
|-------|-------------|---------------------|--------------|
| warrior | Weary soldier in patched mail armor, struggling to make ends meet | 15 / 8 / 10  | base 100 + 15·(lvl-1) |
| mage    | Frustrated scholar with mediocre magical talent and worn robes    | 8 / 15 / 10  | base 100 + 8·(lvl-1)  |
| rogue   | Common street thief with nervous demeanor and patched leathers    | 10 / 10 / 15 | base 100 + 10·(lvl-1) |
| ranger  | Simple tracker with weather-beaten gear and humble skills         | 12 / 10 / 13 | base 100 + 12·(lvl-1) |

Leveling: `level = min(100, max(1, (xp // 100) + 1))`.

### Appendix G — Content sanitizer (improve, don't copy)

Original uses regex replacements. **Recommend replacing with an LLM rewriter** that preserves narrative tone. Keep the regex layer as a fallback. Original replacement pairs (selection):

```
blood→red marks, bleeding→wounded, corpse→fallen figure, kill→defeat,
murder→conflict, death→end, die→fall, war→conflict, battle→encounter,
fight→challenge, zombie→undead figure, cursed→enchanted, pain→discomfort,
extremely→very, terribly→very, horribly→very
```

Plus full-rejection patterns that block image generation entirely: `execution|torture|mutilate|disembowel|cannibal|suicide|homicide|genocide`.

Retry logic for image safety failures (3 attempts, exponential backoff `[2, 5, 10]`s):
1. First retry — sanitize via regex
2. Second retry — apply specific narrative swaps ("bandit attack" → "unexpected event", "unconscious" → "resting")
3. Third retry — fall back to ultra-safe generic scene description

### Appendix H — API endpoints (FastAPI router prefixes mounted in `main.py`)

| Method | Path | Purpose |
|--------|------|---------|
| GET    | /api/health | Liveness check |
| POST   | /api/characters/builds | Generate 4 builds for a portrait (parallel Gemini calls) |
| POST   | /api/characters/create | Create character row (assigns voice_id from portrait_id) |
| GET    | /api/characters/{id} | Fetch character |
| POST   | /api/stories/first-scene/{portrait_id}/{build_type} | Get cached opening scene (fall back to live generate) |
| POST   | /api/stories/generate | Generate next scene given character + previous choice |
| POST   | /api/stories/branches/prerender | Generate next 4 branches in parallel; returns array of `{choice_id, is_ready, scene}` |
| POST   | /api/images/portrait-dialogue | Generate ElevenLabs intro audio for a portrait (used during character creation) |
| POST   | /api/test/* | Dev-only smoke endpoints (auto-mounted when `ENVIRONMENT=development`) |

CORS: `*` in dev, hardcoded Vercel domain list in prod (see `backend/main.py`).

---

## SECTION C — REQUIRED USER-PROVIDED ASSETS (everything you must supply before the app can be built autonomously)

### 🔑 API Keys (mandatory — cannot run without these)

| # | Variable | Where to obtain | Notes |
|---|----------|-----------------|-------|
| 1 | `GEMINI_API_KEY` | https://aistudio.google.com/apikey | Free tier = 100 req/day. Pay-as-you-go for more. |
| 2 | `ELEVENLABS_API_KEY` | https://elevenlabs.io → Profile → API Keys | Pricing varies; voice cloning needs Creator tier+. |
| 3 | `SUPABASE_URL` | https://supabase.com → Project Settings → API | Format: `https://<ref>.supabase.co` |
| 4 | `SUPABASE_ANON_KEY` | Same page | Public-safe, used by frontend & for SELECT under RLS. |
| 5 | `SUPABASE_SERVICE_KEY` | Same page (Service Role Key) | **NEVER ship to client.** Backend only. Bypasses RLS. |
| 6 | `NEXT_PUBLIC_API_URL` | Your backend deployment URL | e.g., `https://api.yourgame.com`. Default `http://localhost:8000` for local. |

Optional:
- `SUPABASE_DB_PASSWORD` (for `supabase db push` to remote)
- `SUPABASE_PROJECT_ID`, `SUPABASE_ACCESS_TOKEN` (for CLI ops)

### 🖼️ Image assets (must be uploaded to Supabase Storage `character-images/presets/`)

| Required file | Path | Source |
|---------------|------|--------|
| 8 portrait images (m1-m4, f1-f4) | `presets/male/male_portrait_0[1-4].png`, `presets/female/female_portrait_0[1-4].png` | **You must provide these.** Original used midjourney-generated medieval portraits. Recommended: 1024×1024 PNG, photorealistic medieval style, head-and-shoulders crop, varied ages/expressions. The hardcoded `PORTRAIT_CHARACTERISTICS` in Appendix B describes each portrait's expected vibe. |
| (Optional) Custom landing video | `frontend/public/intro-background.mp4` | Optional looping background video for landing page. |
| (Optional) Background music | `frontend/public/game-background-music.mp3` | Optional ambient medieval loop. Royalty-free recommended. |
| (Optional) Sample scene fallback | `frontend/public/scenes/forest_awakening.jpg` | Fallback image if scene generation fails. |

> ⚠️ **The 8 portraits are the most critical asset.** Their visual style + the trait dictionary together define the visual DNA. If your portraits don't match the descriptors (e.g., you ship a portrait of a smiling young woman but `f3` says "desperate anguish, scars"), the generated full-body images will be inconsistent.

### 🎤 Voice assets (optional — defaults work but quality is generic)

You have **three options** ranked by quality:

| Option | Effort | Quality | What to provide |
|--------|--------|---------|-----------------|
| **A. Use defaults** | Zero | Medium | Nothing. The 8 ElevenLabs default voice IDs in Appendix E will work out of the box. |
| **B. Use ElevenLabs voice design** | Low | High | Nothing extra — the `eleven_ttv_v3` API generates a custom voice from each portrait's text descriptor and seeds it deterministically. Just enable in code. |
| **C. Clone real voices** | High | Highest | Provide 8 voice samples (≥30 seconds each, single speaker, clean audio). Upload to ElevenLabs voice cloning. Save the resulting voice IDs into `backend/services/portrait_dialogue.py:voice_mappings`. |

For option C, you'd need 8 audio files (one per portrait) at ≥30 s, ideally matching the descriptor (e.g., `m4` should be an old gravelly male voice). MP3 or WAV.

### 🎮 Pre-generation: 32 builds + 32 first scenes (auto-generated, but you must run the script)

Once API keys + portraits are in place, run:
```bash
python backend/scripts/generate_all_builds.py     # ~5-10 min, ~32 Gemini image calls
python backend/scripts/generate_first_scenes.py   # ~10-15 min, ~32 text + 32 image + 32 audio calls
```

This will populate `character_builds` (32 rows) and `first_scenes` (32 rows). Cost estimate at 2026 prices: ~$2-5 in Gemini + ~$1-3 in ElevenLabs (varies by tier).

### 🔐 Auth (Supabase)

For real users (not the test seed user), you must:
1. In Supabase dashboard → Authentication → Providers → enable Email + Google.
2. Set redirect URLs to your frontend domain.
3. (Optional) Configure custom email templates.

### 🚀 Deployment targets (all optional but recommended)

| Service | Purpose | What you provide |
|---------|---------|------------------|
| Vercel | Frontend hosting | GitHub connection + project import |
| Scaleway / Fly / Railway | Backend FastAPI container | Dockerfile (already in repo) + env vars |
| Supabase Cloud | Production DB + Storage | Project creation; run `supabase db push` to deploy migrations |

---

## SECTION D — ONE-LINE SUMMARY FOR THE BUILDER

> Build a Next.js 15 + FastAPI + Supabase three-tier RPG where a player picks one of 8 hand-crafted portraits, gets a class build (warrior/mage/rogue/ranger) with a Gemini 2.5 Flash Image-fused full-body render, and plays through a branching first-person amnesia narrative where every scene's text (Gemini 2.0 Flash), image (Gemini Image, fed the character's full-body so the face stays consistent — "Visual DNA"), and voice (ElevenLabs) are generated live but masked behind aggressive parallel pre-generation. Use the exact `PORTRAIT_CHARACTERISTICS` dict in Appendix B, the exact Tailwind tokens in Appendix C, and the exact prompt templates in Appendix D. Improve the original by adding real Supabase Auth, real save/load, SSE narration streaming, accessibility, mobile-first UI, smarter cost guardrails, and combat dice-roll overlays. Required user inputs: 5 API keys (Gemini, ElevenLabs, Supabase URL/anon/service), 8 portrait images that match the trait dictionary, and (optional) 8 voice samples for cloning.

---

*Generated from a full code analysis of `gen-ai-rpg` (branch `dev`) on 2026-05-09. Source files referenced: `backend/models.py`, `backend/services/{gemini,elevenlabs,scene_pregenerator,content_sanitizer,portrait_dialogue}.py`, `backend/api/*.py`, `frontend/src/app/**/page.tsx`, `frontend/src/components/**`, `frontend/tailwind.config.ts`, `supabase/migrations/*.sql`.*
