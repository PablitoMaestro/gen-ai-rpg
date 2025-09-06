# Nano Banana JavaScript/TypeScript Implementation Guide

## Installation

### NPM Package
```bash
npm install @google/genai
```

### TypeScript Support
```bash
npm install --save-dev @types/node
```

## Basic Setup

### Initialize the Client
```typescript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
```

## Core Implementation Patterns

### 1. Simple Image Generation from Text

```typescript
import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";

async function generateImage(prompt: string): Promise<Buffer> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image-preview",
    contents: prompt,
  });
  
  // Extract image from response
  for (const part of response.candidates[0].content.parts) {
    if (part.inlineData) {
      const imageData = part.inlineData.data;
      return Buffer.from(imageData, "base64");
    }
  }
  
  throw new Error("No image generated");
}

// Usage
const imageBuffer = await generateImage(
  "Create a photorealistic medieval warrior with glowing blue eyes"
);
fs.writeFileSync("warrior.png", imageBuffer);
```

### 2. Image Editing with Input Image

```typescript
async function editImage(
  imageBuffer: Buffer,
  editPrompt: string
): Promise<Buffer> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const base64Image = imageBuffer.toString("base64");
  
  const prompt = [
    { text: editPrompt },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64Image,
      },
    },
  ];
  
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image-preview",
    contents: prompt,
  });
  
  for (const part of response.candidates[0].content.parts) {
    if (part.inlineData) {
      return Buffer.from(part.inlineData.data, "base64");
    }
  }
  
  throw new Error("No image generated");
}

// Usage
const originalImage = fs.readFileSync("warrior.png");
const editedImage = await editImage(
  originalImage,
  "Place this warrior in a dark forest at night with moonlight"
);
```

### 3. Character Consistency Across Scenes

```typescript
async function generateConsistentCharacterScene(
  characterImage: Buffer,
  sceneDescription: string
): Promise<Buffer> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const base64Character = characterImage.toString("base64");
  
  const prompt = [
    { 
      text: `Using this exact character, create a scene where: ${sceneDescription}. 
             Maintain all character features, clothing, and distinctive marks.` 
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: base64Character,
      },
    },
  ];
  
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image-preview",
    contents: prompt,
  });
  
  for (const part of response.candidates[0].content.parts) {
    if (part.inlineData) {
      return Buffer.from(part.inlineData.data, "base64");
    }
  }
  
  throw new Error("No image generated");
}
```

### 4. Multiple Image Composition

```typescript
async function composeImages(
  image1: Buffer,
  image2: Buffer,
  compositionPrompt: string
): Promise<Buffer> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  
  const prompt = [
    { text: compositionPrompt },
    {
      inlineData: {
        mimeType: "image/png",
        data: image1.toString("base64"),
      },
    },
    {
      inlineData: {
        mimeType: "image/png",
        data: image2.toString("base64"),
      },
    },
  ];
  
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image-preview",
    contents: prompt,
  });
  
  for (const part of response.candidates[0].content.parts) {
    if (part.inlineData) {
      return Buffer.from(part.inlineData.data, "base64");
    }
  }
  
  throw new Error("No image generated");
}

// Usage: Combine character with environment
const character = fs.readFileSync("character.png");
const environment = fs.readFileSync("castle.png");
const composed = await composeImages(
  character,
  environment,
  "Place the character from the first image into the castle environment, " +
  "standing in the courtyard looking heroic"
);
```

### 5. Chat Mode for Iterative Editing (Recommended)

```typescript
class ImageEditingSession {
  private chat: any;
  private ai: GoogleGenAI;
  
  constructor(apiKey: string) {
    this.ai = new GoogleGenAI({ apiKey });
    this.chat = this.ai.chats.create({
      model: "gemini-2.5-flash-image-preview"
    });
  }
  
  async sendInitialImage(image: Buffer, description: string): Promise<Buffer> {
    const base64Image = image.toString("base64");
    
    const response = await this.chat.sendMessage({
      message: [
        { text: description },
        {
          inlineData: {
            mimeType: "image/png",
            data: base64Image,
          },
        },
      ]
    });
    
    return this.extractImage(response);
  }
  
  async editCurrent(editPrompt: string): Promise<Buffer> {
    const response = await this.chat.sendMessage({
      message: editPrompt
    });
    
    return this.extractImage(response);
  }
  
  private extractImage(response: any): Buffer {
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        return Buffer.from(part.inlineData.data, "base64");
      }
    }
    throw new Error("No image in response");
  }
}

// Usage
const session = new ImageEditingSession(process.env.GEMINI_API_KEY!);
const portrait = fs.readFileSync("portrait.png");

// Initial character generation
let result = await session.sendInitialImage(
  portrait,
  "Create a full-body character from this portrait, medieval warrior style"
);

// Iterative edits maintain context
result = await session.editCurrent("Add a glowing sword");
result = await session.editCurrent("Place in a dark dungeon");
result = await session.editCurrent("Add dramatic lighting from torches");
```

