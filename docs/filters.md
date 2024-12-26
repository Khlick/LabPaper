# Filters

LabPaper provides several custom filters that can be used with nbconvert to modify text during the conversion process. These filters are automatically available when using any of the LabPaper exporters.

## Available Filters

### newline_block

Ensures that a block of text always starts with a newline. This is particularly useful for LaTeX output where you want to ensure proper spacing between blocks of content.

```python
from labpaper.filters import newline_block

# Input
text = "Some text"

# Output
"""

Some text

"""
```

### latex_internal_references

Converts markdown-style internal references to LaTeX autoref commands. This allows you to use markdown-style links for cross-references in your notebook that will be properly converted to LaTeX references.

```python
from labpaper.filters import latex_internal_references

# Input
text = "See [Figure 1](#fig:example) for details"

# Output
"See \autoref{fig:example} for details"
```

### comment_lines

Adds a comment character and space to the beginning of every line in the text. This is useful for converting text blocks into comments in the output format.

```python
from labpaper.filters import comment_lines

# Input
text = "Line 1\nLine 2"

# Output with default comment char '%'
"% Line 1\n% Line 2"

# Can specify different comment char
comment_lines(text, comment_char="#")
"# Line 1\n# Line 2"
```

## Using Filters

These filters are automatically available in LabPaper templates. If you're creating custom templates, you can access these filters through the template environment:

```jinja
{{ cell.source | newline_block }}
{{ cell.source | latex_internal_references }}
{{ cell.source | comment_lines }} 