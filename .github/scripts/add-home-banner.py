#!/usr/bin/env python3
"""
Script to add a banner to the home page linking to changed chapters.
"""

import os
import sys
import json
import re
from pathlib import Path

def add_home_page_banner(index_html_path, changed_chapters):
    """Add a banner to the home page with links to changed chapters."""
    with open(index_html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    if not changed_chapters:
        # No changes detected - show a different message
        banner = '''
<div class="preview-home-changes-banner">
    <p style="margin: 0;">
        <strong>📋 Changes in this PR:</strong> No changes were detected in the rendered book.
    </p>
</div>
'''
    else:
        # Create the banner HTML with links to changed chapters
        chapter_links = []
        for chapter_id in changed_chapters:
            # Convert chapter ID to readable title
            # E.g., "01-culture-and-conduct" -> "Culture and conduct"
            # First try to extract the title from the actual HTML file
            chapter_html = index_html_path.parent / f"{chapter_id}.html"
            title = chapter_id
            if chapter_html.exists():
                with open(chapter_html, 'r', encoding='utf-8') as cf:
                    content = cf.read()
                    # Look for the h1 heading
                    h1_match = re.search(r'<h1[^>]*>.*?<span class="chapter-number">(\d+)</span>\s*(.*?)</h1>', content, re.DOTALL)
                    if h1_match:
                        title = h1_match.group(2).strip()
                        chapter_num = h1_match.group(1)
                        title = f"{chapter_num}. {title}"
            
            chapter_links.append(f'<a href="{chapter_id}.html">{title}</a>')
        
        links_html = ', '.join(chapter_links)
        
        # Add DOCX link to the banner
        docx_filename = "UCD-SeRG-Lab-Manual-tracked-changes.docx"
        
        banner = f'''
<div class="preview-home-changes-banner">
    <p style="margin: 0;">
        <strong>📋 Changes in this PR:</strong> The following chapters have been modified: {links_html}
        <br>
        <strong>📄 DOCX with tracked changes:</strong> <a href="{docx_filename}" download>Download {docx_filename}</a>
        <br>
        <strong>💡 Tip:</strong> If change highlighting is glitchy, add the <code>no-preview-highlights</code> label to this PR to disable it.
    </p>
</div>
'''
    
    # Find insertion point (after <main> tag)
    main_match = re.search(r'(<main[^>]*>)', html)
    if main_match:
        insertion_point = main_match.end()
        html = html[:insertion_point] + banner + html[insertion_point:]
        
        # Write back
        with open(index_html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Added home page banner with {len(changed_chapters)} changed chapter(s)")
    else:
        print("Could not find insertion point for home page banner", file=sys.stderr)

def main():
    # Get the HTML directory
    html_dir = Path(os.getenv('HTML_DIR', './docs'))
    
    # Read changed chapters from JSON file or environment variable
    changed_chapters_file = html_dir / 'changed-chapters.json'
    changed_chapters = []
    
    if changed_chapters_file.exists():
        with open(changed_chapters_file, 'r') as f:
            data = json.load(f)
            changed_chapters = data.get('changed_chapters', [])
        print(f"Loaded {len(changed_chapters)} changed chapter(s) from JSON file")
    else:
        # Try to get from environment variable
        env_chapters = os.getenv('PREVIEW_CHANGED_CHAPTERS', '').strip()
        if env_chapters:
            changed_chapters = [ch.strip() for ch in env_chapters.split('\n') if ch.strip()]
            print(f"Got {len(changed_chapters)} changed chapter(s) from environment variable")
        else:
            print("No changed chapters found")
    
    # Add banner to ALL HTML files in the directory, not just index.html
    html_files = list(html_dir.glob('*.html'))
    print(f"Found {len(html_files)} HTML files to process")
    
    for html_file in html_files:
        add_home_page_banner(html_file, changed_chapters)

if __name__ == '__main__':
    main()
