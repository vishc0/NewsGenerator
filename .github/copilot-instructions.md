# Copilot instructions for NewsGenerator

Purpose
- Help AI coding agents quickly implement and extend the News Generator engine: an automated pipeline that collects recent articles (by topic), curates and summarizes them, publishes daily/regular blog posts, and produces podcast episodes.

Big-picture architecture (high level)
- Ingestors: collect content from RSS, site scrapers, provided article lists, PDF/DOC/TXT files, YouTube URLs and channels. (Expect `ingestors/`)
  - RSS/feeds: `feedparser` or `kurtmckee/feedparser` usage.
  - Article extraction: `newspaper3k` (repo `codelucas/newspaper`) or `readability-lxml`.
  - YouTube transcripts: `jdepoix/youtube-transcript-api` and `yt-dlp` for captions/media.
- Research & Curation: dedupe, date-filter (only last N days), rank/relevance by topic keywords and scores, then produce curated summaries (LLM calls). (Expect `researcher/` and `summarizer/`)
- Formatter: convert curated content to blog-ready Markdown and a podcast-script (template-based). (Expect `formatter/`)
- TTS & Podcast generation: convert scripts to audio (MP3), normalize audio, create episode metadata and show notes. Options: Coqui TTS / Mozilla TTS / `gTTS` (local) or user-provided commercial TTS keys. (Expect `tts/`)
- Publisher
  - Blog: static site generator (zero-cost: GitHub Pages + Jekyll/Hugo/Eleventy) hosting via `gh-pages` or `GitHub Actions` publishing. (Expect `publisher/blog_publisher.py`)
  - Podcast: host audio files on a zero-cost host (recommended: Internet Archive for free storage) and expose an RSS feed (host RSS on GitHub Pages). Anchor is a convenient distribution option but may require manual steps—prefer the RSS approach for full automation.
- Orchestration & Scheduling: GitHub Actions for cron scheduling (public repo = free runner minutes for this usage). Heavy jobs (large audio generation) can run on self-hosted runner or lightweight VPS.

Selected OSS building blocks (candidates to pull-in)
- Content extraction: `codelucas/newspaper` (newspaper3k) — solid for article text extraction.
- Feeds: `kurtmckee/feedparser` — minimal, reliable RSS parsing.
- YouTube transcripts/downloads: `jdepoix/youtube-transcript-api`, `yt-dlp/yt-dlp` for media and captions.
 - YouTube transcripts/downloads: `jdepoix/youtube-transcript-api`, `yt-dlp/yt-dlp` for media and captions.
 - Default LLM: Hugging Face Inference API (`google/flan-t5-small` used in scaffold). The scaffold prefers HF when `HUGGINGFACE_API_KEY` is present and falls back to OpenAI if configured.
- Auto-blog examples: `calumjs/gpt-auto-blog-writer` (good example of generating markdown and pushing to repo), `ikramhasan/AutoBlog-AI-Blog-Generator` (local-LLM examples).
- TTS: `coqui-ai/TTS` or `mozilla/TTS` for on-prem free TTS; `gTTS` is a lightweight fallback for small-scale usage.
- Scheduler / automation: `huginn` or plain `GitHub Actions` workflows depending on desired control.

Important project-specific conventions (how this repo will be organized)
- `topics.yaml`: user-provided topics list (topic name, sources, lookback-hours, cadence). Example entry:
  - name: "China headlines"
    sources: ["https://www.scmp.com/rss/news.xml", "https://example-site.com/rss"]
    lookback_hours: 48
    cadence_per_day: 3
- `sources/` (optional): directory where user can drop `*.txt|*.md|*.pdf|*.docx|youtube_urls.txt` that the ingestors read.
- `ingestors/`: `rss_ingestor.py`, `site_ingestor.py`, `youtube_ingestor.py`, `file_ingestor.py`.
- `pipeline/run.py`: single entry for local testing; honors `--topics` and `--since` flags.
- `publisher/` contains `blog_publisher.py` and `podcast_publisher.py`.
 - `publisher/` contains `blog_publisher.py` and `podcast_publisher.py`. The `podcast_publisher` concatenates per-segment MP3 files (requires `ffmpeg` available for `pydub`).
- `config.yml` or `.env` for local secrets; CI uses `GITHUB_SECRETS`.

