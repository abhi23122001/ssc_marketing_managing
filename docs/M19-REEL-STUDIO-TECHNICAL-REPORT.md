# M19 Reel Studio Technical Report

## Architecture

- **Input**: raw video/images (SM-06 media ingestion), logo/brand assets (`social_brand_assets`).
- **Analysis**: scene detection, blank/low-quality detection, clip ranking (implementation draft — pending local computer-vision library).
- **Storytelling**: hook/main/closing/CTA generator (AI text prompt model).
- **Editing**: FFmpeg-based (`m19_media._render_ffmpeg`): trim, cut, sequence, transitions, speed, zoom, crop, aspect-ratio, stabilization, brightness/contrast, audio normalization, text overlays, logo placement, end-screen, CTA.
- **Subtitles**: auto-generated SRT (HI/EN/Hinglish template) + manual correction supported.
- **Render**: final MP4 + thumbnail + subtitle + metadata + production log.

## Export profiles (configurable, not hardcoded)

- Vertical short-form: 9:16, 1080x1920, H.264, yuv420p, AAC 128k, faststart
- Landscape: 16:9, 1920x1080, H.264, yuv420p
- Platform size/duration limits read from a profile table (to be added)

## Test result

- Synthetic `testsrc2` 640x360 → 9:16 padded output: `rc = 0`, output `198,296 bytes`, valid MP4.
- The AI editorial (storytelling, script, subtitle) is implemented; live TTS is a pending dependency.

## Readiness gate for production

- Verified rendering. Production publishing still requires: real account auth + owner approval + exact-version gate.
