"""Generate podcast RSS feed for iPhone and other podcast apps."""
import os
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET


def generate_podcast_rss(podcast_dir='outbox/podcasts', output_file='outbox/podcast_feed.xml',
                         title='NewsGenerator Podcast', description='Automated news summaries podcast',
                         base_url=None):
    """Generate an RSS 2.0 podcast feed from generated episodes.

    Args:
        podcast_dir: Directory containing topic subdirectories with episode.mp3 files
        output_file: Path to write the RSS feed
        title: Podcast title
        description: Podcast description
        base_url: Base URL where episodes will be hosted (e.g., Internet Archive URL or GitHub Pages)
    """
    podcast_path = Path(podcast_dir)
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Create RSS structure
    rss = ET.Element('rss', version='2.0')
    rss.set('xmlns:itunes', 'http://www.itunes.com/dtds/podcast-1.0.dtd')
    rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')

    channel = ET.SubElement(rss, 'channel')

    # Channel metadata
    ET.SubElement(channel, 'title').text = title
    ET.SubElement(channel, 'description').text = description
    ET.SubElement(channel, 'language').text = 'en-us'
    ET.SubElement(channel, 'pubDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    # iTunes-specific tags for better podcast app support
    itunes_author = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author')
    itunes_author.text = 'NewsGenerator'

    itunes_summary = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary')
    itunes_summary.text = description

    itunes_category = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category')
    itunes_category.set('text', 'News')

    # Find all episodes
    episodes_found = 0
    if podcast_path.exists():
        for topic_dir in sorted(podcast_path.iterdir()):
            if topic_dir.is_dir():
                episode_file = topic_dir / 'episode.mp3'
                if episode_file.exists():
                    episodes_found += 1
                    topic_name = topic_dir.name.replace('_', ' ')
                    episode_date = datetime.fromtimestamp(episode_file.stat().st_mtime)
                    file_size = episode_file.stat().st_size

                    item = ET.SubElement(channel, 'item')
                    ET.SubElement(item, 'title').text = f'{topic_name} - {episode_date.strftime("%Y-%m-%d")}'
                    ET.SubElement(item, 'description').text = f'Automated news summary for {topic_name}'
                    ET.SubElement(item, 'pubDate').text = episode_date.strftime('%a, %d %b %Y %H:%M:%S GMT')

                    # Enclosure (the audio file)
                    enclosure = ET.SubElement(item, 'enclosure')
                    if base_url:
                        audio_url = f'{base_url.rstrip("/")}/{topic_dir.name}/episode.mp3'
                    else:
                        # Relative path for local use
                        audio_url = str(episode_file)
                    enclosure.set('url', audio_url)
                    enclosure.set('length', str(file_size))
                    enclosure.set('type', 'audio/mpeg')

                    # iTunes duration (placeholder - would need ffprobe to get actual duration)
                    itunes_duration = ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
                    itunes_duration.text = '00:15:00'  # Placeholder

    # Write RSS feed
    tree = ET.ElementTree(rss)
    ET.indent(tree, space='  ')
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    print(f'Generated podcast RSS feed: {output_path}')
    print(f'Episodes found: {episodes_found}')

    return str(output_path)


def generate_blog_index(content_dir='content', output_file='content/index.md'):
    """Generate a simple index page for blog posts.

    Args:
        content_dir: Directory containing markdown blog posts
        output_file: Path to write the index
    """
    content_path = Path(content_dir)
    output_path = Path(output_file)

    if not content_path.exists():
        print(f'Content directory not found: {content_path}')
        return None

    posts = []
    for md_file in sorted(content_path.glob('*.md')):
        if md_file.name != 'index.md':
            topic_name = md_file.stem.replace('_', ' ')
            mod_time = datetime.fromtimestamp(md_file.stat().st_mtime)
            posts.append({
                'name': topic_name,
                'file': md_file.name,
                'date': mod_time.strftime('%Y-%m-%d %H:%M')
            })

    # Generate index
    lines = [
        '# NewsGenerator Blog',
        '',
        f'*Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}*',
        '',
        '## Latest Posts',
        ''
    ]

    for post in posts:
        lines.append(f'- [{post["name"]}]({post["file"]}) - {post["date"]}')

    lines.extend([
        '',
        '---',
        '',
        '*Generated by [NewsGenerator](https://github.com/vishc0/NewsGenerator)*'
    ])

    output_path.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Generated blog index: {output_path}')
    print(f'Posts found: {len(posts)}')

    return str(output_path)


if __name__ == '__main__':
    generate_podcast_rss()
    generate_blog_index()
