# NewsGenerator — Configuration & Setup Guide

This document walks a new developer or operator through the exact sequence of configuration tasks required to run, develop, and publish with this repository. Follow the steps in order.

1) Overview and goals
- Purpose: ingest recent news by topic, summarize, format blog posts, synthesize 15 one-minute podcast segments, and optionally publish audio to the Internet Archive and blog to GitHub Pages.
- Default LLM: Hugging Face Inference API (the scaffold prefers HF, falls back to OpenAI if present).

2) Prerequisites (local machine)
- Git and a GitHub account.
- Python 3.10+ (3.11 recommended).
- PowerShell on Windows (instructions below use PowerShell commands).
- `ffmpeg` installed and in PATH for audio operations (pydub uses ffmpeg). On Windows download from https://ffmpeg.org and add to PATH.

3) Create provider accounts and tokens (in sequence)
- Hugging Face (recommended):
  - Sign up: https://huggingface.co/join
  - Create an access token (Settings -> Access Tokens). Copy and store it.
  - Token name suggestion: `newsgen-inference`.

- Internet Archive (optional, for podcast hosting):
  - Sign up: https://archive.org/account/create
  - Note: you will need `access_key` and `secret` for API upload.
- OpenAI (optional fallback): create account and API key if you want OpenAI as a fallback.

4) Add secrets to GitHub repository (public repo safety)
- In GitHub repo -> Settings -> Secrets and variables -> Actions -> New repository secret.
  - `HUGGINGFACE_API_KEY` = your HF token
  - `OPENAI_API_KEY` = optional OpenAI key
  - `INTERNET_ARCHIVE_ACCESS_KEY` and `INTERNET_ARCHIVE_SECRET` = optional IA credentials
- Security notes:
  - Never commit these keys to the repository. Keep them only in GitHub Secrets and your local `.env` (never check in `.env`).
  - CI workflows in forks cannot access your repository secrets.

5) Local dev setup (PowerShell)
```powershell
git clone <your-repo-url>
cd NewsGenerator
python -m venv .venv
.\.venv\Scripts\Activate
pip install --upgrade pip
pip install -r requirements.txt
```

6) Create local `.env` for local testing (optional)
- Copy `.env.example` to `.env` and paste your local keys (for local runs only).
```powershell
cp .env.example .env
# then edit .env with your keys
notepad .env
```

7) Install ffmpeg (Windows quick notes)
- Download static build from https://ffmpeg.org/download.html and extract.
- Add the `bin` folder to your PATH (Windows System Environment -> Edit PATH). Restart PowerShell.

8) Configure `topics.yaml` (how to control usage)
- Example fields per topic:
  - `name` (string)
  - `sources` (array of RSS feed URLs)
  - `lookback_hours` (int) — how far back to fetch articles
  - `cadence_per_day` (int) — intended publishing frequency
  - `article_cap` (int) — max number of articles to fetch per run (important to manage LLM usage)
  - `segments` (int) — number of one-minute segments to synthesize (default 15)
- Recommended to tune `article_cap` and `segments` to keep API usage predictable.

9) Add manual sources directory (optional)
- You can drop files in `sources/`:
  - `urls.txt` — newline-separated article URLs
  - `youtube_urls.txt` — newline-separated YouTube video URLs for transcript ingestion
  - `*.pdf` / `*.docx` — file ingestors (future extension)

10) Run the pipeline (dry-run) locally
```powershell
python pipeline\run.py --topics topics.yaml --since 48
```
- Output locations:
  - Draft blog posts: `outbox/*.md` and `content/*.md` (content is what would be published to GitHub Pages)
  - Podcasts (local concatenated episodes): `outbox/podcasts/<topic>/episode.mp3`

11) Enable scheduled runs on GitHub Actions
- The repo includes `.github/workflows/schedule-pipeline.yml` to run the pipeline every 6 hours by default. It will only publish (upload) if secrets for publishing are present.

