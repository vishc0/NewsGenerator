from pathlib import Path


def write_markdown_to_content(markdown_text, filename):
    content_dir = Path('content')
    content_dir.mkdir(exist_ok=True)
    target = content_dir / filename
    target.write_text(markdown_text, encoding='utf-8')
    return str(target)
