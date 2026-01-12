# Images Directory

Place your images and figures in this directory.

## Naming conventions

Use descriptive names for your images:
- `chapter1-workflow-diagram.png`
- `results-plot-2024.png`
- `methodology-flowchart.svg`

## Supported formats

Quarto supports various image formats:
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- SVG (`.svg`)
- GIF (`.gif`)
- PDF (`.pdf`) - for LaTeX/PDF output

## Referencing images

In your `.qmd` files, reference images like this:

```markdown
![Caption describing the image](images/your-image.png){#fig-label}
```

Then you can cross-reference it in text:

```markdown
As shown in @fig-label, ...
```
