#!/usr/bin/env python3
"""
Script to detect changed chapters by comparing rendered HTML and DOCX files.
This compares the PR's rendered files with the published versions from gh-pages.
"""

import os
import sys
import subprocess
from pathlib import Path

def checkout_base_files(base_ref='origin/gh-pages', target_dir='/tmp/base-files'):
    """
    Check out the base HTML and DOCX files from gh-pages for comparison.
    
    This may fail in the following scenarios:
    1. First PR to a new repository (gh-pages branch doesn't exist yet)
    2. Repository doesn't use gh-pages for deployment
    3. Network/permissions issues accessing the remote branch
    
    Returns:
        Path to directory with base files, or None if checkout failed
    """
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Fetch the gh-pages branch
        result = subprocess.run(
            ['git', 'fetch', 'origin', 'gh-pages:gh-pages'], 
            check=False, 
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Could not fetch gh-pages branch: {result.stderr}")
            print("This is expected for:")
            print("  - First PR to a new repository")
            print("  - Repositories not using gh-pages for deployment")
            return None
        
        # List all HTML and DOCX files in gh-pages
        result = subprocess.run(
            ['git', 'ls-tree', '-r', '--name-only', base_ref],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            files = [f for f in result.stdout.split('\n') 
                    if f.endswith('.html') or f.endswith('.docx')]
            
            # Extract each file
            for file in files:
                output_path = target_path / file
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'wb') as f:
                    subprocess.run(
                        ['git', 'show', f'{base_ref}:{file}'],
                        stdout=f,
                        check=False
                    )
            
            return target_path if files else None
        
        return None
    except Exception as e:
        print(f"Could not check out base files: {e}", file=sys.stderr)
        return None

def files_differ(file1, file2):
    """Check if two files differ."""
    if not file1.exists() or not file2.exists():
        # If one doesn't exist, they differ
        return file1.exists() or file2.exists()
    
    # Simple byte-level comparison
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return f1.read() != f2.read()
    except Exception:
        return True

def main():
    # Get the local rendered files directory
    rendered_dir = Path(os.getenv('HTML_DIR', './docs'))
    
    if not rendered_dir.exists():
        print("Rendered files directory does not exist yet")
        return
    
    # Check out base files from gh-pages
    print("Checking out base files from gh-pages for comparison...")
    base_dir = checkout_base_files()
    
    if not base_dir:
        print("\nWARNING: Could not check out base files from gh-pages")
        print("Treating all rendered files as changed.")
        print("\nReasons this might happen:")
        print("  1. This is the first PR and gh-pages branch doesn't exist yet")
        print("  2. Repository doesn't use gh-pages for deployment")
        print("  3. Network or permissions issue\n")
        
        # Treat all files as changed
        html_files = list(rendered_dir.glob("*.html"))
        changed_chapters = [f.stem for f in html_files if f.stem != 'index']
    else:
        print(f"Base files checked out successfully to {base_dir}\n")
        
        # Find all HTML files in rendered output
        html_files = list(rendered_dir.glob("*.html"))
        
        changed_chapters = []
        for html_file in html_files:
            # Skip index.html - we'll handle that separately
            if html_file.stem == 'index':
                continue
            
            # Check if HTML changed
            base_html = base_dir / f"docs/{html_file.name}"
            if not base_html.exists():
                base_html = base_dir / html_file.name
            
            html_changed = files_differ(html_file, base_html)
            
            # Check if corresponding DOCX changed
            docx_file = html_file.with_suffix('.docx')
            base_docx = base_dir / f"docs/{docx_file.name}"
            if not base_docx.exists():
                base_docx = base_dir / docx_file.name
            
            docx_changed = docx_file.exists() and files_differ(docx_file, base_docx)
            
            # If either changed, mark this chapter as changed
            if html_changed or docx_changed:
                changed_chapters.append(html_file.stem)
                print(f"  Changed: {html_file.stem} (HTML: {html_changed}, DOCX: {docx_changed})")
    
    if not changed_chapters:
        print("No chapters changed")
        env_file = os.getenv('GITHUB_ENV')
        if env_file:
            with open(env_file, 'a') as f:
                f.write("PREVIEW_CHANGED_CHAPTERS=\n")
                f.write("PREVIEW_SHOW_HIGHLIGHTS=false\n")
        
        # Still create the JSON file for home banner
        import json
        with open('./docs/changed-chapters.json', 'w') as f:
            json.dump({
                'changed_chapters': [],
                'count': 0
            }, f)
        print("Created empty changed-chapters.json file")
        return
    
    print(f"\nChanged chapters: {', '.join(changed_chapters)}")
    
    # Export as environment variable
    env_file = os.getenv('GITHUB_ENV')
    if env_file:
        with open(env_file, 'a') as f:
            f.write("PREVIEW_CHANGED_CHAPTERS<<EOF\n")
            f.write('\n'.join(changed_chapters) + '\n')
            f.write("EOF\n")
            # Check if highlighting should be disabled via environment variable
            # (This can be set based on PR labels in the workflow)
            disable_highlights = os.getenv('DISABLE_PREVIEW_HIGHLIGHTS', 'false').lower() == 'true'
            if disable_highlights:
                f.write("PREVIEW_SHOW_HIGHLIGHTS=false\n")
            else:
                f.write("PREVIEW_SHOW_HIGHLIGHTS=true\n")
    
    # Also create a JSON file for easy access
    import json
    with open('./docs/changed-chapters.json', 'w') as f:
        json.dump({
            'changed_chapters': changed_chapters,
            'count': len(changed_chapters)
        }, f)

if __name__ == '__main__':
    main()
