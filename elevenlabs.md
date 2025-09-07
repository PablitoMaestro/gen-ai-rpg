# pip install elevenlabs
import base64
from pathlib import Path
from elevenlabs import ElevenLabs

API_KEY = "YOUR_API_KEY"
client = ElevenLabs(api_key=API_KEY)

# 1) Projektowanie głosu (previews)
resp = client.text_to_voice.design(
    voice_description=(
        "Warm, confident Polish male narrator with a calm tempo, "
        "clear articulation, slight gravel in mids, natural breaths, "
        "suitable for tech explainers and product demos."
    ),
    model_id="eleven_ttv_v3",          # v3 model
    auto_generate_text=True,           # albo podaj własny 'text' (100–1000 znaków)
    output_format="mp3_44100_192",     # wymaga Creator+
    guidance_scale=5.0,                # 0–100
    loudness=0.2,                      # -1..1 (0 ≈ -24 LUFS)
    seed=12345,                        # replikowalność
    # reference_audio_base64=...,      # (opcjonalnie) v3 wspiera ref audio
    # prompt_strength=0.6,             # 0..1 (z ref audio)
    stream_previews=False              # False => od razu dostaniesz audio_base_64
)

# 2) Zapis wszystkich podglądów do plików (MP3/OPUS/PCM zależnie od output_format)
out_dir = Path("voice_previews")
out_dir.mkdir(exist_ok=True)
for i, p in enumerate(resp.previews, start=1):
    audio_bytes = base64.b64decode(p.audio_base_64)
    ext = ".mp3" if "mp3" in (p.media_type or "audio/mpeg") else ".bin"
    fpath = out_dir / f"preview_{i}_{p.generated_voice_id}{ext}"
    fpath.write_bytes(audio_bytes)
    print(f"Saved: {fpath}  | lang={p.language}  | duration={p.duration_secs:.2f}s")

# 3) Wybór najlepszego podglądu
best = resp.previews[0]
print("Chosen generated_voice_id:", best.generated_voice_id)

# (Dalszy krok wg dokumentacji:)
# Użyj best.generated_voice_id z endpointem /v1/text-to-voice,
# aby utworzyć właściwy głos (patrz sekcja 'Text to Voice' w API).