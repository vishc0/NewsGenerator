from pydub import AudioSegment
from pathlib import Path
import os
import logging
from datetime import datetime, timezone


def utc_now():
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def concat_segments(segment_paths, out_path):
    """Concatenate MP3 segments into a single MP3 episode.

    Requires `ffmpeg` available in PATH for pydub to export reliably.
    """
    combined = None
    for p in segment_paths:
        seg = AudioSegment.from_file(p, format='mp3')
        if combined is None:
            combined = seg
        else:
            combined += seg

    if combined is None:
        raise RuntimeError('No segments to combine')

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.export(out_path, format='mp3', bitrate='64k')
    return str(out_path)


def upload_to_internet_archive(file_path, metadata, access_key=None, secret=None, dry_run=False):
    """Upload a file to Internet Archive.
    
    Args:
        file_path: Path to the file to upload
        metadata: Dict with metadata (must include 'identifier')
        access_key: IA access key
        secret: IA secret key
        dry_run: If True, only log what would be uploaded without actually uploading
    
    Returns:
        True if successful (or if dry_run), False otherwise
    """
    try:
        from internetarchive import upload, get_item
    except Exception:
        raise RuntimeError('internetarchive package not installed')

    identifier = metadata.get('identifier')
    if not identifier:
        raise RuntimeError('metadata.identifier required for Internet Archive')

    if not access_key or not secret:
        if dry_run:
            logging.info(f"[DRY-RUN] Would upload {file_path} to Internet Archive with identifier: {identifier}")
            return True
        else:
            logging.warning("Internet Archive credentials not provided. Skipping upload.")
            return False
    
    if dry_run:
        logging.info(f"[DRY-RUN] Would upload {file_path} to Internet Archive")
        logging.info(f"[DRY-RUN] Identifier: {identifier}")
        logging.info(f"[DRY-RUN] Metadata: {metadata}")
        return True
    
    try:
        # Upload the file
        upload(identifier, file_path, metadata=metadata, access_key=access_key, secret=secret)
        logging.info(f"Successfully uploaded {file_path} to Internet Archive: https://archive.org/details/{identifier}")
        return True
    except Exception as e:
        logging.error(f"Failed to upload to Internet Archive: {e}")
        return False


def generate_ia_metadata(topic_name, description=None):
    """Generate metadata for Internet Archive upload.
    
    Args:
        topic_name: Name of the topic
        description: Optional description
    
    Returns:
        Dict with IA metadata
    """
    now = utc_now()
    date_str = now.strftime('%Y-%m-%d')
    identifier = f"newsgenerator-{topic_name.lower().replace(' ', '-')}-{date_str}"
    
    return {
        'identifier': identifier,
        'title': f"{topic_name} - {date_str}",
        'description': description or f"Automated news curation for {topic_name} on {date_str}",
        'mediatype': 'audio',
        'collection': 'opensource_audio',
        'creator': 'NewsGenerator',
        'date': date_str,
        'subject': ['news', 'automated', 'podcast', topic_name.lower()],
        'language': 'eng'
    }
