"""Podcast RSS feed generation for distribution via Apple Podcasts, Spotify, etc."""

from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def utc_now():
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def create_podcast_rss(
    title,
    description,
    author,
    email,
    link,
    image_url,
    episodes,
    language='en-us',
    category='News',
    explicit=False
):
    """Create a podcast RSS feed.
    
    Args:
        title: Podcast title
        description: Podcast description
        author: Author name
        email: Contact email
        link: Podcast website URL
        image_url: Podcast artwork URL (must be 1400x1400 to 3000x3000 px)
        episodes: List of episode dicts with keys:
            - title: Episode title
            - description: Episode description
            - audio_url: Direct URL to MP3 file
            - duration: Duration in seconds
            - publish_date: datetime object
            - guid: Unique identifier for the episode
        language: Language code (default: 'en-us')
        category: iTunes category (default: 'News')
        explicit: Whether podcast contains explicit content (default: False)
    
    Returns:
        RSS feed as XML string
    """
    # Create RSS root
    rss = ET.Element('rss', {
        'version': '2.0',
        'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
        'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
        'xmlns:atom': 'http://www.w3.org/2005/Atom'
    })
    
    channel = ET.SubElement(rss, 'channel')
    
    # Required channel elements
    ET.SubElement(channel, 'title').text = title
    ET.SubElement(channel, 'description').text = description
    ET.SubElement(channel, 'link').text = link
    ET.SubElement(channel, 'language').text = language
    ET.SubElement(channel, 'copyright').text = f'© {utc_now().year} {author}'
    ET.SubElement(channel, 'lastBuildDate').text = _format_rfc2822(utc_now())
    
    # iTunes specific elements
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = author
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text = description
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'yes' if explicit else 'no'
    
    # iTunes category
    itunes_category = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category', {'text': category})
    
    # iTunes image
    ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image', {'href': image_url})
    
    # Owner
    owner = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}owner')
    ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}name').text = author
    ET.SubElement(owner, '{http://www.itunes.com/dtds/podcast-1.0.dtd}email').text = email
    
    # Add episodes
    for ep in episodes:
        item = ET.SubElement(channel, 'item')
        
        ET.SubElement(item, 'title').text = ep.get('title', 'Untitled Episode')
        ET.SubElement(item, 'description').text = ep.get('description', '')
        
        # Audio enclosure
        audio_url = ep.get('audio_url', '')
        file_size = ep.get('file_size', 0)  # Size in bytes
        ET.SubElement(item, 'enclosure', {
            'url': audio_url,
            'length': str(file_size),
            'type': 'audio/mpeg'
        })
        
        ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = ep.get('guid', audio_url)
        ET.SubElement(item, 'pubDate').text = _format_rfc2822(ep.get('publish_date', utc_now()))
        
        # iTunes duration (HH:MM:SS or MM:SS)
        duration_seconds = ep.get('duration', 0)
        duration_str = _format_duration(duration_seconds)
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text = duration_str
        
        ET.SubElement(item, '{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit').text = 'no'
    
    # Pretty print XML
    xml_str = ET.tostring(rss, encoding='unicode')
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent='  ')


def _format_rfc2822(dt):
    """Format datetime as RFC 2822 for RSS feeds."""
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')


def _format_duration(seconds):
    """Format duration in seconds as HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def save_podcast_rss(rss_content, output_path):
    """Save RSS feed to file.
    
    Args:
        rss_content: RSS XML string
        output_path: Path to save the RSS file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    return str(output_path)


def generate_episode_metadata(topic_name, episode_path, base_url):
    """Generate metadata for a podcast episode.
    
    Args:
        topic_name: Name of the topic
        episode_path: Local path to the episode MP3 file
        base_url: Base URL where the MP3 will be hosted
    
    Returns:
        Dict with episode metadata
    """
    from pydub import AudioSegment
    import os
    
    episode_path = Path(episode_path)
    
    # Get file size
    file_size = episode_path.stat().st_size if episode_path.exists() else 0
    
    # Get duration (if file exists)
    duration = 0
    if episode_path.exists():
        try:
            audio = AudioSegment.from_file(str(episode_path))
            duration = len(audio) / 1000  # Convert milliseconds to seconds
        except Exception:
            pass
    
    # Generate episode metadata
    now = utc_now()
    date_str = now.strftime('%Y-%m-%d')
    
    # Construct audio URL
    audio_filename = episode_path.name
    audio_url = f"{base_url.rstrip('/')}/{audio_filename}"
    
    return {
        'title': f"{topic_name} - {date_str}",
        'description': f"Automated news curation for {topic_name} on {date_str}",
        'audio_url': audio_url,
        'file_size': file_size,
        'duration': duration,
        'publish_date': now,
        'guid': f"{topic_name}-{date_str}"
    }
