import argparse
import yaml
import logging
from pathlib import Path

from ingestors import rss_ingestor
from researcher import summarizer
from formatter import blog_formatter
from publisher import blog_publisher, podcast_publisher
from tts import gtts_tts

logging.basicConfig(level=logging.INFO)


def load_topics(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def clamp(n, lo, hi):
    return max(lo, min(hi, n))


def main(topics_file, since_hours):
    topics = load_topics(topics_file)
    out_dir = Path('outbox')
    out_dir.mkdir(exist_ok=True)

    for topic in topics:
        name = topic.get('name')
        sources = topic.get('sources', [])
        article_cap = clamp(topic.get('article_cap', 30), 1, 200)
        segments = clamp(topic.get('segments', 15), 1, 30)  # default 15 one-minute segments
        logging.info(f"Processing topic: {name} (cap={article_cap}, segments={segments})")

        articles = []
        for src in sources:
            try:
                entries = rss_ingestor.fetch_feed(src, since_hours)
                articles.extend(entries)
            except Exception as e:
                logging.warning(f"Failed to ingest {src}: {e}")

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
        summaries = []
        for art in unique[:segments]:
            try:
                text = rss_ingestor.fetch_article_text(art['link'])
                # ask summarizer for short segment sized for ~1 minute (approx 120-160 words)
                s = summarizer.summarize(text, model='google/flan-t5-small')
                summaries.append({'title': art.get('title'), 'summary': s, 'link': art.get('link')})
            except Exception as e:
                logging.warning(f"Failed to summarize {art.get('link')}: {e}")

        # write blog draft
        md = blog_formatter.format_topic(name, summaries)
        file_path = out_dir / f"{name.replace(' ', '_')}.md"
        file_path.write_text(md, encoding='utf-8')
        logging.info(f"Wrote draft for {name} -> {file_path}")
        blog_publisher.write_markdown_to_content(md, f"{name.replace(' ', '_')}.md")

        # TTS and podcast assembly
        podcast_dir = out_dir / 'podcasts' / name.replace(' ', '_')
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
            # publish step (dry-run unless IA keys present)
            # TODO: upload to Internet Archive when keys provided


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--topics', default='topics.yaml')
    parser.add_argument('--since', type=int, default=48)
    args = parser.parse_args()
    main(args.topics, args.since)
