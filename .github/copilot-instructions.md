# GitHub Copilot Instructions

This file provides custom instructions for GitHub Copilot when working in this repository.

## General Guidelines

Follow the guidance in the [UCD-SERG Lab Manual](https://ucd-serg.github.io/lab-manual/).

The source files for the lab manual are available at <https://github.com/UCD-SERG/lab-manual> if easier to read.

## Style Guidelines

### Lists

When describing lists of three or more items, use a bullet list instead of a comma-separated list. Use your stylistic judgment to determine when this rule applies.

**Examples:**

❌ **Don't** use comma-separated lists for three or more items:
```
The template includes GitHub Actions workflows for publishing, link checking, and spell checking.
```

✅ **Do** use bullet lists instead:
```
The template includes GitHub Actions workflows for:

- Publishing
- Link checking
- Spell checking
```

Always put a blank line before the start of a bullet-point list in markdown (`.md`) files and variants (especially Quarto `.qmd` files).

**When to use your judgment:**

- Short, simple items in a sentence may remain comma-separated if it maintains readability
- Complex items or items with descriptions should always use bullet lists
- Use bullet lists when the items are important and deserve emphasis
- Technical lists (commands, file names, features) typically benefit from bullet format
