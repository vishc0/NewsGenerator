import argparse
import yaml
import logging
from pathlib import Path
import sys
import re
from datetime import datetime, timezone

# Ensure repository root is on sys.path so imports like `ingestors` work
# when running this file directly (e.g. `python pipeline/run.py`) under CI runners.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingestors import rss_ingestor, weather_ingestor, file_ingestor, youtube_ingestor
from researcher import summarizer, token_tracker
from formatter import blog_formatter
from publisher import blog_publisher, podcast_publisher, podcast_rss
from tts import gtts_tts
import os

logging.basicConfig(level=logging.INFO)


def utc_now():
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def load_topics(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def clamp(n, lo, hi):
    return max(lo, min(hi, n))


def sanitize_filename(name):
    """Convert a topic name to a safe filename by replacing problematic characters.
    
    Handles all common filesystem-reserved characters including Windows reserved chars.
    """
    # Replace filesystem-reserved characters with underscores
    return re.sub(r'[<>:"/\\|?*]', '_', name).replace(' ', '_')


def main(topics_file, since_hours):
    topics = load_topics(topics_file)
    out_dir = Path('outbox')
    out_dir.mkdir(exist_ok=True)
    
    # Check for Internet Archive credentials
    ia_access_key = os.getenv('INTERNET_ARCHIVE_ACCESS_KEY')
    ia_secret = os.getenv('INTERNET_ARCHIVE_SECRET')
    enable_ia_upload = bool(ia_access_key and ia_secret)
    
    if enable_ia_upload:
        logging.info("Internet Archive credentials found - uploads will be enabled")
    else:
        logging.info("Internet Archive credentials not found - running in dry-run mode")
    
    # Scan sources directory for additional inputs
    additional_sources = file_ingestor.scan_sources_directory('sources')
    logging.info(f"Found {len(additional_sources['urls'])} URLs, "
                f"{len(additional_sources['youtube_urls'])} YouTube URLs in sources/")
    
    # Track all episodes for RSS feed generation
    all_episodes = []

    for topic in topics:
        name = topic.get('name')
        topic_type = topic.get('type', 'rss')  # default to RSS
        article_cap = clamp(topic.get('article_cap', 30), 1, 200)
        segments = clamp(topic.get('segments', 15), 1, 30)  # default 15 one-minute segments
        logging.info(f"Processing topic: {name} (type={topic_type}, cap={article_cap}, segments={segments})")

        summaries = []
        
        # Handle weather topics differently
        if topic_type == 'weather':
            locations = topic.get('locations', [])
            provider = topic.get('provider', 'open-meteo')
            try:
                summaries = weather_ingestor.fetch_weather(locations, provider)
            except Exception as e:
                logging.warning(f"Failed to fetch weather data: {e}")
        else:
            # Handle RSS-based topics
            sources = topic.get('sources', [])
            articles = []
            
            # Fetch from RSS feeds
            for src in sources:
                try:
                    entries = rss_ingestor.fetch_feed(src, since_hours)
                    articles.extend(entries)
                except Exception as e:
                    logging.warning(f"Failed to ingest {src}: {e}")
            
            # Add articles from manual URLs in sources/urls.txt
            for url in additional_sources['urls']:
                try:
                    articles.append({
                        'title': f"Article from {url}",
                        'link': url,
                        'published': ''
                    })
                except Exception as e:
                    logging.warning(f"Failed to add URL {url}: {e}")
            
            # Add YouTube transcripts from sources/youtube_urls.txt
            for yt_url in additional_sources['youtube_urls']:
                try:
                    video_id = youtube_ingestor.extract_video_id(yt_url)
                    if video_id:
                        articles.append({
                            'title': f"YouTube Video {video_id}",
                            'link': yt_url,
                            'published': ''
                        })
                except Exception as e:
                    logging.warning(f"Failed to add YouTube URL {yt_url}: {e}")

            # naive dedupe by link and keep newest
            seen = set()
            unique = []
            for a in sorted(articles, key=lambda x: x.get('published', ''), reverse=True):
                if a['link'] in seen:
                    continue
                seen.add(a['link'])
                unique.append(a)

            unique = unique[:article_cap]

            # prepare per-segment summaries: one article -> one segment (best-effort)
            for art in unique[:segments]:
                try:
                    link = art['link']
                    
                    # Check if it's a YouTube URL using proper URL parsing
                    from urllib.parse import urlparse
                    parsed_url = urlparse(link)
                    is_youtube = parsed_url.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be', 'm.youtube.com']
                    
                    if is_youtube:
                        text = youtube_ingestor.fetch_transcript(link)
                    else:
                        text = rss_ingestor.fetch_article_text(link)
                    
                    # ask summarizer for short segment sized for ~1 minute (approx 120-160 words)
                    s = summarizer.summarize(text, model='google/flan-t5-small')
                    summaries.append({'title': art.get('title'), 'summary': s, 'link': art.get('link')})
                except Exception as e:
                    logging.warning(f"Failed to summarize {art.get('link')}: {e}")

        # write blog draft
        md = blog_formatter.format_topic(name, summaries, format_type='jekyll')
        safe_name = sanitize_filename(name)
        file_path = out_dir / f"{safe_name}.md"
        file_path.write_text(md, encoding='utf-8')
        logging.info(f"Wrote draft for {name} -> {file_path}")
        
        # Write to content directory with date-based filename for Jekyll
        date_prefix = utc_now().strftime('%Y-%m-%d')
        jekyll_filename = f"{date_prefix}-{safe_name}.md"
        blog_publisher.write_markdown_to_content(md, jekyll_filename)

        # TTS and podcast assembly
        podcast_dir = out_dir / 'podcasts' / safe_name
        podcast_dir.mkdir(parents=True, exist_ok=True)
        segment_files = []
        for idx, s in enumerate(summaries, start=1):
            seg_text = s.get('summary') or s.get('title')
            # short-circuit very long text by truncating to ~180 words
            words = seg_text.split()
            if len(words) > 180:
                seg_text = ' '.join(words[:180])
            mp3_path = str(podcast_dir / f"{idx:02d}.mp3")
            try:
                gtts_tts.text_to_speech_gtts(seg_text, mp3_path)
                segment_files.append(mp3_path)
            except Exception as e:
                logging.warning(f"TTS failed for segment {idx} of {name}: {e}")

        if segment_files:
            episode_path = podcast_publisher.concat_segments(segment_files, podcast_dir / 'episode.mp3')
            logging.info(f"Created episode: {episode_path}")
            
            # Upload to Internet Archive if credentials are available
            if enable_ia_upload:
                ia_metadata = podcast_publisher.generate_ia_metadata(
                    name,
                    description=f"Automated news curation for {name}"
                )
                success = podcast_publisher.upload_to_internet_archive(
                    episode_path,
                    ia_metadata,
                    access_key=ia_access_key,
                    secret=ia_secret,
                    dry_run=not enable_ia_upload
                )
                
                if success and enable_ia_upload:
                    # Track episode for RSS feed
                    episode_url = f"https://archive.org/download/{ia_metadata['identifier']}/episode.mp3"
                    all_episodes.append({
                        'topic_name': name,
                        'audio_url': episode_url,
                        'ia_identifier': ia_metadata['identifier'],
                        'metadata': ia_metadata
                    })
            else:
                logging.info(f"Skipping Internet Archive upload for {name} (no credentials)")
        else:
            logging.warning(f"No podcast segments created for {name}")
    
    # Generate podcast RSS feed if we have episodes
    if all_episodes and enable_ia_upload:
        logging.info(f"Generating podcast RSS feed with {len(all_episodes)} episodes")
        
        # Create RSS feed for each topic's episodes
        for ep in all_episodes:
            topic_name = ep['topic_name']
            rss_episodes = [podcast_rss.generate_episode_metadata(
                topic_name,
                f"outbox/podcasts/{sanitize_filename(topic_name)}/episode.mp3",
                ep['audio_url'].rsplit('/', 1)[0]  # Base URL
            )]
            
            rss_content = podcast_rss.create_podcast_rss(
                title=f"NewsGenerator: {topic_name}",
                description=f"Automated news curation for {topic_name}",
                author="NewsGenerator",
                email="news@example.com",  # TODO: Make this configurable
                link="https://github.com/vishc0/NewsGenerator",
                image_url="https://via.placeholder.com/1400x1400.png?text=NewsGenerator",  # TODO: Add real artwork
                episodes=rss_episodes
            )
            
            rss_file = out_dir / 'podcasts' / sanitize_filename(topic_name) / 'podcast.rss'
            podcast_rss.save_podcast_rss(rss_content, rss_file)
            logging.info(f"Podcast RSS feed saved to: {rss_file}")
    
    # Log token usage report at the end
    token_tracker.get_tracker().log_report()
    
    # Save token usage report to file
    tracker_file = out_dir / 'token_usage_report.txt'
    token_tracker.get_tracker().save_report(tracker_file)
    logging.info(f"Token usage report saved to: {tracker_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--topics', default='topics.yaml')
    parser.add_argument('--since', type=int, default=48)
    args = parser.parse_args()
    main(args.topics, args.since)
