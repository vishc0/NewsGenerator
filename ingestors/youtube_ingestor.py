from youtube_transcript_api import YouTubeTranscriptApi
import re


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\n?#]+)',
        r'youtube\.com/embed/([^&\n?#]+)',
        r'youtube\.com/v/([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def fetch_transcript(video_url, languages=None):
    """Fetch transcript for a YouTube video.
    
    Args:
        video_url: YouTube video URL
        languages: List of language codes to try (default: ['en'])
    
    Returns:
        String containing the full transcript text
    """
    if languages is None:
        languages = ['en']
    
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {video_url}")
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        transcript_text = ' '.join([entry['text'] for entry in transcript_list])
        return transcript_text
    except Exception as e:
        raise RuntimeError(f"Failed to fetch transcript for video {video_id}: {str(e)}")


def fetch_transcripts_from_file(file_path, languages=None):
    """Read YouTube URLs from a file and fetch their transcripts.
    
    Args:
        file_path: Path to file containing one YouTube URL per line
        languages: List of language codes to try (default: ['en'])
    
    Returns:
        List of dicts with 'video_id', 'url', 'transcript' keys
    """
    results = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    for url in urls:
        try:
            video_id = extract_video_id(url)
            if not video_id:
                continue
            
            transcript = fetch_transcript(url, languages)
            results.append({
                'video_id': video_id,
                'url': url,
                'transcript': transcript,
                'title': f"YouTube Video {video_id}"
            })
        except Exception as e:
            results.append({
                'video_id': video_id or 'unknown',
                'url': url,
                'transcript': '',
                'title': f"YouTube Video (failed)",
                'error': str(e)
            })
    
    return results