### 6. Parallel Story Branch Generation

```typescript
async function generateStoryBranches(
  characterImage: Buffer,
  currentScene: string,
  choices: string[]
): Promise<Buffer[]> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const base64Character = characterImage.toString("base64");
  
  // Generate all branches in parallel
  const promises = choices.map(async (choice) => {
    const prompt = [
      { 
        text: `Current scene: ${currentScene}
               Choice taken: ${choice}
               Generate the resulting scene with this character.` 
      },
      {
        inlineData: {
          mimeType: "image/png",
          data: base64Character,
        },
      },
    ];
    
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-image-preview",
      contents: prompt,
    });
    
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        return Buffer.from(part.inlineData.data, "base64");
      }
    }
    
    throw new Error(`No image generated for choice: ${choice}`);
  });
  
  return Promise.all(promises);
}

// Usage
const branches = await generateStoryBranches(
  characterImage,
  "You stand at the entrance of a dark cave",
  [
    "Enter the cave with sword drawn",
    "Circle around to find another entrance",
    "Call out to see if anyone is inside",
    "Set up camp and wait until morning"
  ]
);
```

### 7. Multiple Image Story Sequence

```typescript
async function generateStorySequence(
  prompt: string,
  imageCount: number = 8
): Promise<Buffer[]> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  
  const fullPrompt = `${prompt} Generate exactly ${imageCount} images to tell this story.`;
  
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash-image-preview",
    contents: fullPrompt,
  });
  
  const images: Buffer[] = [];
  for (const part of response.candidates[0].content.parts) {
    if (part.inlineData) {
      images.push(Buffer.from(part.inlineData.data, "base64"));
    }
  }
  
  return images;
}

// Usage
const storyImages = await generateStorySequence(
  "Tell an epic 8-part story of a knight's journey from " +
  "humble beginnings to defeating a dragon",
  8
);
```

## Error Handling

### Comprehensive Error Handler

```typescript
class NanoBananaError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = "NanoBananaError";
  }
}

async function generateImageWithRetry(
  prompt: string,
  maxRetries: number = 3
): Promise<Buffer> {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-image-preview",
        contents: prompt,
      });
      
      if (!response.candidates || response.candidates.length === 0) {
        throw new NanoBananaError("No candidates in response");
      }
      
      for (const part of response.candidates[0].content.parts) {
        if (part.inlineData) {
          return Buffer.from(part.inlineData.data, "base64");
        }
      }
      
      throw new NanoBananaError("No image in response");
      
    } catch (error: any) {
      console.error(`Attempt ${attempt} failed:`, error.message);
      
      if (attempt === maxRetries) {
        throw new NanoBananaError(
          `Failed after ${maxRetries} attempts`,
          "MAX_RETRIES_EXCEEDED",
          error
        );
      }
      
      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, attempt)));
    }
  }
  
  throw new NanoBananaError("Unexpected error in retry logic");
}
```

## Response Handling Utilities

### Extract All Response Parts

```typescript
interface ResponseParts {
  text: string[];
  images: Buffer[];
}

function parseResponse(response: any): ResponseParts {
  const parts: ResponseParts = {
    text: [],
    images: []
  };
  
  if (!response.candidates || response.candidates.length === 0) {
    return parts;
  }
  
  for (const part of response.candidates[0].content.parts) {
    if (part.text) {
      parts.text.push(part.text);
    } else if (part.inlineData) {
      parts.images.push(Buffer.from(part.inlineData.data, "base64"));
    }
  }
  
  return parts;
}
```

### Save Images with Metadata

```typescript
interface ImageMetadata {
  prompt: string;
  timestamp: Date;
  sessionId?: string;
}

async function saveImageWithMetadata(
  imageBuffer: Buffer,
  metadata: ImageMetadata,
  outputPath: string
): Promise<void> {
  // Save image
  fs.writeFileSync(outputPath, imageBuffer);
  
  // Save metadata
  const metadataPath = outputPath.replace(/\.\w+$/, '.json');
  fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
}
```

## TypeScript Interfaces

### Complete Type Definitions

