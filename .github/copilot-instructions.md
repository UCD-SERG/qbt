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

## Code Chunks

### Code Folding

Use `code-fold: true` for code chunks where the output is what's important to the narrative and not the code used to produce it. This allows readers to focus on the results while still having the option to view the code if they want to.

**When to use `code-fold: true`:**

- Visualization code where the plot/figure is the main point
- Data preparation or cleaning code that produces a summary table
- Long or complex code that would distract from the narrative
- Code that generates output (plots, tables, results) that readers need to see

**When NOT to use `code-fold: true`:**

- Tutorial code where readers need to learn the syntax
- Short, simple examples that are part of the explanation
- Code that is the main focus of the section
- When the console output is part of the main content (unformatted tables, model summaries, etc.)

**Example:**

````markdown
```{{r}}
#| code-fold: true
#| fig-cap: "Relationship between weight and miles per gallon"

library(ggplot2)
ggplot(mtcars, aes(x = wt, y = mpg)) +
  geom_point() +
  geom_smooth(method = "lm") +
  theme_minimal() +
  labs(x = "Weight (1000 lbs)", y = "Miles per Gallon")
```
````
