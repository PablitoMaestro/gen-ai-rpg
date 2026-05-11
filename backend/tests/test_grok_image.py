"""Smoke test for the Grok image service.

Run from repo root with:
    cd backend && source venv/bin/activate && python tests/test_grok_image.py

Costs (current xAI pricing): each call to grok-imagine-image-quality is
$0.05. This script makes 3 calls = ~$0.15. Skips gracefully if
XAI_API_KEY is not set.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure backend/ is on sys.path so `services.*` imports resolve when this
# file is run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config.settings import settings  # noqa: E402
from services.grok_image import grok_image_service  # noqa: E402

OUT_DIR = Path(__file__).parent / "test_outputs_grok"
OUT_DIR.mkdir(exist_ok=True)


async def test_text_to_image() -> bytes:
    print("\n[1/3] Text → image (no refs)…")
    img = await grok_image_service.generate_portrait(
        prompt=(
            "Portrait of a weathered medieval ranger with grey-green eyes, "
            "long brown hair, a hooded leather cloak, photoreal, neutral "
            "background, cinematic lighting."
        )
    )
    assert isinstance(img, bytes) and len(img) > 1024, (
        f"expected non-trivial image bytes, got {type(img)} len={len(img) if img else 0}"
    )
    out = OUT_DIR / "01_portrait.png"
    out.write_bytes(img)
    print(f"     ✓ {len(img):,} bytes → {out}")
    return img


async def test_image_ref_to_image(portrait: bytes) -> bytes:
    print("\n[2/3] Single image-ref → image (character build)…")
    img = await grok_image_service.generate_character_image(
        portrait_image=portrait,
        gender="male",
        build_type="ranger",
        portrait_characteristics={
            "age": "adult",
            "eye_color": "grey-green eyes",
            "skin": "weathered skin",
            "hair": "long brown hair",
        },
    )
    assert isinstance(img, bytes) and len(img) > 1024, (
        f"expected non-trivial image bytes, got {type(img)} len={len(img) if img else 0}"
    )
    # Sanity: the fallback path returns the *exact* portrait bytes; if we
    # got those back, generation failed silently.
    assert img != portrait, (
        "generate_character_image returned the original portrait — "
        "likely fell into the error fallback. Check logs."
    )
    out = OUT_DIR / "02_character.png"
    out.write_bytes(img)
    print(f"     ✓ {len(img):,} bytes → {out}")
    return img


async def test_multi_ref_to_image(character: bytes) -> bytes:
    print("\n[3/3] Multi-ref → image (scene with character + anchor + previous)…")
    # Reuse the same image as both anchor and previous to exercise the
    # 3-ref code path while keeping cost flat.
    img = await grok_image_service.generate_scene_image(
        character_image=character,
        scene_description=(
            "SETTING: forest clearing, dawn, low fog; "
            "LIGHT: pale shafts through canopy, cool gray-blue, weak; "
            "KEY OBJECTS: shattered barrels, bloodstained earth, "
            "splintered cart wheel; "
            "ATMOSPHERE: drifting mist, dew on leaves"
        ),
        anchor_image=character,
        # previous_image dedupes against anchor in the service; pass
        # `None` here so we genuinely test the 2-ref path. Multi-ref-3
        # is exercised when previous != anchor in real usage.
        previous_image=None,
        mood="disoriented dread",
    )
    assert isinstance(img, bytes) and len(img) > 1024, (
        f"expected non-trivial image bytes, got {type(img)} len={len(img) if img else 0}"
    )
    assert img != character, (
        "generate_scene_image returned the character image — fell into "
        "the error fallback. Check logs."
    )
    out = OUT_DIR / "03_scene.png"
    out.write_bytes(img)
    print(f"     ✓ {len(img):,} bytes → {out}")
    return img


async def main() -> int:
    if not settings.xai_api_key:
        print(
            "XAI_API_KEY not configured (settings.xai_api_key is empty). "
            "Add it to backend/.env.local. Aborting smoke test.",
            file=sys.stderr,
        )
        return 2
    print(f"Output dir: {OUT_DIR}")
    portrait = await test_text_to_image()
    character = await test_image_ref_to_image(portrait)
    await test_multi_ref_to_image(character)
    print("\nAll Grok image smoke tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
