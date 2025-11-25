from pathlib import Path
import logging


def read_urls_from_file(file_path):
    """Read URLs from a text file (one URL per line).
    
    Args:
        file_path: Path to the file containing URLs
    
    Returns:
        List of URL strings
    """
    urls = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    urls.append(line)
    except Exception as e:
        logging.warning(f"Failed to read URLs from {file_path}: {e}")
    
    return urls


def read_text_file(file_path):
    """Read content from a text file.
    
    Args:
        file_path: Path to the text file
    
    Returns:
        String containing the file content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.warning(f"Failed to read text file {file_path}: {e}")
        return ""


def scan_sources_directory(sources_dir='sources'):
    """Scan the sources directory for additional input files.
    
    Args:
        sources_dir: Path to the sources directory (default: 'sources')
    
    Returns:
        Dict with keys:
            - 'urls': list of URLs from urls.txt
            - 'youtube_urls': list of YouTube URLs from youtube_urls.txt
            - 'text_files': list of paths to .txt files (excluding urls.txt and youtube_urls.txt)
            - 'other_files': list of paths to other supported files (.md, .pdf, .docx)
    """
    result = {
        'urls': [],
        'youtube_urls': [],
        'text_files': [],
        'other_files': []
    }
    
    sources_path = Path(sources_dir)
    if not sources_path.exists():
        return result
    
    # Read URLs from urls.txt
    urls_file = sources_path / 'urls.txt'
    if urls_file.exists():
        result['urls'] = read_urls_from_file(urls_file)
    
    # Read YouTube URLs from youtube_urls.txt
    youtube_file = sources_path / 'youtube_urls.txt'
    if youtube_file.exists():
        result['youtube_urls'] = read_urls_from_file(youtube_file)
    
    # Scan for other text files
    for file_path in sources_path.glob('*.txt'):
        if file_path.name not in ['urls.txt', 'youtube_urls.txt']:
            result['text_files'].append(str(file_path))
    
    # Scan for other supported files
    for ext in ['.md', '.pdf', '.docx']:
        for file_path in sources_path.glob(f'*{ext}'):
            result['other_files'].append(str(file_path))
    
    return result


def extract_pdf_text(file_path):
    """Extract text from a PDF file (placeholder for future implementation).
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        String containing extracted text
    """
    # TODO: Implement PDF extraction using PyPDF2 or pdfplumber
    logging.warning(f"PDF extraction not yet implemented for {file_path}")
    return ""


def extract_docx_text(file_path):
    """Extract text from a DOCX file (placeholder for future implementation).
    
    Args:
        file_path: Path to the DOCX file
    
    Returns:
        String containing extracted text
    """
    # TODO: Implement DOCX extraction using python-docx
    logging.warning(f"DOCX extraction not yet implemented for {file_path}")
    return ""
