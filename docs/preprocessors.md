# Preprocessors

Preprocessors in LabPaper modify notebook content before the conversion process begins. They handle tasks like code execution, markdown processing, and content validation.

## Available Preprocessors

### PygmentizePreprocessor

Handles syntax highlighting for code blocks in the LaTeX output. This preprocessor generates the necessary Pygments definitions and styles for proper code formatting in the final PDF.

Configuration options:
- `style` (str, default: "abap"): Name of the pygments style to use for syntax highlighting

Example configuration:
```python
c.PygmentizePreprocessor.style = "monokai"
```

### PythonMarkdownPreprocessor

A powerful preprocessor that enables dynamic content generation in markdown cells and manages document metadata. It provides two main features:

Dynamic Markdown Content:

 - Evaluates Python expressions embedded in markdown cells using `{{ expression }}` syntax
 - Executes code cells to build up a namespace for expression evaluation
 - Provides access to matplotlib (plt) in the evaluation namespace

Example usage in markdown cells:

```markdown
The mean of our data is {{ data.mean() }}
The plot shows {{ len(figures) }} different conditions
```

Note: The preprocessor automatically closes matplotlib figures after execution to prevent display issues.

## Configuration

Preprocessors can be configured in your Jupyter configuration:

```python
c.LabPaperExporter.preprocessors = [
    'labpaper.preprocessors.PygmentizePreprocessor',
    'labpaper.preprocessors.PythonMarkdownPreprocessor'
]
```

## Custom Preprocessors

Create custom preprocessors by inheriting from `nbconvert.preprocessors.Preprocessor`:

```python
from nbconvert.preprocessors import Preprocessor

class CustomPreprocessor(Preprocessor):
    def preprocess_cell(self, cell, resources, index):
        # Your preprocessing logic here
        return cell, resources
```

## Execution Order

1. PythonMarkdownPreprocessor runs first to:
   - Set document metadata
   - Execute code cells to build namespace
   - Process markdown cells with embedded expressions

2. PygmentizePreprocessor runs next to:
   - Generate syntax highlighting definitions
   - Apply code styling for the LaTeX output 