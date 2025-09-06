#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai

from config.settings import settings


async def test_portrait_generation() -> None:
    """Test portrait generation with debug output."""

    # Configure API
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

    prompt = ("A photorealistic portrait of a medieval knight from the neck up, "
              "wearing armor, neutral background. Medieval fantasy RPG character art style.")

    print(f"Testing with prompt: {prompt}")
    print("-" * 50)

    try:
        # Generate content
        response = await model.generate_content_async(prompt)

        print(f"Response type: {type(response)}")
        print(f"Response has candidates: {hasattr(response, 'candidates')}")

        if hasattr(response, 'candidates') and response.candidates:
            for i, candidate in enumerate(response.candidates):
                print(f"\nCandidate {i}:")
                print(f"  Has content: {hasattr(candidate, 'content')}")

                if hasattr(candidate, 'content'):
                    content = candidate.content
                    print(f"  Content has parts: {hasattr(content, 'parts')}")

                    if hasattr(content, 'parts'):
                        for j, part in enumerate(content.parts):
                            print(f"\n  Part {j}:")
                            print(f"    Type: {type(part)}")
                            print(f"    Has text: {hasattr(part, 'text')}")
                            print(f"    Has inline_data: {hasattr(part, 'inline_data')}")

                            if hasattr(part, 'text') and part.text:
                                print(f"    Text: {part.text[:100]}")

                            if hasattr(part, 'inline_data') and part.inline_data:
                                print(
                                    f"    Inline data type: {type(part.inline_data)}"
                                )
                                print(
                                    f"    Has mime_type: "
                                    f"{hasattr(part.inline_data, 'mime_type')}"
                                )
                                print(f"    Has data: {hasattr(part.inline_data, 'data')}")

                                if hasattr(part.inline_data, 'mime_type'):
                                    print(f"    Mime type: {part.inline_data.mime_type}")

                                if hasattr(part.inline_data, 'data'):
                                    data = part.inline_data.data
                                    print(f"    Data type: {type(data)}")
                                    print(f"    Data length: {len(data) if data else 0}")

                                    # Try to save the raw data
                                    if data:
                                        with open('test_raw_output.bin', 'wb') as f:
                                            # Check if it's already bytes or needs encoding
                                            if isinstance(data, bytes):
                                                f.write(data)
                                                print(f"    Saved as bytes: {len(data)} bytes")
                                            elif isinstance(data, str):
                                                # Assume it's base64 encoded
                                                import base64
                                                decoded = base64.b64decode(data)
                                                f.write(decoded)
                                                print(
                                                    f"    Saved as base64 decoded: "
                                                    f"{len(decoded)} bytes"
                                                )

        # Also try the text attribute directly
        if hasattr(response, 'text'):
            print(f"\nDirect text attribute: {response.text[:200] if response.text else 'None'}")

        # Try parts directly
        if hasattr(response, 'parts'):
            print(f"\nDirect parts attribute: {response.parts}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_portrait_generation())
