#!/usr/bin/env python3
"""
Script to compare rendered HTML files and highlight changed sections.
This compares the PR's rendered HTML with the published version from gh-pages.
"""

import os
import sys
import re
import difflib
import subprocess
from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape

class HTMLDiffer:
    """Compare HTML files and inject highlighting for changed sections."""
    
    def __init__(self, local_html_dir, base_html_dir=None):
        self.local_html_dir = Path(local_html_dir)
        self.base_html_dir = Path(base_html_dir) if base_html_dir else None
        
    def fetch_base_html(self, filepath):
        """Get the base (published) HTML for comparison."""
        if not self.base_html_dir:
            return None
            
        # Get the relative path and construct base path
        relative_path = filepath.relative_to(self.local_html_dir)
        base_path = self.base_html_dir / relative_path
        
        if not base_path.exists():
            print(f"  Base file not found: {base_path}", file=sys.stderr)
            return None
        
        try:
            with open(base_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"  Could not read {base_path}: {e}", file=sys.stderr)
            return None
    
    def extract_main_content(self, html):
        """Extract the main content section from HTML, ignoring navigation and metadata."""
        # Find the main content area (typically in <main> or specific div)
        main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
        if main_match:
            return main_match.group(1)
        
        # Fallback: look for common content containers
        content_match = re.search(r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        if content_match:
            return content_match.group(1)
        
        return html
    
    def normalize_html(self, html):
        """Normalize HTML for better comparison (remove extra whitespace, etc.)."""
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html)
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        return html.strip()
    
    def highlight_html_diff(self, old_html, new_html):
        """Highlight differences between old and new HTML content, preserving HTML tags."""
        # Extract text for comparison, but keep track of HTML structure
        old_text = self.extract_text_from_element(f'<div>{old_html}</div>')
        new_text = self.extract_text_from_element(f'<div>{new_html}</div>')
        
        # If the HTML is very different or one is empty, fall back to simple comparison
        if not old_text or not new_text:
            return new_html
        
        # Split into words for both text versions
        old_words = re.findall(r'\S+|\s+', old_text)
        new_words = re.findall(r'\S+|\s+', new_text)
        
        # Use SequenceMatcher to find differences at word level
        matcher = difflib.SequenceMatcher(None, old_words, new_words)
        
        # Build a set of word positions that changed
        changed_ranges = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag in ('replace', 'insert'):
                # Track the character positions of changed words in new_text
                start_pos = len(''.join(new_words[:j1]))
                end_pos = len(''.join(new_words[:j2]))
                changed_ranges.append((start_pos, end_pos, tag))
        
        # If no changes detected, return original
        if not changed_ranges:
            return new_html
        
        # Now apply highlighting to the HTML, preserving tags
        # We'll use a simple approach: wrap changed text segments with <mark> tags
        # This is tricky with HTML, so we'll use a token-based approach
        
        # Parse HTML into tokens (tags and text)
        html_tokens = re.findall(r'(<[^>]+>|[^<]+)', new_html)
        
        result = []
        text_pos = 0  # Track position in the plain text
        
        for token in html_tokens:
            if token.startswith('<'):
                # It's a tag, keep it as-is
                result.append(token)
            else:
                # It's text content - check if any part needs highlighting
                token_len = len(token)
                token_end = text_pos + token_len
                
                # Check which parts of this token overlap with changed ranges
                highlighted = self.apply_highlights_to_text(token, text_pos, changed_ranges)
                result.append(highlighted)
                
                text_pos = token_end
        
        return ''.join(result)
    
    def apply_highlights_to_text(self, text, text_start_pos, changed_ranges):
        """Apply highlight marks to a text segment based on changed ranges."""
        if not text.strip():
            return text  # Don't highlight whitespace-only
        
        # Find which changed ranges overlap with this text segment
        text_end_pos = text_start_pos + len(text)
        overlapping = []
        
        for start, end, change_type in changed_ranges:
            if start < text_end_pos and end > text_start_pos:
                # Calculate overlap within this text segment
                overlap_start = max(0, start - text_start_pos)
                overlap_end = min(len(text), end - text_start_pos)
                overlapping.append((overlap_start, overlap_end, change_type))
        
        if not overlapping:
            return text
        
        # Sort by start position
        overlapping.sort()
        
        # Build result with highlights
        result = []
        last_end = 0
        
        for overlap_start, overlap_end, change_type in overlapping:
            # Add unchanged text before this highlight
            if overlap_start > last_end:
                result.append(text[last_end:overlap_start])
            
            # Add highlighted text
            highlighted_text = text[overlap_start:overlap_end]
            if change_type == 'replace':
                result.append(f'<mark class="preview-text-changed">{highlighted_text}</mark>')
            elif change_type == 'insert':
                result.append(f'<mark class="preview-text-added">{highlighted_text}</mark>')
            
            last_end = overlap_end
        
        # Add any remaining text
        if last_end < len(text):
            result.append(text[last_end:])
        
        return ''.join(result)
    
    def highlight_text_diff(self, old_text, new_text):
        """Highlight differences between old and new text at word/phrase level."""
        # Split into words while preserving spaces
        old_words = re.findall(r'\S+|\s+', old_text)
        new_words = re.findall(r'\S+|\s+', new_text)
        
        # Use SequenceMatcher to find differences
        matcher = difflib.SequenceMatcher(None, old_words, new_words)
        
        result = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # No change, keep as is
                result.extend(new_words[j1:j2])
            elif tag == 'replace':
                # Text was changed - highlight the new text
                changed_text = ''.join(new_words[j1:j2])
                result.append(f'<mark class="preview-text-changed" title="Modified from: {escape("".join(old_words[i1:i2]))}">{changed_text}</mark>')
            elif tag == 'insert':
                # Text was added - highlight as insertion
                added_text = ''.join(new_words[j1:j2])
                result.append(f'<mark class="preview-text-added">{added_text}</mark>')
            elif tag == 'delete':
                # Text was deleted - we don't show deletions in the new version
                pass
        
        return ''.join(result)
    
    def extract_text_from_element(self, element_html):
        """Extract plain text from an HTML element, preserving basic structure."""
        # Remove inner HTML tags but keep the text
        text = re.sub(r'<[^>]+>', '', element_html)
        return unescape(text).strip()
    
    def highlight_changed_elements(self, old_html, new_html):
        """Find and highlight changed paragraphs and sections in the HTML."""
        if not old_html:
            return new_html, 0
        
        # Constants for similarity matching
        SIMILARITY_THRESHOLD_MIN = 0.5  # Minimum similarity to consider elements related
        SIMILARITY_THRESHOLD_MAX = 0.99  # Maximum similarity to still highlight differences
        
        # Extract main content for both versions
        old_content = self.extract_main_content(old_html)
        new_content = self.extract_main_content(new_html)
        
        # Define element types to compare
        COMPARABLE_ELEMENTS = 'p|h[1-6]|li|blockquote'
        element_pattern = f'(<(?:{COMPARABLE_ELEMENTS})[^>]*>.*?</(?:{COMPARABLE_ELEMENTS})>)'
        
        old_elements = re.findall(element_pattern, old_content, re.DOTALL)
        new_elements = re.findall(element_pattern, new_content, re.DOTALL)
        
        # Create a list of (text, element) tuples to handle duplicates
        old_elem_list = []
        for elem in old_elements:
            text = self.extract_text_from_element(elem)
            if text:  # Only store non-empty elements
                old_elem_list.append((text, elem))
        
        # Track which old elements have been matched to avoid reuse
        used_old_indices = set()
        
        # Process each new element and check if it changed
        highlighted_new_html = new_html
        changes_made = 0
        
        for new_elem in new_elements:
            new_text = self.extract_text_from_element(new_elem)
            if not new_text:
                continue
            
            # Try to find a matching old element
            best_match_idx = None
            best_ratio = 0.0
            
            for idx, (old_text, old_elem) in enumerate(old_elem_list):
                if idx in used_old_indices:
                    continue  # Already matched this element
                    
                ratio = difflib.SequenceMatcher(None, old_text, new_text).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match_idx = idx
            
            # If we found a similar element and it's not identical, highlight the differences
            if best_match_idx is not None and best_ratio > SIMILARITY_THRESHOLD_MIN and best_ratio < SIMILARITY_THRESHOLD_MAX:
                used_old_indices.add(best_match_idx)
                old_text, old_elem = old_elem_list[best_match_idx]
                
                # Extract the inner text from the new element
                tag_match = re.match(r'(<[^>]+>)(.*)(</[^>]+>)', new_elem, re.DOTALL)
                if tag_match:
                    open_tag, inner_content, close_tag = tag_match.groups()
                    
                    # Get the old element's inner content
                    old_tag_match = re.match(r'(<[^>]+>)(.*)(</[^>]+>)', old_elem, re.DOTALL)
                    old_inner_content = old_tag_match.group(2) if old_tag_match else ""
                    
                    # Highlight the differences using inner HTML (preserves formatting)
                    highlighted_inner = self.highlight_html_diff(old_inner_content, inner_content)
                    
                    # Reconstruct the element with highlighting
                    highlighted_elem = f'{open_tag}{highlighted_inner}{close_tag}'
                    
                    # Replace in the HTML - use a unique marker to ensure we replace the right instance
                    # We escape the element for regex safety
                    escaped_elem = re.escape(new_elem)
                    highlighted_new_html = re.sub(escaped_elem, highlighted_elem, highlighted_new_html, count=1)
                    changes_made += 1
            
            elif (best_match_idx is None or best_ratio < SIMILARITY_THRESHOLD_MIN) and new_text:
                # This is a completely new element - highlight the whole thing
                tag_match = re.match(r'(<[^>]+>)(.*)(</[^>]+>)', new_elem, re.DOTALL)
                if tag_match:
                    open_tag, inner_content, close_tag = tag_match.groups()
                    
                    # Mark the entire element as new, but preserve the inner HTML
                    highlighted_elem = f'{open_tag}<mark class="preview-element-added">{inner_content}</mark>{close_tag}'
                    
                    # Replace in the HTML using regex with escaping
                    escaped_elem = re.escape(new_elem)
                    highlighted_new_html = re.sub(escaped_elem, highlighted_elem, highlighted_new_html, count=1)
                    changes_made += 1
        
        return highlighted_new_html, changes_made
    
    def find_changed_sections(self, old_html, new_html):
        """Find sections that changed between old and new HTML."""
        if not old_html:
            return None, 0
        
        old_content = self.normalize_html(self.extract_main_content(old_html))
        new_content = self.normalize_html(self.extract_main_content(new_html))
        
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, old_content, new_content).ratio()
        
        # If content is nearly identical, no need to highlight
        if similarity > 0.95:
            return None, similarity
        
        # Use unified diff to find changed lines
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        differ = difflib.unified_diff(old_lines, new_lines, lineterm='')
        diff_lines = list(differ)
        
        # Count changes
        changes = sum(1 for line in diff_lines if line.startswith('+') or line.startswith('-'))
        
        return diff_lines if changes > 0 else None, similarity
    
    def inject_combined_banner(self, html, num_changes, similarity, filename):
        """Add a combined banner about all changes to the HTML."""
        # Calculate change percentage
        change_pct = int((1 - similarity) * 100)
        
        # Create combined notice HTML - using CSS class defined in styles.css
        # Note: DOCX link removed from chapter banners - it's only in the home page banner
        notice = f'''
<div class="preview-combined-banner">
    <p style="margin: 0;">
        <strong>📝 Preview Changes:</strong> This page has been modified in this pull request (~{change_pct}% of content changed).
        <br>
        <strong>🎨 Highlighting Legend:</strong> 
        <mark class="preview-text-changed" style="display: inline; padding: 1px 3px;">Modified text (yellow)</mark> shows changed words/phrases with tooltips of original text, 
        <mark class="preview-text-added" style="display: inline; padding: 1px 3px;">added text (green)</mark> shows new content, and 
        <mark class="preview-element-added" style="display: inline; padding: 1px 3px;">new sections (blue)</mark> highlight entirely new paragraphs.
    </p>
</div>
'''
        
        # Replace the placeholder banner if it exists
        placeholder_pattern = r'<div class="preview-changed-banner"[^>]*>.*?PREVIEW_BANNER_PLACEHOLDER.*?</div>'
        if re.search(placeholder_pattern, html, re.DOTALL):
            html = re.sub(placeholder_pattern, notice, html, flags=re.DOTALL)
        else:
            # No placeholder, insert at the start of main content
            main_match = re.search(r'(<main[^>]*>)', html)
            if main_match:
                insertion_point = main_match.end()
                html = html[:insertion_point] + notice + html[insertion_point:]
        
        return html
    
    def inject_change_notice(self, html, num_changes, similarity):
        """Add a notice about content changes to the HTML (deprecated - now using combined banner)."""
        # This method is kept for backward compatibility but is no longer used
        # The inject_combined_banner method is used instead
        return html
    
    def highlight_toc_entries(self, html, changed_files):
        """Highlight table of contents entries for changed files."""
        if not changed_files:
            return html
        
        # changed_files should already be HTML filenames
        changed_html_files = set(changed_files)
        
        # Find all TOC links and add highlighting class to those that point to changed files
        # TOC links are typically in the sidebar navigation
        for html_file in changed_html_files:
            # Pattern to match TOC links - look for links in the sidebar navigation
            # that point to the changed file
            pattern = rf'(<a[^>]*href="[^"]*{re.escape(html_file)}[^"]*"[^>]*class="[^"]*")([^"]*"[^>]*>)'
            
            def add_toc_highlight_class(match):
                prefix = match.group(1)
                suffix = match.group(2)
                # Add our highlighting class
                return f'{prefix} preview-toc-changed{suffix}'
            
            html = re.sub(pattern, add_toc_highlight_class, html)
        
        return html
    
    def process_file(self, local_filepath):
        """Process a single HTML file: fetch old version, compare, and highlight."""
        print(f"Processing {local_filepath}...")
        print(f"  File path: {local_filepath}")
        print(f"  File exists: {local_filepath.exists()}")
        
        # Read the new (PR) version
        with open(local_filepath, 'r', encoding='utf-8') as f:
            new_html = f.read()
        
        print(f"  HTML length: {len(new_html)} chars")
        
        # Check if there's a placeholder that needs replacing
        has_placeholder = 'PREVIEW_BANNER_PLACEHOLDER' in new_html
        print(f"  Has placeholder: {has_placeholder}")
        
        # Fetch the published (main) version
        old_html = self.fetch_base_html(local_filepath)
        
        if old_html:
            print(f"  Old HTML length: {len(old_html)} chars")
            
            # Find what changed
            diff_lines, similarity = self.find_changed_sections(old_html, new_html)
            
            # Always try to apply inline highlighting, regardless of similarity
            # This catches paragraph-level changes even when overall similarity is high
            print(f"  Checking for inline changes (overall similarity: {similarity:.2%})...")
            highlighted_html, inline_changes = self.highlight_changed_elements(old_html, new_html)
            
            if inline_changes > 0:
                print(f"  ✓ Highlighted {inline_changes} changed element(s) inline")
                # Verify the highlighting was actually applied
                if '<mark class="preview-' in highlighted_html:
                    print(f"  ✓ Confirmed <mark> tags present in highlighted HTML")
                else:
                    print(f"  ✗ WARNING: No <mark> tags found after highlighting!")
                new_html = highlighted_html
            else:
                print(f"  No inline changes detected")
            
            if diff_lines or has_placeholder:
                # Add combined banner with DOCX link
                num_changes = len([l for l in diff_lines if l.startswith('+') or l.startswith('-')]) if diff_lines else 0
                print(f"  Adding combined banner (changes: {num_changes}, similarity: {similarity:.2%})")
                new_html = self.inject_combined_banner(new_html, num_changes, similarity, local_filepath)
            
            # Always write back if we made ANY changes (inline or banner)
            if diff_lines or has_placeholder or inline_changes > 0:
                print(f"  Writing changes back to file...")
                with open(local_filepath, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                print(f"  ✓ Updated {local_filepath}")
                
                # Verify the file was written correctly
                with open(local_filepath, 'r', encoding='utf-8') as f:
                    verify_html = f.read()
                if '<mark class="preview-' in verify_html:
                    print(f"  ✓ Verified <mark> tags in written file")
                else:
                    print(f"  ✗ WARNING: No <mark> tags in written file!")
            else:
                print(f"  No changes to write")
        elif has_placeholder:
            # Could not fetch base version but placeholder exists - replace with new file banner
            print(f"  Could not fetch base version (file may be new)")
            print(f"  Replacing placeholder with new file banner")
            # Use 0 similarity to show 100% changed
            new_html = self.inject_combined_banner(new_html, 1, 0.0, local_filepath)
            with open(local_filepath, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"  ✓ Updated {local_filepath}")
        else:
            print(f"  Could not fetch base version (file may be new)")


def checkout_base_html(base_ref='origin/gh-pages', target_dir='/tmp/base-html'):
    """Check out the base HTML files from gh-pages for comparison."""
    target_path = Path(target_dir)
    
    # Create target directory
    target_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try to fetch the gh-pages branch
        subprocess.run(['git', 'fetch', 'origin', 'gh-pages:gh-pages'], 
                      check=False, capture_output=True)
        
        # Check out just the docs or root directory from gh-pages
        result = subprocess.run(
            ['git', 'show', f'{base_ref}:docs/'],
            capture_output=True,
            check=False
        )
        
        if result.returncode != 0:
            # Try root directory instead
            result = subprocess.run(
                ['git', 'ls-tree', '-r', '--name-only', base_ref],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                files = [f for f in result.stdout.split('\n') if f.endswith('.html')]
                
                # Extract each HTML file
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
        print(f"Could not check out base HTML: {e}", file=sys.stderr)
        return None

def main():
    # Get the local HTML directory
    html_dir = os.getenv('HTML_DIR', './docs')
    
    # Get list of changed HTML files (derived from changed .qmd files)
    changed_files = os.getenv('PREVIEW_CHANGED_CHAPTERS', '').strip()
    
    if not changed_files:
        print("No changed files to process")
        return
    
    # Try to check out base HTML from gh-pages
    print("Checking out base HTML from gh-pages...")
    base_html_dir = checkout_base_html()
    
    if not base_html_dir:
        print("Warning: Could not check out base HTML, will skip content comparison")
        print("(This is normal for new files or if gh-pages doesn't exist yet)")
    else:
        print(f"Base HTML checked out to {base_html_dir}")
    
    # changed_files contains chapter IDs (e.g., "02-communication")
    # Convert to .html files
    html_files = []
    changed_chapter_ids = []
    for chapter_id in changed_files.split('\n'):
        chapter_id = chapter_id.strip()
        if chapter_id:
            changed_chapter_ids.append(chapter_id)
            # Chapter ID to HTML file
            html_file = f"{chapter_id}.html"
            html_path = Path(html_dir) / html_file
            if html_path.exists():
                html_files.append(html_path)
    
    if not html_files:
        print("No HTML files to process")
        return
    
    # Create differ and process files
    differ = HTMLDiffer(html_dir, base_html_dir)
    
    for html_file in html_files:
        differ.process_file(html_file)
    
    # Highlight TOC entries in all HTML files (not just changed ones)
    print("\nHighlighting table of contents entries for changed chapters...")
    all_html_files = list(Path(html_dir).glob("*.html"))
    
    for html_path in all_html_files:
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()
            
            # Add TOC highlighting - convert chapter IDs to HTML filenames for TOC
            changed_html_files = [f"{ch_id}.html" for ch_id in changed_chapter_ids]
            highlighted_html = differ.highlight_toc_entries(html, changed_html_files)
            
            # Only write back if something changed
            if highlighted_html != html:
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(highlighted_html)
                print(f"  Added TOC highlighting to {html_path.name}")
        except Exception as e:
            print(f"  Error processing {html_path}: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
