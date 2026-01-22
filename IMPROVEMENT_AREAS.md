# Potential Areas for Improvement

This document identifies potential areas for improvement in the qbt (Quarto Book Template) repository based on a comprehensive code analysis.

## 1. Code Quality & Error Handling

### Python Scripts - Exception Handling

**File**: `.github/scripts/create-docx-tracked-changes.py` (line 169)
- **Issue**: Bare `except:` clause without exception type
- **Problem**: Catches all exceptions including `KeyboardInterrupt` and `SystemExit`, masking critical errors
- **Recommendation**: Change to `except Exception as e:` and add proper error logging

**File**: `.github/scripts/detect-changed-chapters.py` (line 84)
- **Issue**: Generic `except Exception:` without logging
- **Problem**: Silent failures when file operations fail
- **Recommendation**: Add logging to help troubleshoot failures

**File**: `.github/scripts/highlight-html-changes.py` (lines 462-508)
- **Issue**: Multiple subprocess calls with `check=False` without checking return codes
- **Problem**: Git command failures are silently ignored
- **Recommendation**: Check `result.returncode` or add proper error logging

## 2. Hardcoded Configuration Values

**File**: `.github/scripts/add-home-banner.py` (line 50)
- **Issue**: Hardcoded DOCX filename `"UCD-SeRG-Lab-Manual-tracked-changes.docx"`
- **Problem**: Not template-agnostic; requires modification for each book
- **Recommendation**: Extract to environment variable or configuration file

**File**: `.github/scripts/add-home-banner.py` (line 105)
- **Issue**: Banner injected into ALL HTML files
- **Problem**: Clutters every chapter with changes indicator
- **Recommendation**: Only inject into `index.html` or make conditional

**File**: `.github/scripts/create-docx-tracked-changes.py` (lines 108, 127, 191)
- **Issue**: Hardcoded author name `'PR Preview'` and dates `'2024-01-01'`
- **Problem**: Unrealistic metadata for tracking changes
- **Recommendation**: Use actual PR date and contributor info from GitHub Actions

## 3. Documentation Gaps

### Missing Python Documentation
- **Files**: All `.github/scripts/*.py` files
- **Issue**: No docstrings or type hints
- **Problem**: Difficult for contributors to understand function signatures
- **Recommendation**: Add comprehensive docstrings with parameter and return types

### Missing Scripts README
- **Location**: `.github/scripts/` directory
- **Issue**: No README explaining what each script does
- **Problem**: Contributors can't understand or run scripts independently
- **Recommendation**: Create `.github/scripts/README.md` with usage examples

### Missing Troubleshooting Guide
- **File**: `CONTRIBUTING.md`
- **Issue**: No error handling documentation
- **Problem**: Contributors don't know how to troubleshoot workflow failures
- **Recommendation**: Add troubleshooting section

## 4. Potential Bugs and Logic Issues

**File**: `.github/scripts/detect-changed-chapters.py` (lines 117-140)
- **Issue**: Nested path lookups could match wrong files
- **Problem**: Unreliable when directory structure varies
- **Recommendation**: Standardize path handling with explicit glob patterns

**File**: `.github/scripts/highlight-html-changes.py` (lines 273-277)
- **Issue**: Uses regex for HTML manipulation with `count=1`
- **Problem**: Wrong element could be replaced if HTML content repeats
- **Recommendation**: Use HTML parser instead of regex

**File**: `.github/scripts/create-docx-tracked-changes.py` (lines 86-87)
- **Issue**: Compares only paragraph text, not formatting or tables
- **Problem**: Many document changes won't show as tracked
- **Recommendation**: Compare XML representation or use proper DOCX diffing tool

**File**: `.github/scripts/check-bibliography-dois.R` (lines 119-124)
- **Issue**: Bare scoping assignment `<<-` in error handler
- **Problem**: Fragile; could cause issues if structure changes
- **Recommendation**: Use proper return mechanisms

## 5. Security & Robustness Issues

**File**: `.github/scripts/highlight-html-changes.py` (line 14)
- **Issue**: HTML unescape without sanitization
- **Problem**: Could be exploited with malicious content
- **Recommendation**: Add HTML sanitization layer

**File**: `.github/scripts/detect-changed-chapters.py` (lines 29-48)
- **Issue**: Subprocess calls without timeout
- **Problem**: Could hang indefinitely on network issues
- **Recommendation**: Add timeout parameter (e.g., `timeout=30`)

**File**: `.github/scripts/create-docx-tracked-changes.py` (lines 156-170)
- **Issue**: Fallback to copy file without validation
- **Problem**: Could silently deploy corrupted DOCX
- **Recommendation**: Add validation before returning success

## 6. Testing Gaps

