# NewsGenerator - Automated News Curation & Podcast Pipeline

An intelligent, zero-cost automated pipeline that ingests news from multiple sources, summarizes content using AI, generates blog posts, and produces podcast episodes—all running on GitHub Actions.

## ✨ Features

**Content Ingestion:**
- 📰 RSS feed parsing with configurable date filtering
- 🌤️ Weather data integration (Open-Meteo API, no key required)
- 🎥 YouTube video transcript extraction
- 📋 Manual URL and file-based content sources
- 🔄 Smart deduplication and filtering

**AI-Powered Processing:**
- 🤖 Multi-provider LLM support (Hugging Face, OpenAI, with fallback)
- 📝 Intelligent summarization optimized for readability
- 💰 Token usage tracking with cost estimates
- ⚡ Rate limiting and quota management

**Publishing & Distribution:**
- 📱 Jekyll-compatible blog posts with front matter
- 🎙️ TTS audio generation for podcast segments
- 🎵 Automated podcast episode creation (MP3)
- 📡 iTunes-compatible RSS feed generation
- ☁️ Internet Archive hosting (free, unlimited storage)
- 🌐 GitHub Pages integration (free blog hosting)

**Automation:**
- ⏰ Scheduled runs via GitHub Actions (every 6 hours)
- 🔧 On-demand execution via PR comments
- 📊 Comprehensive logging and error handling
- 🔐 Secure credential management

## 🚀 Quick Start

### Prerequisites
- GitHub account (for hosting and automation)
- Hugging Face account (free - for AI summarization)

### Setup in 3 Steps

1. **Fork this repository**

2. **Add API Keys**
   - Go to Settings → Secrets and variables → Actions
   - Add `HUGGINGFACE_API_KEY` (get from https://huggingface.co/settings/tokens)
   - Optional: Add Internet Archive credentials for podcast hosting

3. **Customize Topics**
   - Edit `topics.yaml` to configure your news topics
   - Commit the changes

That's it! The pipeline runs automatically every 6 hours.

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment and operations guide
- **[CONFIGURE.md](CONFIGURE.md)** - Detailed configuration options
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development and contribution guide

## 🎯 Use Cases

- **Personal News Digest**: Automated daily briefings on topics you care about
- **Podcast Creation**: Turn news articles into audio episodes
- **Topic Monitoring**: Track specific industries, technologies, or locations
- **Research Assistant**: Aggregate and summarize content from multiple sources
- **Content Curation**: Maintain an automatically updated blog

## 📊 Example Output

**Blog Posts:**
- Jekyll-formatted markdown with front matter
- Date-based filenames for chronological ordering
- Automatic deployment to GitHub Pages
- Example: `content/2025-11-24-World_News.md`

**Podcast Episodes:**
- Concatenated MP3 files with multiple segments
- iTunes-compatible RSS feed
- Hosted on Internet Archive (free)
- Example: `outbox/podcasts/World_News/episode.mp3`

**Reports:**
- Token usage and cost estimates
- Error logs and debugging information
- Example: `outbox/token_usage_report.txt`

## 🎛️ Configuration

### Configure Topics (`topics.yaml`)

```yaml
- name: "AI Tech News"
  sources:
    - "https://venturebeat.com/category/ai/feed/"
    - "https://www.technologyreview.com/feed/tag/ai/"
  lookback_hours: 48
  article_cap: 25
  segments: 10

- name: "Weather"
  type: "weather"
  provider: "open-meteo"
  locations:
    - name: "San Francisco"
      lat: 37.7749
      lon: -122.4194
  segments: 3
```

See [CONFIGURE.md](CONFIGURE.md) for all options.

## 🔧 Local Development

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

# Create .env with your API keys
cp .env.example .env
# Edit .env and add keys

# Run pipeline
python pipeline\run.py --topics topics.yaml --since 48
```

## 🏗️ Architecture

```
NewsGenerator/
├── ingestors/          # Content ingestion (RSS, Weather, YouTube, Files)
├── researcher/         # AI summarization and token tracking
├── formatter/          # Blog post formatting (Markdown, Jekyll, Hugo)
├── publisher/          # Publishing (Blog, Podcast, Internet Archive)
├── tts/                # Text-to-speech generation
├── pipeline/           # Main orchestration
└── .github/workflows/  # GitHub Actions automation
```

## 💰 Cost Breakdown

**Free Tier (Recommended):**
- Hugging Face Inference API: FREE
- Internet Archive: FREE (unlimited storage)
- GitHub Actions: FREE (2,000 min/month for public repos)
- GitHub Pages: FREE

**Total Monthly Cost: $0**

**Optional Paid Services:**
- OpenAI GPT-3.5 (fallback): ~$8-10/month for typical usage

## 🛡️ Security

- ✅ Secrets managed via GitHub Secrets
- ✅ Never commit API keys to repository
- ✅ Fork isolation (secrets not accessible to forks)
- ✅ Dry-run mode when credentials missing

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Pull request process

## 📝 License

See LICENSE file for details.

## 🙋 Support

- **Documentation**: See DEPLOYMENT.md and CONFIGURE.md
- **Issues**: Open a GitHub issue with details
- **Discussions**: Use GitHub Discussions for questions

## 🎉 Acknowledgments

Built with:
- [feedparser](https://github.com/kurtmckee/feedparser) - RSS parsing
- [newspaper3k](https://github.com/codelucas/newspaper) - Article extraction
- [gTTS](https://github.com/pndurette/gTTS) - Text-to-speech
- [Open-Meteo](https://open-meteo.com/) - Weather data
- [Hugging Face](https://huggingface.co/) - AI inference

---

**Ready to automate your news?** Follow the [Quick Start](#-quick-start) above!

## Next Steps

- [📖 Read the Deployment Guide](DEPLOYMENT.md)
- [⚙️ Configure Your Topics](topics.yaml)
- [🔑 Add Your API Keys](https://github.com/vishc0/NewsGenerator/settings/secrets/actions)
- [🌐 Enable GitHub Pages](https://github.com/vishc0/NewsGenerator/settings/pages)
