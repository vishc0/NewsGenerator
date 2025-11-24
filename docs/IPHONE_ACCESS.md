# Accessing NewsGenerator Content on iPhone

This guide explains how to access your generated news blog posts and podcasts on your iPhone.

## Quick Start

### For Blog Posts
1. **Safari Browser**: Open Safari and navigate to your GitHub repository's `content/` folder
2. **GitHub Mobile App**: Install the [GitHub app](https://apps.apple.com/app/github/id1477376905) and browse markdown files directly

### For Podcasts
1. **Apple Podcasts**: Subscribe via RSS feed (see setup below)
2. **Overcast**: Excellent free app with RSS support - [Download](https://apps.apple.com/app/overcast/id888422857)
3. **Pocket Casts**: Premium podcast app with great organization - [Download](https://apps.apple.com/app/pocket-casts/id414834813)

---

## Detailed Setup Instructions

### Option 1: View Blog Posts on iPhone

#### Using Safari
1. Open Safari on your iPhone
2. Navigate to: `https://github.com/vishc0/NewsGenerator/tree/main/content`
3. Tap on any `.md` file to read the formatted blog post
4. Bookmark the page for easy access

#### Using GitHub Mobile App (Recommended)
1. Download the [GitHub app](https://apps.apple.com/app/github/id1477376905) from the App Store
2. Sign in with your GitHub account
3. Navigate to the NewsGenerator repository
4. Go to `content/` folder
5. Tap any markdown file to view formatted content
6. Star the repository for quick access

---

### Option 2: Listen to Podcasts on iPhone

#### Method A: Using Apple Podcasts (Built-in App)

**Prerequisites**: You need to host the podcast RSS feed on a public URL (GitHub Pages or Internet Archive).

1. Set up GitHub Pages for your repository:
   - Go to repository Settings → Pages
   - Enable GitHub Pages from the `main` branch, `/docs` folder
   - Move `outbox/podcast_feed.xml` to `docs/podcast_feed.xml`

2. Get your RSS feed URL:
   - Format: `https://vishc0.github.io/NewsGenerator/podcast_feed.xml`

3. Add to Apple Podcasts:
   - Open Apple Podcasts app
   - Tap "Library" → "Edit" → "Add a Show by URL..."
   - Paste your RSS feed URL
   - Tap "Subscribe"

#### Method B: Using Overcast (Recommended - Free)

[Overcast](https://apps.apple.com/app/overcast/id888422857) is an excellent free podcast app with private RSS feed support.

1. Download and install Overcast from the App Store
2. Open Overcast and create an account (or skip)
3. Tap the "+" button
4. Select "Add URL"
5. Paste your podcast RSS feed URL
6. Tap "Add"

**Why Overcast?**
- Free with no ads in playback
- Smart Speed (removes silences)
- Voice Boost (enhances speech clarity)
- Great for commuting

#### Method C: Using Pocket Casts

[Pocket Casts](https://apps.apple.com/app/pocket-casts/id414834813) is a premium podcast app with excellent organization features.

1. Download Pocket Casts from the App Store
2. Tap "Discover" → "..." (more) → "Add Private RSS Feed"
3. Paste your RSS feed URL
4. Tap "Subscribe"

#### Method D: Direct MP3 Access (No App Required)

If you don't want to set up RSS:

1. Go to your repository's Actions tab
2. Find the latest successful workflow run
3. Download the "newsgenerator-output" artifact
4. Extract the ZIP file
5. Find MP3 files in `outbox/podcasts/<topic>/episode.mp3`
6. Transfer to iPhone via:
   - AirDrop
   - iCloud Drive
   - Email attachment
   - Sync via iTunes/Finder

---

## Setting Up GitHub Pages for Hosting

To host your podcast RSS feed for easy access:

### Step 1: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages** (in left sidebar)
3. Under "Source", select **Deploy from a branch**
4. Choose **main** branch and **/ (root)** folder
5. Click **Save**
6. Wait a few minutes for the site to deploy

### Step 2: Create docs folder (for podcast hosting)

Add a workflow step to copy outputs to the docs folder:

```yaml
- name: Deploy to GitHub Pages
  run: |
    mkdir -p docs/podcasts
    cp -r outbox/podcast_feed.xml docs/
    cp -r outbox/podcasts/* docs/podcasts/
    cp -r content/* docs/
```

### Step 3: Access Your Content

After deployment, your content will be available at:
- **Blog**: `https://vishc0.github.io/NewsGenerator/`
- **Podcast RSS**: `https://vishc0.github.io/NewsGenerator/podcast_feed.xml`

---

## Alternative: Internet Archive Hosting (100% Free)

For permanent, free audio hosting:

1. Create an account at [archive.org](https://archive.org/account/create)
2. Upload your podcast episodes
3. Update the RSS feed with Internet Archive URLs
4. Subscribe to the RSS feed in your podcast app

The pipeline can be configured to auto-upload to Internet Archive - see `CONFIGURE.md` for setup instructions.

---

## Recommended iPhone Apps Summary

| App | Cost | Best For | RSS Support |
|-----|------|----------|-------------|
| Apple Podcasts | Free | Built-in, syncs across devices | ✅ (with public URL) |
| Overcast | Free | Best free option, Smart Speed | ✅ |
| Pocket Casts | $3.99 | Organization, cross-platform | ✅ |
| Castro | $3.99/mo | Queue management | ✅ |
| Safari | Free | Blog viewing | N/A |
| GitHub App | Free | Markdown viewing | N/A |

---

## Troubleshooting

### "Cannot add podcast" error
- Ensure your RSS feed URL is publicly accessible
- Check that the XML is valid at https://validator.w3.org/feed/

### Podcast not updating
- Most apps check for updates every few hours
- Pull down to refresh in your podcast app
- Verify the workflow has run successfully

### Audio quality issues
- Generated audio is 64kbps mono (optimized for voice)
- Use Overcast's "Voice Boost" feature for clearer audio

### Can't find the artifact
- Go to Actions tab in your repository
- Click on the latest workflow run
- Scroll down to "Artifacts" section
- Download "newsgenerator-output"

---

## Configuration Requirements

To enable the full pipeline, you need to configure:

1. **HUGGINGFACE_API_KEY** (required for summarization)
   - Create account: https://huggingface.co/join
   - Generate token: https://huggingface.co/settings/tokens
   - Add to GitHub Secrets

2. **OPENAI_API_KEY** (optional, fallback summarizer)
   - Create account: https://platform.openai.com/signup
   - Generate API key: https://platform.openai.com/api-keys
   - Add to GitHub Secrets

3. **Internet Archive Keys** (optional, for permanent hosting)
   - Create account: https://archive.org/account/create
   - Get API keys from settings
   - Add `INTERNET_ARCHIVE_ACCESS_KEY` and `INTERNET_ARCHIVE_SECRET` to GitHub Secrets

See `CONFIGURE.md` for detailed setup instructions.

---

## Questions?

If you have issues accessing content on your iPhone, please:
1. Check the troubleshooting section above
2. Open an issue on the GitHub repository
3. Include your iOS version and app name
