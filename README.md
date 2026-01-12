# Quarto Book Template

A template repository for creating books with [Quarto](https://quarto.org/). This template is based on the [UCD-SERG/lab-manual](https://github.com/UCD-SERG/lab-manual) structure and provides everything you need to quickly start writing your own book.

## Features

- 📚 **Book-ready structure** with sample chapters and references
- 🎨 **Customizable themes** supporting light and dark modes
- 🚀 **Automatic deployment** to GitHub Pages via GitHub Actions
- 🔗 **Automated link checking** to ensure all URLs are reachable
- 📄 **Multiple output formats** including HTML, PDF, EPUB, and DOCX
- 📑 **Bibliography support** with BibTeX integration
- 🔢 **Automatic numbering** of sections and cross-references
- 💅 **Custom CSS** for styling your book

## Quick Start

### Using this template

1. Click the "Use this template" button at the top of this repository
2. Name your new repository and create it
3. Clone your new repository to your local machine

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

### Prerequisites

You need to have [Quarto](https://quarto.org/) installed. Download it from [quarto.org/docs/get-started](https://quarto.org/docs/get-started/).

To verify Quarto is installed:

```bash
quarto --version
```

### Customize your book

1. **Edit `_quarto.yml`** to update:
   - Book title and author
   - Repository URL
   - Chapter list
   - Theme and styling options

2. **Modify `index.qmd`** to create your book's homepage/introduction

3. **Edit or create chapters** (`.qmd` files):
   - Modify `chapter1.qmd` and `chapter2.qmd` as needed
   - Create new chapters and add them to the `chapters` list in `_quarto.yml`

4. **Add references** to `references.bib` in BibTeX format

5. **Customize styling** in `styles.css`

## Building the book

### Local preview

To preview your book with live reload during development:

```bash
quarto preview
```

This will open your book in a web browser and automatically refresh when you make changes.

### Render the book

To render the complete book:

```bash
quarto render
```

The output will be generated in the `docs/` directory.

## Publishing to GitHub Pages

This template includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically builds and publishes your book to GitHub Pages when you push to the main branch.

### Setup steps:

1. **Enable GitHub Pages** in your repository:
   - Go to Settings → Pages
   - Under "Build and deployment", set Source to "GitHub Actions"

2. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Initial book setup"
   git push origin main
   ```

3. **Wait for the workflow** to complete (check the Actions tab)

4. **Access your book** at: `https://YOUR-USERNAME.github.io/YOUR-REPO/`

## Project Structure

```
.
├── _quarto.yml              # Main configuration file
├── index.qmd                # Book homepage/introduction
├── chapter1.qmd             # Sample chapter 1
├── chapter2.qmd             # Sample chapter 2
├── references.qmd           # References page
├── references.bib           # BibTeX bibliography
├── styles.css               # Custom CSS styles
├── lychee.toml              # Link checker configuration
├── .gitignore              # Git ignore file
├── LICENSE                  # CC0 1.0 Universal License
├── README.md               # This file
└── .github/
    └── workflows/
        ├── publish.yml      # GitHub Pages deployment workflow
        └── check-links.yml  # URL reachability checker workflow
```

## Automated Workflows

This template includes two GitHub Actions workflows:

### Publishing Workflow (`publish.yml`)
Automatically builds and deploys your book to GitHub Pages when you push to the main branch.

### Link Checker Workflow (`check-links.yml`)
Automatically checks that all URLs in your book are reachable:
- **Runs on**: Push to main, pull requests, weekly schedule (Mondays at 9:00 UTC), and manual trigger
- **Checks**: All links in `.qmd`, `.md`, and `.html` files
- **Reports**: Workflow fails if broken links are detected. Check the workflow logs for details on which links are broken.
- **Configuration**: Customize behavior in `lychee.toml`

To manually trigger the link checker:
1. Go to the Actions tab in your repository
2. Select "Check Links" workflow
3. Click "Run workflow"

## Writing Content

Quarto uses markdown with extensions. Here are some quick tips:

### Headings

```markdown
# Chapter Title
## Section
### Subsection
```

### Code blocks

````markdown
```python
print("Hello, World!")
```
````

### Math equations

```markdown
Inline: $E = mc^2$

Display:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

### Citations

Reference a citation: `@citationkey`

### Cross-references

Reference figures, tables, and sections using labels:

```markdown
See @fig-example for details.
```

For more details, see the [Quarto documentation](https://quarto.org/docs/guide/).

## Customization

### Changing themes

Edit the `format.html.theme` section in `_quarto.yml`:

```yaml
format:
  html:
    theme:
      light: cosmo  # Try: cosmo, flatly, litera, minty, etc.
      dark: darkly  # Try: darkly, cyborg, slate, superhero, etc.
```

### Adding chapters

1. Create a new `.qmd` file (e.g., `chapter3.qmd`)
2. Add it to the `chapters` list in `_quarto.yml`:

```yaml
book:
  chapters:
    - index.qmd
    - chapter1.qmd
    - chapter2.qmd
    - chapter3.qmd  # Your new chapter
    - references.qmd
```

### Custom CSS

Add your custom styles to `styles.css`. These will override the default theme styles.

## License

This template is released under the [CC0 1.0 Universal License](LICENSE), which means you can freely use, modify, and distribute it without any restrictions.

## Acknowledgments

This template is based on the structure of the [UCD-SERG Lab Manual](https://github.com/UCD-SERG/lab-manual), which was adapted from the [Benjamin-Chung Lab Manual](https://jadebc.github.io/lab-manual/index.html).

## Support

- [Quarto Documentation](https://quarto.org/docs/guide/)
- [Quarto Community](https://github.com/quarto-dev/quarto-cli/discussions)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- https://www.newytimes.com/asdfoijwf (demo link to test)

## Contributing

Feel free to open issues or submit pull requests to improve this template!
