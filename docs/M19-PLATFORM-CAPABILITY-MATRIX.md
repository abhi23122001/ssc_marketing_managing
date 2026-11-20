# M19 Platform Capability Matrix

## Platform support

| Platform | Account types | Publishing | Insights | Live verification |
|---|---|---|---|---|
| Instagram | Professional accounts, Pages | Reels, image, carousel (mock-first) | Mock insights | PENDING owner auth |
| Facebook | Pages | Video, image (mock-first) | Mock insights | PENDING owner auth |
| LinkedIn | Authorized profiles/pages | Post (mock-first) | Mock insights | PENDING owner auth |
| YouTube | Channels | Shorts upload (mock-first) | Mock analytics | PENDING owner auth |

## Media format support (SM-06)

- Input: MP4, MOV, AVI (video); JPEG/PNG (image)
- Output (9:16 vertical): 1080x1920, H.264 + AAC, yuv420p
- Subtitles: per-video SRT, HI/EN/Hinglish
- Thumbnails: JPEG, brand-styled

## Feature status

| Feature | Status |
|---|---|
| Media ingestion + checksum | IMPLEMENTED |
| Video rendering (FFmpeg) | VERIFIED (synthetic) |
| Auto-subtitles | CODE only (TTS not yet integrated) |
| Voiceover | CODE only (TTS not yet integrated) |
| Thumbnail generation | CODE draft |
| Platform adapters | Mock-first |
| Live metrics | BLOCKED (auth required) |

## Licensing / copyright guard

- No copyrighted trending songs without authorization.
- Music source + license tracked in `social_audio_assets` (pending table).
- Manual audio selection step defined for extracted/trending tracks.

## Interaction rules

- No scraping through unauthorized automation.
- Rate-limit handling and token expiry handling implemented in queue/error recovery.
