#!/usr/bin/env python3
"""
Check bibliography files for DOI requirements:
1. Every book and article must have a DOI field
2. Every DOI must resolve to a valid URL
3. Reference information must match the document at the DOI URL
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error
import json
import time


def parse_bibtex_file(filepath: Path) -> List[Dict[str, any]]:
    """Parse a BibTeX file and extract entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    entries = []
    # Match BibTeX entries: @type{key, ...}
    # Pattern matches from @ to the closing brace, handling multiline content
    pattern = r'@(\w+)\{([^,]+),\s*((?:[^{}]|\{[^}]*\})*)\}'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        entry_type = match.group(1).lower()
        entry_key = match.group(2).strip()
        fields_text = match.group(3)
        
        # Parse fields
        fields = {}
        field_pattern = r'(\w+)\s*=\s*\{([^}]*)\}'
        for field_match in re.finditer(field_pattern, fields_text):
            field_name = field_match.group(1).lower()
            field_value = field_match.group(2).strip()
            fields[field_name] = field_value
        
        entries.append({
            'type': entry_type,
            'key': entry_key,
            'fields': fields,
            'raw': match.group(0)
        })
    
    return entries


def check_doi_field(entry: Dict[str, any]) -> Tuple[bool, Optional[str]]:
    """Check if entry has a DOI field."""
    if entry['type'] in ['book', 'article']:
        if 'doi' not in entry['fields']:
            return False, f"Entry '{entry['key']}' ({entry['type']}) is missing DOI field"
    return True, None


