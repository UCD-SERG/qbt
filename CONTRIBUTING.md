# Contributing to Your Quarto Book

Thank you for your interest in contributing to this book!

## How to contribute

### For book authors

If you're working on content for this book:

1. **Create a new branch** for your work:
   ```bash
   git checkout -b chapter/your-topic
   ```

2. **Edit or create `.qmd` files** for your chapter

3. **Preview your changes** locally:
   ```bash
   quarto preview
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add chapter on your topic"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin chapter/your-topic
   ```

### Content guidelines

- Use clear, concise language
- Include code examples where appropriate
- Add references to `references.bib` for any citations
- Use appropriate headings (h2 `##` for main sections, h3 `###` for subsections)
- Include images in an `images/` or `figures/` directory
- Test code examples to ensure they work

### Markdown formatting

- Use **bold** for emphasis on terms
- Use `code` formatting for inline code, file names, and commands
- Use code blocks with language specification for longer code examples
- Use callout boxes for important information:
  ```markdown
  ::: {.callout-note}
  Important information here
  :::
  ```

### Adding images

1. Place images in the `images/` directory
2. Reference them in your `.qmd` file:
   ```markdown
   ![Caption text](images/your-image.png){#fig-label}
   ```

### Adding URLs

When adding external links to your content, please ensure:

1. **URLs are valid and reachable** - The repository has an automated link checker that runs weekly and on every push/pull request
2. **Use HTTPS when possible** - Prefer secure URLs over HTTP
3. **Check link stability** - Use permanent links (permalinks) when available rather than URLs that might change

The link checker workflow will automatically:

- Check all URLs in `.qmd`, `.md`, and `.html` files
- Report broken or unreachable links
- Create issues for broken links that need attention

If you need to exclude certain URLs from checking (e.g., example URLs), add them to the `lychee.toml` configuration file.

#### Manual override for link checking

If you have manually verified all links in your pull request and want to skip the automated link checker, you can add the **`links checked by hand`** label to your PR. This will cause the link checker workflow to skip the check for that specific pull request, while still running on the main branch and scheduled checks.

### Citations

Add BibTeX entries to `references.bib`:

```bibtex
@article{authorYEAR,
  title={Article Title},
  author={Author, First and Author, Second},
  journal={Journal Name},
  year={2024}
}
```

Then cite in text: `@authorYEAR`

## Questions?

If you have questions about contributing, please open an issue in the repository.
