# AI RPG Hackathon Project

## Title
**AI Hero’s Journey – Interactive GenAI RPG**

---

## Core Concept
A **web-based AI role-playing game** where the player starts as a weak level-0 adventurer (inspired by Gothic 2 or Oblivion).  
The game narrates from a **first-person perspective** (“I wake up in the woods…”) and presents **branching choices**.  

Each choice leads to a new scene with:
- **Dynamic text narration** (Gemini 2.5 Pro)  
- **Consistent character images** (Nano Banana API)  
- **Scene visuals** (character rendered into the environment)  
- **Optional narration voice** (ElevenLabs TTS)  

---

## Gameplay Loop
1. **Character Creation**
   - Input: gender, face (choose from presets or upload photo), starter clothing (tattered rags), starter weapon (stick).  
   - Output: Base character portrait.  

2. **Story Begins**
   - Player wakes in the woods, confused.  
   - Narration + first rendered scene (character + forest).  

3. **Choices (always 4 options)**
   - Example:  
     1. Stand up.  
     2. Rest longer.  
     3. Grab stick and explore.  
     4. Investigate the bushes.  

4. **Branch Rendering**
   - In the background, Gemini generates 4 possible next steps (story + scene descriptions).  
   - Nano Banana renders 4 possible scene images (with the character composited).  
   - When player chooses, the pre-rendered text + image are shown instantly (or with a loading screen if clicked too fast).  

5. **Narration**
   - ElevenLabs TTS reads the story text.  
   - Optionally, player choices are also narrated as: *“I decided to [choice].”*  

6. **Progression**
   - Each choice updates character state (HP, XP, inventory).  
   - Later: add combat mechanics (stats vs. enemy stats = win chance).  

---

## System Architecture

### Inputs
- **Required:** Player text choices.  
- **Optional:** Uploaded face image, voice input for decisions (future).  

### Processing
- **Story Engine (Gemini 2.5 Pro):**  
  - Generates next story segment for each of 4 choices.  
  - Outputs text + structured scene description.  

- **Image Engine (Nano Banana API):**  
  - Renders player character (face, weapon, armor) composited into environment.  
  - Generates images for each possible branch.  

- **Narration Engine (ElevenLabs TTS):**  
  - Reads text aloud in natural voice.  

- **Parallel Pre-Rendering:**  
  - Always generate 4 outcomes in advance to minimize waiting.  

### Outputs
- **Scene view:** Character + background image.  
- **Text narration:** Displayed instantly.  
- **Audio narration:** Plays via ElevenLabs.  
- **Choice buttons (4):** Advance story to next branch.  

---

## MVP Scope (Hackathon-friendly)
1. Character creation with presets.  
2. Opening scene (wake in woods).  
3. One decision loop (4 choices → 4 branches).  
4. Image + narration for 1–2 steps deep.  
5. Simple XP counter (e.g. +5 XP when fighting goblin).  

---

## Stretch Goals
- Combat mechanic (player stats vs. enemy stats).  
- Inventory system (weapon upgrades: stick → axe → bow).  
- Dynamic environments (day/night cycle).  
- Voice input for choices.  
- Multiplayer co-op storytelling (two players choose together).  

---

## Demo Script (for judges)
1. Show character creation (pick face, choose stick).  
2. First scene renders: *“I wake up in the woods…”*  
3. Narration plays via ElevenLabs.  
4. Present 4 choices → click “Investigate bushes.”  
5. Instantly show scene with goblin ambush.  
6. Narration continues: *“A goblin jumps out from the bushes!”*  
7. End with XP gained + hint of next quest.  

---

## Why This Works for Hackathon
- **Interactive + visual + narrated = WOW factor.**  
- **Uses multiple APIs (Gemini, Nano Banana, ElevenLabs) = great integration story.**  
- **Nostalgic RPG theme (Gothic, Oblivion) resonates with devs/judges.**  
- **Scalable vision**: from MVP story loop → full RPG platform.  
