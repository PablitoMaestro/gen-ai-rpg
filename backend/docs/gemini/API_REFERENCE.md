# Nano Banana API Reference

## Authentication

### API Key Setup

#### Obtaining an API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Navigate to API Keys section
4. Create a new API key for your project
5. **Important**: For hackathon, use free tier key (100 requests/day limit)

#### Environment Variables
```bash
# .env file
GEMINI_API_KEY=your_api_key_here

# Optional: Separate key for Nano Banana if different
NANO_BANANA_API_KEY=your_nano_banana_key_here
```

#### Authentication Methods

##### JavaScript/TypeScript
```javascript
import { GoogleGenAI } from "@google/genai";

// From environment variable
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

// Direct (not recommended for production)
const ai = new GoogleGenAI({ apiKey: "your_api_key_here" });
```

##### Python
```python
from google import genai

# From environment variable
import os
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Direct (not recommended for production)
client = genai.Client(api_key="your_api_key_here")
```

## API Endpoints

### Base URLs

| Environment | Base URL |
|------------|----------|
| Gemini API | `https://generativelanguage.googleapis.com/v1beta/` |
| Vertex AI | `https://[REGION]-aiplatform.googleapis.com/v1/` |
| AI Studio | `https://aistudio.google.com/` |

### Model Endpoints

#### Generate Content
- **Endpoint**: `/models/{model}/generateContent`
- **Model**: `gemini-2.5-flash-image-preview`
- **Method**: POST
- **Content-Type**: `application/json`

## Rate Limits & Quotas

### Free Tier (Hackathon Special)
| Limit Type | Value | Duration | Notes |
|------------|-------|----------|-------|
| Requests | 100 | Per day | Per project |
| Concurrent Requests | 10 | - | Simultaneous API calls |
| Input Token Limit | 480 | Per request | Text tokens |
| Output Images | 1-8 | Per request | Configurable |
| Max Input Images | 3 | Per request | For composition/editing |
| Request Timeout | 60s | Per request | May vary with complexity |

### Paid Tier
| Limit Type | Value | Duration | Notes |
|------------|-------|----------|-------|
| Requests | Unlimited* | - | Subject to billing |
| Rate Limit | 360 | Per minute | Can be increased |
| Concurrent Requests | 100 | - | Default, can be increased |
| Input Token Limit | 480 | Per request | Text tokens |
| Output Token Price | $30.00 | Per 1M tokens | ~$0.039 per image |

*Subject to account quotas and billing limits

### Rate Limit Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1693526400
```

## Request Format

### Basic Structure

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "contents": [
    {
      "parts": [
        {
          "text": "Your prompt here"
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.4,
    "topK": 32,
    "topP": 1,
    "maxOutputTokens": 4096
  },
  "safetySettings": [
    {
      "category": "HARM_CATEGORY_HARASSMENT",
      "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
  ]
}
```

### With Image Input

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "contents": [
    {
      "parts": [
        {
          "text": "Edit this image"
        },
        {
          "inline_data": {
            "mime_type": "image/png",
            "data": "base64_encoded_image_data"
          }
        }
      ]
    }
  ]
}
```

### Multiple Images

```json
{
  "model": "gemini-2.5-flash-image-preview",
  "contents": [
    {
      "parts": [
        {
          "text": "Combine these images"
        },
        {
          "inline_data": {
            "mime_type": "image/png",
            "data": "base64_image_1"
          }
        },
        {
          "inline_data": {
            "mime_type": "image/png",
            "data": "base64_image_2"
          }
        }
      ]
    }
  ]
}
```

## Response Format

### Successful Response

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Generated description or response text"
          },
          {
            "inline_data": {
              "mime_type": "image/png",
              "data": "base64_encoded_generated_image"
            }
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "probability": "NEGLIGIBLE"
        }
      ]
    }
  ],
  "promptFeedback": {
    "safetyRatings": [
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "probability": "NEGLIGIBLE"
      }
    ]
  }
}
```

### Error Response

```json
{
  "error": {
    "code": 429,
    "message": "Resource exhausted",
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "RATE_LIMIT_EXCEEDED",
        "domain": "generativelanguage.googleapis.com",
        "metadata": {
          "service": "generativelanguage.googleapis.com",
          "quota_limit": "100",
          "quota_metric": "requests_per_day"
        }
      }
    ]
  }
}
```

## Error Codes

### HTTP Status Codes

