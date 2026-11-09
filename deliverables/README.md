# Round 2 deliverables

Send by email to EB.VN@netcompany.com, subject "Round 2 – NEW AURA", **before 22:00 (GMT+7) on 9 Nov 2026**. Aim to send by 18:00.

| File (final name) | Requirement | Owner | Status |
|---|---|---|---|
| `MVP.mp4` | Max 7 minutes, English narration or subtitles, explain changes since Round 1 | Nhật Anh | Done (5:44): screen recording + burned-in English subtitles + English voice-over (neural voice `en-US-EmmaNeural`, via edge-tts). Rebuild: `python video-kit/scripts/build-video.py --edge en-US-EmmaNeural --out deliverables/MVP.mp4` (needs the raw recording in `mvp/out/raw/` and `pip install edge-tts`; without `--edge` it uses the offline Windows voice) |
| `User Journey.pdf` | Max 2 pages, at least one complete end-to-end journey | | Rebuilt 8 Nov from the final UI (2 pages); rebuild if the UI changes |
| `System Context Diagram.pdf` | Max 2 pages, all external entities and interactions labelled, matches the real MVP | | Rebuilt 8 Nov as a context diagram: system circle, external rectangles, labelled data flows (2 pages) |
| `AI Journal.pdf` | Organiser template, saved as PDF (max 5 tasks, 150-word strategy) | | Draft in docs/round2/AI-Journal-DRAFT.docx; team must fill the real times (yellow), then run `export-ai-journal.ps1` |

The AI Journal template is `docs/reference/AI Journal template.docx`; the Round 2 requirements are in `docs/reference/IT Consultant Challenge 2026 - Round 2 (brief).pdf`.

Before sending: files open correctly, short clear names, no passwords or API keys in any file.

The two PDFs are generated from `deliverables/src/` (HTML + screenshots of the running app). Rebuild with `cd deliverables/src && NODE_PATH=$(npm root -g) node build_pdfs.js` (needs Playwright with Chromium).

## Before sending

```bash
python deliverables/check-submission.py
```
Checks the four file names, page limits, video length (7:00 max), leftover placeholders in the AI Journal draft and key-like strings. The email text and the large-video fallback (a share link) are in `docs/round2/EMAIL.md`.