12) Enable publishing to Internet Archive (optional)
- To enable automatic upload, add your IA keys to GitHub Secrets and then modify the pipeline to call `publisher.podcast_publisher.upload_to_internet_archive()` with metadata including an `identifier` (unique string per upload) and `metadata` dictionary.
- Metadata must include `identifier`, `title`, `description`, and `creator` keys. Example call (python):
```python
from publisher.podcast_publisher import upload_to_internet_archive
upload_to_internet_archive('outbox/podcasts/World_headlines/episode.mp3',
                          metadata={'identifier':'newsgen-2025-11-24-world','title':'World headlines'},
                          access_key=os.getenv('INTERNET_ARCHIVE_ACCESS_KEY'),
                          secret=os.getenv('INTERNET_ARCHIVE_SECRET'))
```

13) Estimating LLM usage / budgeting (practical)
- Typical speech tokens: ~140–160 words ≈ 1 minute. HF token counts vary by tokenizer — size estimate is conservative.
- Per-segment summarization: assume input tokens ≈ (article tokens) and output tokens ≈ 300 tokens (for short summary). Use `article_cap * segments` to estimate calls.
- Suggested safety: set `article_cap` ≤ 30 and `segments` ≤ 15 initially. Monitor usage on HF dashboard.

14) Troubleshooting tips
- `ffmpeg` not found: ensure ffmpeg is in PATH and restart PowerShell.
- `newspaper3k` extraction fails on JS-heavy sites: add site-specific extractors or rely on RSS summaries instead.
- HF rate limit errors: reduce `article_cap` or add delay between calls.

15) Next configuration tasks you may want to do
- Create a dedicated Hugging Face account and token for this project and add it to GitHub Secrets.
- Decide if you want monthly retention on IA; implement a cleanup job to remove items older than 30 days.
- Add a token-estimator to `researcher/` to output a per-run approximate token usage report.

If anything in this sequence is unclear, tell me which step you want expanded (for example: step-by-step screenshots for creating HF tokens, or sample GitHub Secrets setup instructions), and I'll add those exact instructions.

16) Creating and managing `sources/` (GUI-first + scripts)

Overview
- The pipeline accepts additional inputs via a `sources/` directory at the repository root. Files placed here are read by ingestors (future extensions will add more file types). Current supported helper files:
  - `urls.txt` — newline-separated article URLs (http/https)
  - `youtube_urls.txt` — newline-separated YouTube video URLs
  - `*.pdf`, `*.docx` — (future) file ingest; drop files here for manual ingestion

GUI (Windows Explorer) — create `sources/` and files
1. Open the repository folder in File Explorer: `C:\Environment\NewsGenerator`.
2. Right-click → New → Folder → name it `sources`.
3. Inside `sources`, right-click → New → Text Document. Rename to `urls.txt` (accept extension change).
4. Open `urls.txt` in Notepad and paste newline-separated article URLs, for example:
```
https://www.bbc.com/news/world-12345678
https://www.cnn.com/2025/11/24/example-article
```
5. Save the file.

Upload sources using GitHub web UI (if you prefer browser)
1. Open your repo: https://github.com/vishc0/NewsGenerator
2. Click `Add file` → `Upload files`.
3. Drag and drop your `sources/urls.txt` and any other files.
4. Add a commit message like `Add sample sources` and commit to `main`.

VS Code GUI
1. Open the folder in VS Code (`File → Open Folder` → choose `C:\Environment\NewsGenerator`).
2. In the Explorer, right-click → `New Folder` → `sources`.
3. Right-click the new folder → `New File` → `urls.txt`. Paste URLs, save.
4. Use the Source Control pane to stage and commit changes with a message.

Scripted (PowerShell) — quick helper
- A helper script `scripts/create_sources.ps1` is included in this repo. Run it to scaffold `sources/` and sample files.

Validate sources and run
- After adding files, run the pipeline locally to validate ingestion:
```powershell
python pipeline\run.py --topics topics.yaml --since 48
```
- Inspect `outbox/` for generated drafts and `outbox/podcasts/` for synthesized episodes.

Notes and best practices
- Keep `urls.txt` small (a few dozen URLs) to limit LLM calls — prefer RSS feeds in `topics.yaml` when available.
- Use one YouTube URL per line in `youtube_urls.txt`. The scaffold will use transcript tools if a `youtube_ingestor` is later implemented.
- If you add large binary files (PDFs), avoid committing them to the main branch for large size; instead upload to an external storage and reference them in `urls.txt` or process locally.