### Missing Unit Tests
- **Issue**: No unit tests for any Python scripts
- **Problem**: Regressions undetected; hard to refactor safely
- **Recommendation**: Create `tests/` directory with pytest tests for:
  - File change detection logic
  - HTML highlighting functions
  - DOCX comparison
  - JSON output generation

### Missing Integration Tests
- **Issue**: No integration tests for workflow execution
- **Problem**: Can't verify workflows work end-to-end
- **Recommendation**: Add workflow test action or manual test documentation

### Missing Test Fixtures
- **Issue**: No test data/fixtures
- **Problem**: Can't test with realistic sample documents
- **Recommendation**: Create test fixtures with sample .qmd, HTML, DOCX files

## 7. Workflow & Process Issues

**File**: `.github/workflows/preview.yml` (lines 54-62)
- **Issue**: Prints raw environment variables in logs
- **Problem**: Could expose sensitive data in public logs
- **Recommendation**: Remove debug output or use `::notice` instead

**File**: `.github/workflows/check-bibliography-dois.yml` (line 45)
- **Issue**: No timeout for R script with API calls
- **Problem**: Could hang indefinitely waiting for CrossRef API
- **Recommendation**: Add timeout to Rscript invocation

**File**: `.github/workflows/lint-project.yaml`
- **Issue**: Workflow name doesn't match filename
- **Problem**: Confusing for navigation and CI/CD tracking
- **Recommendation**: Use consistent naming

## 8. Code Maintainability & Refactoring

### Repeated Git Operations
- **Files**: `detect-changed-chapters.py`, `create-docx-tracked-changes.py`, `highlight-html-changes.py`
- **Issue**: Duplicate code for `git fetch`, `git ls-tree`, `git show`
- **Recommendation**: Create shared utility module `.github/scripts/git_utils.py`

### Repeated Path Handling
- **Files**: Multiple scripts use `Path().glob()` and `os.getenv()`
- **Recommendation**: Create `.github/scripts/config.py` for centralized configuration

### HTML Parsing Complexity
- **File**: `highlight-html-changes.py` (200+ lines of regex-based parsing)
- **Issue**: Fragile and hard to maintain
- **Recommendation**: Replace with proper HTML parsing using `html.parser.HTMLParser` or `lxml`

## 9. Configuration & Usability Issues

**File**: `_quarto.yml` (line 6)
- **Issue**: Placeholder values like `"Your Book Title"`, `"Your Name"`
- **Problem**: Users forget to customize
- **Recommendation**: Add validation script or warning when placeholders detected

**File**: `lychee.toml` (lines 20-28)
- **Issue**: URL patterns use exact placeholders; incomplete regex
- **Problem**: URL checker may incorrectly validate URLs
- **Recommendation**: Improve regex patterns

**File**: `DESCRIPTION` (lines 6-7)
- **Issue**: Placeholder values for author/email
- **Problem**: Not valid R package metadata
- **Recommendation**: Add initialization script that prompts for values

## 10. Accessibility & Documentation

**File**: `styles.css`
- **Issue**: No CSS contrast validation for dark mode
- **Problem**: May not be accessible to users with visual impairments
- **Recommendation**: Document minimum contrast requirements; test with accessibility tools

**File**: `.github/copilot-instructions.md`
- **Issue**: May contain outdated instructions
- **Recommendation**: Review and update for current best practices

## 11. Dependency & Version Management

### Missing Python Requirements File
- **Files**: `.github/scripts/*.py` use external libraries
- **Issue**: No `requirements.txt`
- **Problem**: Cannot reproduce environment
- **Recommendation**: Create `.github/scripts/requirements.txt` with version pins

### Missing R Version Specification
- **File**: `check-bibliography-dois.R`
- **Issue**: Uses modern R syntax without version check
- **Problem**: Could fail on older R versions
- **Recommendation**: Add R version check at script start

## 12. Other Notable Issues

- **File**: `.github/workflows/summary.yml` - Uses experimental `actions/ai-inference` which may not be stable
- **File**: `README.md` - Very long; should be split into separate documentation files
- **File**: `.lintr.R` - Complex regex patterns not well-documented

## Priority Summary

| Priority | Category | Impact |
|----------|----------|--------|
| **High** | Error Handling | Bare except clauses mask critical errors |
| **High** | Configuration | Hardcoded values prevent template reuse |
| **High** | Security | Missing timeouts could cause hangs |
| **Medium** | Testing | Zero test coverage prevents safe refactoring |
| **Medium** | Documentation | Missing docstrings/type hints reduce maintainability |
| **Medium** | Maintainability | Code duplication increases maintenance burden |
| **Low** | Usability | Placeholder values could confuse users |
| **Low** | Process | Inconsistent naming/organization |
