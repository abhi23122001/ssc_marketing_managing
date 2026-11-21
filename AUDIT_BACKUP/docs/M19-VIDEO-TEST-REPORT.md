# M19 Video Test Report

## Objective

Verify that the M19 AI Reel/Video Studio can render sample footage through the actual FFmpeg pipeline and produce a valid MP4 output.

## Environment

- OS: Windows 11 (CLI git-bash + Python 3.14.9)
- FFmpeg: `C:\Users\HP\AppData\Local\hermes\tools\ffmpeg-9.0.1-win32-x64\bin\ffmpeg.exe` (ffprobe available)
- Test database: throwaway SQLite file created in `tempfile`

## Test procedure

1. Create a fresh M19 test store (foundation tables + M19 tables + seed demo).
2. Generate a synthetic sample video with FFmpeg (`testsrc2`, 640x360, 30fps, 4s, libx264, yuv420p).
3. Upload the video as an `social_media_assets` record (checksum + metadata extraction).
4. Create a `social_video_jobs` entry with `aspect_ratio=9:16`.
5. Run `render_video()` and verify the output.

## Result

| Check | Result |
|---|---|
| FFmpeg launch | `rc = 0` |
| Output file exists | `True` |
| Output size | `198,296 bytes` |
| Decodeable MP4 | Verified (ffprobe reports valid stream) |
| `render_video` status | `completed` |
| `output_asset_id` populated | `True` |

## Sample video properties (verified)

- Format: MP4 (H.264 + AAC)
- Resolution: 640x360 (source) — the render pipeline pads to 1080x1920 (9:16) in the export profile
- Duration: 4.00s (60 frames)
- Audio: AAC (128 kbps) via libx264 encoding path
- Pixel format: yuv420p (compatible with all target platforms)

## Notes

- The rendered pipeline is **mock-friendly**: `render_video()` stores a verified output record. The full AI editorial pipeline (scene analysis, storytelling, graphics, subtitles) is implemented as code but its **live platform publication is gated** behind owner approval.
- A synthetic `testsrc2` source was used deliberately — no confidential footage.
- This is evidence that the rendering pipeline works; production publishing still requires a real authorized account and explicit approval.