| Code | Status | Description | Action |
|------|--------|-------------|--------|
| 200 | OK | Success | Process response |
| 400 | Bad Request | Invalid request format | Check request syntax |
| 401 | Unauthorized | Invalid API key | Verify API key |
| 403 | Forbidden | Access denied | Check permissions |
| 404 | Not Found | Model not found | Verify model name |
| 429 | Too Many Requests | Rate limit exceeded | Implement backoff |
| 500 | Internal Server Error | Server error | Retry with backoff |
| 503 | Service Unavailable | Temporary outage | Retry later |

### API Error Codes

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `INVALID_ARGUMENT` | Invalid request parameters | Check request format |
| `DEADLINE_EXCEEDED` | Request timeout | Simplify prompt or retry |
| `NOT_FOUND` | Resource not found | Verify model/endpoint |
| `ALREADY_EXISTS` | Resource already exists | Use different identifier |
| `PERMISSION_DENIED` | Insufficient permissions | Check API key permissions |
| `RESOURCE_EXHAUSTED` | Quota exceeded | Wait for quota reset |
| `FAILED_PRECONDITION` | Precondition not met | Check requirements |
| `ABORTED` | Operation aborted | Retry operation |
| `OUT_OF_RANGE` | Value out of range | Adjust parameters |
| `UNIMPLEMENTED` | Feature not implemented | Use alternative approach |
| `INTERNAL` | Internal error | Contact support if persistent |
| `UNAVAILABLE` | Service unavailable | Retry with backoff |
| `DATA_LOSS` | Data corruption | Retry request |
| `UNAUTHENTICATED` | Not authenticated | Provide valid API key |

## Configuration Parameters

### Generation Config

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `temperature` | float | 0.4 | 0.0-2.0 | Controls randomness |
| `topK` | integer | 32 | 1-40 | Top K sampling |
| `topP` | float | 1.0 | 0.0-1.0 | Nucleus sampling |
| `maxOutputTokens` | integer | 4096 | 1-8192 | Max response length |
| `stopSequences` | array | [] | - | Stop generation triggers |
| `candidateCount` | integer | 1 | 1-8 | Number of responses |

### Safety Settings

#### Categories
- `HARM_CATEGORY_HARASSMENT`
- `HARM_CATEGORY_HATE_SPEECH`
- `HARM_CATEGORY_SEXUALLY_EXPLICIT`
- `HARM_CATEGORY_DANGEROUS_CONTENT`

#### Thresholds
- `BLOCK_NONE` - No blocking
- `BLOCK_ONLY_HIGH` - Block high probability
- `BLOCK_MEDIUM_AND_ABOVE` - Block medium and high
- `BLOCK_LOW_AND_ABOVE` - Block all but negligible

## Pricing

### Free Tier (Hackathon)
- **Cost**: $0
- **Duration**: September 6-7, 2025 (48 hours)
- **Limit**: 100 requests per day
- **Overage**: Not allowed (hard limit)

### Paid Tier

#### Image Generation
- **Price**: $30.00 per 1 million output tokens
- **Tokens per Image**: 1,290
- **Cost per Image**: ~$0.039
- **Billing**: Per request, immediate

#### Text Generation
- **Input**: $0.075 per 1 million tokens
- **Output**: $0.30 per 1 million tokens
- **Cached Input**: $0.01875 per 1 million tokens

### Cost Calculation Examples

```javascript
// Single image generation
const tokensPerImage = 1290;
const pricePerMillionTokens = 30.00;
const costPerImage = (tokensPerImage / 1000000) * pricePerMillionTokens;
// Result: $0.0387 per image

// Story with 8 images
const imagesPerStory = 8;
const costPerStory = costPerImage * imagesPerStory;
// Result: $0.3096 per 8-image story

// Daily hackathon allowance (free tier)
const freeRequests = 100;
const dailyValue = freeRequests * costPerImage;
// Result: $3.87 worth of generation per day
```

## Headers

### Required Headers

```http
POST /v1beta/models/gemini-2.5-flash-image-preview:generateContent
Host: generativelanguage.googleapis.com
Content-Type: application/json
X-Goog-Api-Key: YOUR_API_KEY
```

### Optional Headers

```http
X-Goog-User-Project: project-id
X-Request-ID: unique-request-id
Accept: application/json
Accept-Encoding: gzip, deflate
User-Agent: your-app/1.0.0
```

## SDK Configuration

### JavaScript/TypeScript