```typescript
// types/nano-banana.ts

export interface NanoBananaConfig {
  apiKey: string;
  model?: string;
  maxRetries?: number;
  timeout?: number;
}

export interface ImagePrompt {
  text?: string;
  images?: Buffer[];
  mimeType?: "image/png" | "image/jpeg";
}

export interface GenerationOptions {
  responseModalities?: ("Text" | "Image")[];
  temperature?: number;
  topK?: number;
  topP?: number;
}

export interface GeneratedImage {
  data: Buffer;
  mimeType: string;
  metadata?: {
    width?: number;
    height?: number;
    promptUsed?: string;
  };
}

export interface StoryBranch {
  choice: string;
  narration: string;
  image: Buffer;
}

export interface CharacterBuild {
  gender: "male" | "female";
  buildType: "warrior" | "mage" | "rogue" | "ranger";
  portrait: Buffer;
  fullBody?: Buffer;
}
```

## Best Practices

### 1. Prompt Engineering
```typescript
function buildDescriptivePrompt(params: {
  subject: string;
  action: string;
  environment: string;
  style?: string;
  lighting?: string;
  mood?: string;
}): string {
  const { subject, action, environment, style, lighting, mood } = params;
  
  // Narrative prompts work better than keyword lists
  return `Create a ${style || "photorealistic"} image of ${subject} ${action} in ${environment}. 
          ${lighting ? `The lighting is ${lighting}.` : ""} 
          ${mood ? `The overall mood is ${mood}.` : ""}
          Include rich details and atmosphere.`;
}
```

### 2. Image Caching
```typescript
class ImageCache {
  private cache = new Map<string, Buffer>();
  
  generateKey(prompt: string, images?: Buffer[]): string {
    const imageHashes = images?.map(img => 
      crypto.createHash('md5').update(img).digest('hex')
    ).join('-') || '';
    
    return crypto.createHash('md5')
      .update(prompt + imageHashes)
      .digest('hex');
  }
  
  async getOrGenerate(
    prompt: string,
    generator: () => Promise<Buffer>,
    images?: Buffer[]
  ): Promise<Buffer> {
    const key = this.generateKey(prompt, images);
    
    if (this.cache.has(key)) {
      return this.cache.get(key)!;
    }
    
    const result = await generator();
    this.cache.set(key, result);
    return result;
  }
}
```

### 3. Rate Limiting
```typescript
class RateLimiter {
  private requests: Date[] = [];
  private readonly maxRequests: number;
  private readonly windowMs: number;
  
  constructor(maxRequests: number = 100, windowMs: number = 86400000) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
  }
  
  async waitIfNeeded(): Promise<void> {
    const now = new Date();
    const windowStart = new Date(now.getTime() - this.windowMs);
    
    // Remove old requests
    this.requests = this.requests.filter(date => date > windowStart);
    
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = this.windowMs - (now.getTime() - oldestRequest.getTime());
      
      if (waitTime > 0) {
        console.log(`Rate limit reached. Waiting ${waitTime}ms...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      }
    }
    
    this.requests.push(now);
  }
}

// Usage
const rateLimiter = new RateLimiter(100, 24 * 60 * 60 * 1000);

async function generateWithRateLimit(prompt: string): Promise<Buffer> {
  await rateLimiter.waitIfNeeded();
  return generateImage(prompt);
}
```

## Frontend Integration Example

### Next.js API Route
```typescript
// app/api/generate-image/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenAI } from "@google/genai";

export async function POST(request: NextRequest) {
  try {
    const { prompt, imageData } = await request.json();
    
    const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });
    
    const contents = imageData 
      ? [{ text: prompt }, { inlineData: { mimeType: "image/png", data: imageData }}]
      : prompt;
    
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-image-preview",
      contents,
    });
    
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        return NextResponse.json({
          image: part.inlineData.data,
          mimeType: part.inlineData.mimeType
        });
      }
    }
    
    return NextResponse.json({ error: "No image generated" }, { status: 500 });
    
  } catch (error: any) {
    console.error("Image generation error:", error);
    return NextResponse.json(
      { error: error.message || "Generation failed" },
      { status: 500 }
    );
  }
}
```

## Testing

### Unit Test Example
```typescript
import { describe, it, expect, beforeAll } from '@jest/globals';
import { GoogleGenAI } from "@google/genai";

describe('Nano Banana Image Generation', () => {
  let ai: GoogleGenAI;
  
  beforeAll(() => {
    ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });
  });
  
  it('should generate an image from text prompt', async () => {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash-image-preview",
      contents: "A simple red circle on white background",
    });
    
    let hasImage = false;
    for (const part of response.candidates[0].content.parts) {
      if (part.inlineData) {
        hasImage = true;
        expect(part.inlineData.data).toBeDefined();
        expect(part.inlineData.mimeType).toMatch(/image\/(png|jpeg)/);
      }
    }
    
    expect(hasImage).toBe(true);
  }, 30000);
});
```