Developer workflows and commands
- Local dev (Windows PowerShell):
  - Create venv and install:```
  python -m venv .venv
  .\.venv\Scripts\Activate
  pip install -r requirements.txt
  ```
  - Run pipeline (example):```
  python pipeline\run.py --topics topics.yaml --since 48
  ```
- Run individual components for debugging:
  - Ingest RSS: `python ingestors/rss_ingestor.py --source https://example.com/rss`.
  - Summarize an article: `python researcher/summarizer.py --file samples/article.html`.
- CI scheduling: `/.github/workflows/schedule-pipeline.yml` will use `cron` to run every 6/8 hours; keys are stored in `Secrets`.
 - CI scheduling: `/.github/workflows/schedule-pipeline.yml` runs every 6 hours by default. Publishing steps (uploads or pushes) require repository Secrets (`HUGGINGFACE_API_KEY`, `OPENAI_API_KEY`, `INTERNET_ARCHIVE_*`). Forks won't have access to your secrets; workflows that need secrets will fail in forks (this helps protect your keys).

Security notes for public repos
- Never commit keys. Use `.env` locally and `Secrets` in GitHub Actions.
- The scheduled workflow will run in this repository and can access the repository's secrets. A forked repo cannot access your secrets and therefore cannot publish from your CI.
- For extra safety, the publish/upload job should check for presence of secrets and exit cleanly if missing (the scaffold uses dry-run behavior when IA keys are not present).

Zero-cost architecture recommendations (practical choices)
- Blog hosting: GitHub Pages (Jekyll/Hugo/Eleventy) — store generated Markdown in `content/` and publish.
- Podcast hosting: store MP3s on Internet Archive (free) then publish RSS hosted on GitHub Pages. This enables Apple/Spotify distribution by RSS submission. Anchor is an alternative (convenient but may add friction for automation).
- Compute & scheduler: GitHub Actions as primary orchestrator (public repo). For heavy TTS/transcoding, either run on a small self-hosted runner or stagger jobs to keep within free limits.
- Storage & retention: store metadata + episode links in the repo or a small DB; keep audio on Internet Archive and mark old items for deletion after 1 month via an automated retention job.

Integration & API keys (store in CI/heavily guarded places)
- Add these to `Repository Settings -> Secrets` (names recommended):
  - `OPENAI_API_KEY` (if using OpenAI for summarization)
  - `INTERNET_ARCHIVE_ACCESS_KEY` and `INTERNET_ARCHIVE_SECRET`
  - `S3_*` if using alternate hosting
  - `TTS_API_KEY` for commercial TTS providers (optional)
- Local `.env` for development (do NOT commit).

Patterns and pitfalls found during repo scans (practical tips)
- Prefer RSS & site-native feeds before scraping — feeds are stable and avoid heavy scraping logic.
- `newspaper3k` often fails on JS-heavy sites; keep a failover extractor (readability or fallback to full-html-save then manual extraction).
- YouTube transcripts may be missing for short or auto-generated captions; combine `youtube-transcript-api` and `yt-dlp` fallback.
- Audio file sizes: generate reasonably compressed MP3 (64–96 kbps mono for voice) to reduce storage & bandwidth.

Files the agent should look at first when working on code
- `topics.yaml` — primary input.
- `ingestors/rss_ingestor.py` and `ingestors/site_ingestor.py` — ingestion logic.
- `researcher/summarizer.py` — LLM call wrappers and prompt templates.
- `formatter/blog_template.md` and `formatter/podcast_template.txt` — templates for output.
- `publisher/blog_publisher.py` and `publisher/podcast_publisher.py` — publishing logic.
- `pipeline/run.py` — orchestration entrypoint and CLI.

What to do next (agent checklist when making changes)
- When adding a new ingestor, add unit-level sample inputs into `samples/` with expected outputs.
- Add integration tests that run ingestion -> summarize -> format with small fixtures (no real API calls; mock LLM/TTS).
- When touching publisher code, include a dry-run mode that writes outputs to `outbox/` instead of publishing.
 - When adding a new LLM adapter, include token usage estimates for cost control and a small default model (HF small models are preferred).
 - When adding a publish step (Internet Archive/GH Pages), require an explicit environment variable or secret to enable it; otherwise keep behavior as dry-run.

If anything here is unclear or incomplete, tell me which sections you want expanded (examples: exact `topics.yaml` schema, sample `GitHub Actions` workflow, or a minimal runnable scaffold). I'll iterate and then scaffold the repo with a working minimal pipeline.
