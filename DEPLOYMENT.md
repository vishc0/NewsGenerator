# NewsGenerator - Deployment & Operations Guide

This guide covers deploying and operating the NewsGenerator pipeline in production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [GitHub Actions Setup](#github-actions-setup)
5. [GitHub Pages Setup](#github-pages-setup)
6. [Internet Archive Setup](#internet-archive-setup)
7. [Testing & Validation](#testing--validation)
8. [Monitoring & Maintenance](#monitoring--maintenance)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Accounts
1. **GitHub Account** (you already have this)
2. **Hugging Face Account** (free) - for LLM summarization
   - Sign up: https://huggingface.co/join
   - Create access token: https://huggingface.co/settings/tokens
3. **Internet Archive Account** (free, optional) - for podcast hosting
   - Sign up: https://archive.org/account/create
   - API credentials: Available in account settings

### Optional Accounts
- **OpenAI Account** - fallback LLM option (paid)

## Initial Setup

### Step 1: Fork or Clone Repository
If you haven't already, ensure you have the repository set up in your GitHub account.

### Step 2: Add GitHub Secrets
Go to your repository on GitHub:
1. Navigate to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Add the following secrets:

| Secret Name | Description | Required |
|------------|-------------|----------|
| `HUGGINGFACE_API_KEY` | Your HF access token | Yes (for summarization) |
| `OPENAI_API_KEY` | Your OpenAI API key | No (optional fallback) |
| `INTERNET_ARCHIVE_ACCESS_KEY` | IA access key | No (for podcast hosting) |
| `INTERNET_ARCHIVE_SECRET` | IA secret key | No (for podcast hosting) |

**Important Security Notes:**
- Never commit these keys to the repository
- Secrets in your repo are not accessible to forks
- Use `.env` file for local development (never commit it)

## Configuration

### Configure Topics
Edit `topics.yaml` to customize what content you want to generate:

```yaml
- name: "My Custom Topic"
  sources:
    - "https://example.com/rss/feed.xml"
  lookback_hours: 48          # How far back to fetch articles
  cadence_per_day: 6          # Intended publishing frequency
  article_cap: 30             # Max articles per run
  segments: 12                # Number of podcast segments
```

**Topic Types:**
1. **RSS Topics** (default) - Fetch from RSS feeds
2. **Weather Topics** - Fetch weather data
   ```yaml
   - name: "Weather"
     type: "weather"
     provider: "open-meteo"
     locations:
       - name: "Your City"
         lat: 40.7128
         lon: -74.0060
   ```

### Configure Sources Directory (Optional)
Add manual content sources:

1. Create `sources/urls.txt` - one article URL per line
2. Create `sources/youtube_urls.txt` - one YouTube URL per line

These will be included in all topics.

## GitHub Actions Setup

The repository includes two workflows:

### 1. Scheduled Pipeline (`schedule-pipeline.yml`)
- Runs automatically every 6 hours
- Fetches news, generates content, creates podcasts
- Uploads to Internet Archive (if credentials provided)

**To enable:**
- No action needed - it's already set up
- Runs on: `0 */6 * * *` (every 6 hours)

**To customize schedule:**
Edit `.github/workflows/schedule-pipeline.yml`:
```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Change this line
```

Common cron schedules:
- Every 6 hours: `0 */6 * * *`
- Every 12 hours: `0 */12 * * *`
- Daily at midnight: `0 0 * * *`
- Every 2 hours: `0 */2 * * *`

### 2. Comment-Triggered Pipeline (`comment-trigger.yml`)
- Run on-demand by commenting `/run-pipeline` on a PR
- Useful for testing
- Only works for repository owners/collaborators

## GitHub Pages Setup

Host your blog for free using GitHub Pages:

### Step 1: Enable GitHub Pages
1. Go to **Settings → Pages**
2. Under **Source**, select:
   - Branch: `main` (or your default branch)
   - Folder: `/content`
3. Click **Save**

### Step 2: Add Jekyll Configuration
Create `content/_config.yml`:
```yaml
title: "Your News Blog"
description: "Automated news curation"
theme: jekyll-theme-minimal

# Pagination
paginate: 10
paginate_path: "/page:num/"
```

### Step 3: Verify Deployment
- Your blog will be available at: `https://YOUR_USERNAME.github.io/NewsGenerator/`
- New posts appear automatically after each pipeline run

## Internet Archive Setup

Host podcasts for free on Internet Archive:

### Step 1: Create Account
1. Sign up at https://archive.org/account/create
2. Verify your email

### Step 2: Get API Credentials
1. Go to https://archive.org/account/s3.php
2. Note your Access Key and Secret Key
3. Add them to GitHub Secrets (see above)

### Step 3: Verify Uploads
After the pipeline runs:
1. Check https://archive.org/@YOUR_USERNAME
2. Your uploads will appear as items
3. Each item has format: `newsgenerator-topic-name-YYYY-MM-DD`

### Step 4: Get Podcast URLs
- Direct MP3 URL: `https://archive.org/download/{identifier}/episode.mp3`
- Item page: `https://archive.org/details/{identifier}`

## Testing & Validation

### Local Testing
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt

# Create .env file with your keys
cp .env.example .env
# Edit .env and add your keys

# Run pipeline
python pipeline\run.py --topics topics.yaml --since 48
```

### Check Output
```powershell
# Blog posts (Jekyll format)
ls content\

# Podcast episodes
ls outbox\podcasts\

# Token usage report
cat outbox\token_usage_report.txt
```

### Test GitHub Actions Locally
Use `act` to test workflows locally:
```bash
# Install act: https://github.com/nektos/act
act -j run-pipeline
```

## Monitoring & Maintenance

### Check Pipeline Status
1. Go to **Actions** tab in GitHub
2. View recent workflow runs
3. Check for failures (red ❌) or success (green ✓)

### View Artifacts
After each run:
1. Click on a workflow run
2. Scroll to **Artifacts** section
3. Download outputs to inspect locally

### Monitor Token Usage
Check `outbox/token_usage_report.txt` in artifacts:
- Track API calls
- Monitor costs
- Identify failures

### Monitor Internet Archive Quota
- IA has upload limits (generally generous for free accounts)
- Monitor your account at https://archive.org/account
- Old content can be deleted to free space

## Troubleshooting

### Pipeline Fails: "No module named 'lxml_html_clean'"
**Solution:** Already fixed in `requirements.txt`. Update your dependencies:
```bash
pip install -r requirements.txt
```

### TTS Fails: "Failed to connect"
**Cause:** gTTS requires internet connectivity to Google's TTS service
**Solution:** Ensure the runner has internet access, or errors are expected in sandboxed environments

### Weather Data Fails
**Cause:** Network connectivity issues or API rate limiting
**Solution:** Open-Meteo is free and has generous limits. Ensure internet access.

### Summarization Returns Naive Fallback
**Cause:** No API keys provided or API failures
**Check:**
1. Verify `HUGGINGFACE_API_KEY` is set in GitHub Secrets
2. Check token usage report for errors
3. Verify Hugging Face API status

### Blog Not Updating on GitHub Pages
**Solutions:**
1. Check Pages is enabled: Settings → Pages
2. Verify source folder is `/content`
3. Wait 2-3 minutes for deployment
4. Check Actions tab for Pages deployment status

### Internet Archive Upload Fails
**Check:**
1. Credentials are correct in GitHub Secrets
2. Identifier doesn't already exist
3. File size is within limits (generally not an issue)
4. Check workflow logs for specific error

## Advanced Configuration

### Customize Blog Theme
Add to `content/_config.yml`:
```yaml
remote_theme: pages-themes/minimal@v0.2.0
```

Supported themes: https://pages.github.com/themes/

### Add Custom Domain
1. Add a `CNAME` file to `content/` with your domain
2. Configure DNS: Add CNAME record pointing to `YOUR_USERNAME.github.io`
3. Enable HTTPS in Pages settings

### Retention Policy
To avoid filling Internet Archive with old content, you can:
1. Delete items older than 30 days manually
2. Add a cleanup job to the pipeline (future enhancement)

### Rate Limiting
To avoid hitting API limits:
1. Reduce `article_cap` in `topics.yaml`
2. Reduce `segments` per topic
3. Increase schedule interval (e.g., every 12 hours instead of 6)

## Cost Estimates

### Free Tier (Recommended)
- **Hugging Face Inference API**: FREE (with rate limits)
- **Internet Archive**: FREE (unlimited storage for non-profit/personal use)
- **GitHub Actions**: FREE (2,000 minutes/month for public repos)
- **GitHub Pages**: FREE

### Paid Options
- **OpenAI GPT-3.5**: ~$0.002 per 1K tokens
  - Typical run: 50 articles × 500 tokens input + 150 tokens output ≈ $0.065/run
  - Daily (4 runs): ~$0.26/day = ~$8/month

## Support & Feedback

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review workflow logs in Actions tab
3. Open an issue on GitHub with:
   - Error message
   - Workflow run link
   - Steps to reproduce

## Next Steps

1. ✅ Add API keys to GitHub Secrets
2. ✅ Customize `topics.yaml` with your preferred topics
3. ✅ Enable GitHub Pages
4. ✅ Test the pipeline manually
5. ✅ Monitor first scheduled run
6. ✅ Subscribe to your podcast RSS feed!

Happy automating! 🎉