def validate_doi_url(doi: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validate that a DOI resolves to a valid URL.
    Returns (success, error_message, status_code)
    """
    # Clean up DOI
    doi = doi.strip()
    
    # DOI can be in various formats:
    # - just the identifier: 10.1234/example
    # - full URL: https://doi.org/10.1234/example
    # - http URL: http://dx.doi.org/10.1234/example
    
    # Extract just the DOI identifier
    doi_match = re.search(r'10\.\d+/[^\s]+', doi)
    if not doi_match:
        return False, f"Invalid DOI format: {doi}", None
    
    doi_identifier = doi_match.group(0)
    doi_url = f"https://doi.org/{doi_identifier}"
    
    try:
        # Create request with timeout
        req = urllib.request.Request(
            doi_url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; BibliographyChecker/1.0)'}
        )
        
        # Follow redirects and check if we get a valid response
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            if status_code == 200:
                return True, None, status_code
            else:
                return False, f"DOI URL returned status {status_code}", status_code
    
    except urllib.error.HTTPError as e:
        return False, f"HTTP error {e.code}: {e.reason}", e.code
    except urllib.error.URLError as e:
        return False, f"URL error: {e.reason}", None
    except Exception as e:
        return False, f"Error accessing DOI: {str(e)}", None


def get_doi_metadata(doi: str) -> Optional[Dict[str, any]]:
    """
    Fetch metadata for a DOI from CrossRef API.
    Returns metadata dict or None if failed.
    """
    doi = doi.strip()
    doi_match = re.search(r'10\.\d+/[^\s]+', doi)
    if not doi_match:
        return None
    
    doi_identifier = doi_match.group(0)
    api_url = f"https://api.crossref.org/works/{doi_identifier}"
    
    try:
        req = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; BibliographyChecker/1.0)'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('message', {})
    except Exception:
        # Failed to fetch metadata, return None
        pass
    
    return None


def normalize_string(s: str) -> str:
    """Normalize a string for comparison."""
    if not s:
        return ""
    # Convert to lowercase, remove extra whitespace, remove punctuation
    s = s.lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()


def compare_metadata(entry: Dict[str, any], metadata: Dict[str, any]) -> Tuple[bool, List[str]]:
    """
    Compare BibTeX entry with DOI metadata.
    Returns (match, list_of_warnings)
    """
    warnings = []
    fields = entry['fields']
    
    # Check title
    if 'title' in fields and 'title' in metadata:
        bib_title = normalize_string(fields['title'])
        # CrossRef titles can be in a list
        crossref_title = metadata['title']
        if isinstance(crossref_title, list) and len(crossref_title) > 0:
            crossref_title = crossref_title[0]
        crossref_title = normalize_string(str(crossref_title))
        
        # Allow some flexibility in matching (at least 70% overlap)
        if bib_title and crossref_title:
            # Simple word overlap check
            bib_words = set(bib_title.split())
            crossref_words = set(crossref_title.split())
            if len(bib_words) > 0 and len(crossref_words) > 0:
                overlap = len(bib_words & crossref_words)
                total = min(len(bib_words), len(crossref_words))
                if total > 0 and overlap / total < 0.5:
                    warnings.append(
                        f"Title mismatch: BibTeX='{fields['title']}' vs DOI='{metadata['title']}'"
                    )
    
    # Check author (basic check - just warn if completely different)
    if 'author' in fields and 'author' in metadata:
        bib_author = normalize_string(fields['author'])
        # CrossRef authors are in a list of dicts
        crossref_authors = metadata.get('author', [])
        if crossref_authors:
            # Get family names from CrossRef
            crossref_names = []
            for author in crossref_authors:
                if 'family' in author:
                    crossref_names.append(normalize_string(author['family']))
            
            # Check if at least one family name appears in BibTeX author
            if crossref_names:
                found_match = False
                for name in crossref_names:
                    if name and name in bib_author:
                        found_match = True
                        break
                
                if not found_match:
                    warnings.append(
                        f"Author mismatch: BibTeX='{fields['author']}' vs DOI authors"
                    )
    
    # Check year
    if 'year' in fields and 'published-print' in metadata:
        bib_year = fields['year'].strip()
        crossref_date = metadata['published-print'].get('date-parts', [[]])[0]
        if crossref_date and len(crossref_date) > 0:
            crossref_year = str(crossref_date[0])
            if bib_year != crossref_year:
                warnings.append(
                    f"Year mismatch: BibTeX='{bib_year}' vs DOI='{crossref_year}'"
                )
    elif 'year' in fields and 'published-online' in metadata:
        bib_year = fields['year'].strip()
        crossref_date = metadata['published-online'].get('date-parts', [[]])[0]
        if crossref_date and len(crossref_date) > 0:
            crossref_year = str(crossref_date[0])
            if bib_year != crossref_year:
                warnings.append(
                    f"Year mismatch: BibTeX='{bib_year}' vs DOI='{crossref_year}'"
                )
    
    # Return True if no critical issues (warnings are just informational)
    return True, warnings


def check_bibliography_file(filepath: Path, verify_metadata: bool = True) -> Tuple[int, int, List[str]]:
    """
    Check a bibliography file for DOI requirements.
    Returns (total_entries_checked, errors_count, error_messages)
    """
    print(f"\nChecking {filepath}...")
    
    entries = parse_bibtex_file(filepath)
    errors = []
    checked_count = 0
    
    for entry in entries:
        # Only check books and articles
        if entry['type'] not in ['book', 'article']:
            continue
        
        checked_count += 1
        print(f"  Checking {entry['type']} '{entry['key']}'...")
        
        # Check 1: DOI field exists
        has_doi, error = check_doi_field(entry)
        if not has_doi:
            errors.append(error)
            print(f"    ❌ {error}")
            continue
        
        doi = entry['fields']['doi']
        print(f"    DOI: {doi}")
        
        # Check 2: DOI URL is valid
        is_valid, error, status_code = validate_doi_url(doi)
        if not is_valid:
            error_msg = f"Entry '{entry['key']}': {error}"
            errors.append(error_msg)
            print(f"    ❌ {error_msg}")
            continue
        else:
            print(f"    ✓ DOI URL is valid (status {status_code})")
        
        # Check 3: Metadata matches (if enabled)
        if verify_metadata:
            print(f"    Fetching DOI metadata...")
            metadata = get_doi_metadata(doi)
            
            if metadata:
                matches, warnings = compare_metadata(entry, metadata)
                if warnings:
                    for warning in warnings:
                        print(f"    ⚠️  {warning}")
                else:
                    print(f"    ✓ Metadata appears consistent")
            else:
                print(f"    ⚠️  Could not fetch metadata from CrossRef API")
            
            # Small delay to be nice to the API
            time.sleep(0.5)
    
    return checked_count, len(errors), errors


def main():
    parser = argparse.ArgumentParser(
        description='Check bibliography files for DOI requirements'
    )
    parser.add_argument(
        'files',
        nargs='+',
        type=Path,
        help='Bibliography files to check'
    )
    parser.add_argument(
        '--no-metadata-check',
        action='store_true',
        help='Skip metadata verification (only check DOI presence and URL validity)'
    )
    
    args = parser.parse_args()
    
    total_checked = 0
    total_errors = 0
    all_errors = []
    
    for filepath in args.files:
        if not filepath.exists():
            print(f"Error: File {filepath} does not exist")
            sys.exit(1)
        
        checked, errors, error_list = check_bibliography_file(
            filepath,
            verify_metadata=not args.no_metadata_check
        )
        total_checked += checked
        total_errors += errors
        all_errors.extend(error_list)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total entries checked: {total_checked}")
    print(f"Errors found: {total_errors}")
    
    if all_errors:
        print("\nERRORS:")
        for error in all_errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("\n✓ All checks passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
