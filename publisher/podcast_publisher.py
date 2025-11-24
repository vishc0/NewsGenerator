from pydub import AudioSegment
from pathlib import Path


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


def upload_to_internet_archive(file_path, metadata, access_key=None, secret=None):
    try:
        from internetarchive import upload
    except Exception:
        raise RuntimeError('internetarchive package not installed')

    if not access_key or not secret:
        raise RuntimeError('IA credentials required')

    # This is a convenience wrapper; callers must provide a stable identifier
    identifier = metadata.get('identifier')
    if not identifier:
        raise RuntimeError('metadata.identifier required for Internet Archive')

    upload(identifier, file_path, metadata=metadata, access_key=access_key, secret=secret)