```javascript
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  // Optional configurations
  baseURL: "https://generativelanguage.googleapis.com",
  timeout: 60000, // 60 seconds
  maxRetries: 3,
  headers: {
    "X-Custom-Header": "value"
  }
});

// Model-specific config
const modelConfig = {
  model: "gemini-2.5-flash-image-preview",
  generationConfig: {
    temperature: 0.4,
    topK: 32,
    topP: 1,
    maxOutputTokens: 4096
  },
  safetySettings: [
    {
      category: "HARM_CATEGORY_HARASSMENT",
      threshold: "BLOCK_MEDIUM_AND_ABOVE"
    }
  ]
};
```

### Python

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    # Optional configurations
    client_options={
        "api_endpoint": "generativelanguage.googleapis.com"
    },
    transport="rest"  # or "grpc"
)

# Generation config
config = types.GenerateContentConfig(
    temperature=0.4,
    top_k=32,
    top_p=1,
    max_output_tokens=4096,
    response_modalities=['Text', 'Image'],
    stop_sequences=[],
    candidate_count=1
)

# Safety settings
safety_settings = [
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_MEDIUM_AND_ABOVE"
    )
]
```

## Monitoring & Logging

### Request Logging

```python
import logging
import json
from datetime import datetime

class APILogger:
    def __init__(self, log_file="api_requests.log"):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_request(self, endpoint, prompt, images_count=0):
        self.logger.info(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "prompt_length": len(prompt),
            "images_count": images_count,
            "type": "request"
        }))
    
    def log_response(self, status_code, has_image, latency_ms):
        self.logger.info(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
            "has_image": has_image,
            "latency_ms": latency_ms,
            "type": "response"
        }))
    
    def log_error(self, error_code, error_message):
        self.logger.error(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "error_code": error_code,
            "error_message": error_message,
            "type": "error"
        }))
```

### Usage Tracking

```javascript
class UsageTracker {
  constructor() {
    this.dailyRequests = 0;
    this.resetTime = this.getNextResetTime();
    this.requests = [];
  }
  
  getNextResetTime() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    tomorrow.setHours(0, 0, 0, 0);
    return tomorrow;
  }
  
  trackRequest(promptLength, imageCount) {
    const now = new Date();
    
    // Reset if new day
    if (now >= this.resetTime) {
      this.dailyRequests = 0;
      this.resetTime = this.getNextResetTime();
      this.requests = [];
    }
    
    this.dailyRequests++;
    this.requests.push({
      timestamp: now.toISOString(),
      promptLength,
      imageCount,
      remaining: 100 - this.dailyRequests
    });
    
    return {
      used: this.dailyRequests,
      remaining: Math.max(0, 100 - this.dailyRequests),
      resetIn: this.resetTime - now
    };
  }
  
  canMakeRequest() {
    return this.dailyRequests < 100;
  }
}
```

## Best Practices

### API Key Security
1. Never commit API keys to version control
2. Use environment variables
3. Rotate keys regularly
4. Use separate keys for development/production
5. Monitor usage for anomalies

### Rate Limit Management
1. Implement exponential backoff
2. Track daily usage
3. Queue requests during peak times
4. Cache responses when possible
5. Use batch processing for multiple images

### Error Handling
1. Always wrap API calls in try-catch
2. Log all errors with context
3. Implement retry logic for transient errors
4. Provide fallback options
5. Monitor error rates

### Performance Optimization
1. Use chat mode for iterative edits
2. Generate branches in parallel
3. Compress images before sending
4. Cache frequently used images
5. Minimize prompt length when possible

## Migration Notes

### From Gemini 2.0 to 2.5
```javascript
// Old (deprecated September 26, 2025)
const model = "gemini-2.0-flash-preview-image-generation";

// New
const model = "gemini-2.5-flash-image-preview";
```

### Key Changes
- Improved character consistency
- Better text rendering in images
- Enhanced safety filters
- Support for up to 8 images per request
- More flexible content moderation

## Support & Resources

### Official Resources
- [API Documentation](https://ai.google.dev/gemini-api/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [Status Page](https://status.cloud.google.com/)
- [Issue Tracker](https://issuetracker.google.com/issues)

### Community
- [Discord Server](https://discord.gg/google-ai)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/google-gemini)
- [GitHub Discussions](https://github.com/google/generative-ai-docs/discussions)

### Hackathon Support
- [Kaggle Competition Forum](https://www.kaggle.com/competitions/banana/discussion)
- [Nano Banana Kit](https://github.com/google-gemini/nano-banana-hackathon-kit)
- Hackathon Period: September 6-7, 2025