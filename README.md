# NewsGenerator - Minimal Scaffold

Purpose: small, extendable pipeline that ingests news sources, summarizes content, formats blog posts, and produces basic podcast audio.

## Quick start (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
python pipeline\run.py --topics topics.yaml --since 48
```

## Documentation

- **[CONFIGURE.md](CONFIGURE.md)** - Detailed setup and configuration guide
- **[docs/IPHONE_ACCESS.md](docs/IPHONE_ACCESS.md)** - 📱 How to access blog posts and podcasts on iPhone
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines

## Accessing Generated Content

### Blog Posts
- Generated markdown files are saved to `content/` and `outbox/`
- View on GitHub or enable GitHub Pages for web access

### Podcasts
- Audio episodes are saved to `outbox/podcasts/<topic>/episode.mp3`
- RSS feed is generated at `outbox/podcast_feed.xml`
- **iPhone users**: See [docs/IPHONE_ACCESS.md](docs/IPHONE_ACCESS.md) for podcast app setup

## Design choices:
- Pure Python for readability and broad package support.
- Static-site blog output (GitHub Pages) and Internet Archive for podcast hosting to stay zero-cost.
- Pluggable LLM adapters: `OPENAI_API_KEY` or `HUGGINGFACE_API_KEY` (prefer a free-tier account with strict quota limits).

## LLM guidance:
- For zero-cost predictable usage, create a free Hugging Face account and use the Inference API with a small model; set strict rate limits in usage and test with a small token budget.
- Alternative: run a local LLM (ollama/llama.cpp) on your own machine or on a low-cost VPS if you need more control.

## Hugging Face & Accounts (quick links)
- Create Hugging Face account: https://huggingface.co/join
- Create Access Token: https://huggingface.co/settings/tokens

## Internet Archive (podcast hosting)
- Create account: https://archive.org/account/create
- Upload docs: https://archive.org/services/docs/api/

## Security & public repo notes
- Keep secret keys out of the repo. Use GitHub Actions Secrets (`Settings -> Secrets and variables -> Actions`).
- The scheduled workflow will run in *this* repository and can access the repository's secrets. If someone forks the repo, their fork will not have access to your secrets.
- Publishing steps (upload to Internet Archive or pushing to GitHub Pages) will only run successfully when correct secrets are present in the repository. Without them the pipeline will be effectively a dry-run.

## Podcasts & Segmenting
- The pipeline generates N small segments (default 15) per topic and synthesizes each segment to an MP3. Segments are concatenated into `outbox/podcasts/<topic>/episode.mp3`.
- One minute of speech ≈ 140–160 words. The pipeline truncates segments to ~180 words to keep segment durations near one minute when using gTTS.


## Next steps:
- Provide LLM API key and (optionally) Internet Archive credentials to enable publishing.
- Tell me which summarization preference (OpenAI vs Hugging Face vs local) you prefer and I'll wire the adapter.
