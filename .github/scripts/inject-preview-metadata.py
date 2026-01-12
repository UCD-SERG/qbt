#!/usr/bin/env python3
"""
Script to inject preview metadata into changed .qmd files.
This adds metadata that triggers the preview banner.
"""

import os
import re
from pathlib import Path

def inject_metadata(filepath):
    """Add preview-changed metadata to a .qmd file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file already has YAML front matter
    yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n'
    yaml_match = re.match(yaml_pattern, content, re.DOTALL)
    
    if yaml_match:
        # File has YAML, check if preview-changed already exists
        yaml_content = yaml_match.group(1)
        if 'preview-changed:' in yaml_content:
            # Already has the metadata
            return False
        
        # Add preview-changed to existing YAML
        new_yaml = yaml_content + '\npreview-changed: true\n'
        new_content = f'---\n{new_yaml}---\n' + content[yaml_match.end():]
    else:
        # No YAML front matter, add it
        new_content = '---\npreview-changed: true\n---\n' + content
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    # Get list of changed chapters from environment
    changed_chapters = os.getenv('PREVIEW_CHANGED_CHAPTERS', '').strip()
    
    if not changed_chapters:
        print("No changed chapters to process")
        return
    
    # Convert chapter IDs to .qmd files
    changed_files = []
    for chapter_id in changed_chapters.split('\n'):
        chapter_id = chapter_id.strip()
        if chapter_id:
            qmd_file = Path(f"./{chapter_id}.qmd")
            if qmd_file.exists():
                changed_files.append(qmd_file)
    
    if not changed_files:
        print("No .qmd files found for changed chapters")
        return
    
    # Inject metadata into each file
    for qmd_file in changed_files:
        if inject_metadata(qmd_file):
            print(f"Injected metadata into {qmd_file}")
        else:
            print(f"Metadata already present in {qmd_file}")

if __name__ == '__main__':
    main()
