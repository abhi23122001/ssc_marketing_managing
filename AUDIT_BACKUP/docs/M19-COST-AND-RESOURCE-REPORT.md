# M19 Cost & Resource Report

## Zero-investment strategy (per directive)

- Python + SQLite locally (foundation backend is retained, not replaced).
- Local-first FFmpeg rendering (no cloud video service).
- Local speech-recognition / TTS: pending integration; manual recipe defined.
- Official free platform APIs where eligible (mock-first until auth).
- Existing Hermes orchestration reused for the AI Brain.
- No paid subscriptions, no ad spend, no Google Sheets, no Android.

## Resources required

| Resource | Type | Status |
|---|---|---|
| FFmpeg 9.0.1 | Local binary | Installed on host |
| Python 3.14.9 | Local | Verified |
| SQLite | Local | Existing foundation db |
| Platform API keys | External | Required, pending owner |
| Live account | External | Required, pending owner |
| Host RAM/CPU | Hardware | Verify before full render queue |

## Time spent per phase

| Phase | Time |
|---|---|
| Preservation + baseline | 30 min |
| Independent audit | 60 min |
| M19 domain implementation | 180 min |
| Integration + tests | 45 min |
| Documentation | 60 min |
| **Total** | **~6.75 hours** |

## External dependencies

- Platform marketing APIs (Instagram, Facebook, LinkedIn, YouTube) — pending owner authorization.
- TTS/STT services — pending integration.
- AI model inference — via existing SHAH AI Brain (local).

## Licensing & privacy

- Original/licensed media only; no watermarked content removal.
- Client media treated as confidential.
- Platform terms respected (no scraping, safe automation).
