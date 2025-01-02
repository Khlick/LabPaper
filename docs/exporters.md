# Exporters

The exporters module in LabPaper provides the core functionality for converting Jupyter notebooks into various academic paper formats. Currently, it focuses on the Springer Nature format with plans for additional formats in the future.

## Available Exporters

### SpringerNaturePDF

The primary exporter that converts notebooks into Nature journal format PDF documents. 
To see an example of the class in action, see [this overleaf project](https://www.overleaf.com/latex/templates/springer-nature-latex-template/myxmhdsbzkyd). 
LabPaper is synchronized with the December 2023 version of the template.

```python
jupyter nbconvert --to nature your_notebook.ipynb
```

#### Configuration Options

The SpringerNaturePDF exporter supports the following configuration options which may be set in a configuration file (see [nbconvert docs](https://nbconvert.readthedocs.io/en/latest/config_options.html)) or passed as command-line arguments (with `--SpringerNaturePDF.option=value`):

- `execute_notebook` (bool, default: True)
  - Whether to execute the notebook before processing
  
- `bibliography_style` (str, default: 'sn-nature')
  - BibTeX style to use for citations
  - Must be a valid style from the texmf/bibtex/bst directory
  
- `separate_fig_and_tab_page` (bool, default: False)
  - Whether to separate figures and tables onto separate pages using the endfloat package
  
- `referee` (bool, default: False)
  - Whether to use the referee option for the document class
  
- `line_numbers` (bool, default: False)
  - Whether to show line numbers in code blocks
  
- `no_bib` (bool, default: False)
  - Whether to suppress the bibliography

#### Cell Tags

The following cell tags can be used to control cell behavior and formatting:

Figure-related:
- `figure`, `plot`: Mark cell as containing a figure
- `table`, `tabular`: Mark cell as containing a table
- `stable`, `sideways`, `sidewaystable`: Mark cell as containing a sideways table

Code-related:
- `code`, `listing`: Mark cell as a code listing
- `hide`, `hidden`, `no-display`: Hide cell from output
- `show`, `display`, `visible`, `echo`: Show cell in output (overrides hide)

#### Front Matter Syntax

The first cell of the notebook should be a markdown cell containing the front matter in the following format:

```markdown
# Title of Your Paper

Authors:
1. First Author e: first.author@email.com
   1. Department1, Organization1, Address1
   2. Department2, Organization2, Address2
2. Second Author e: second.author@email.com
   1. Department3, Organization3, Address3

Abstract:
Your abstract text goes here. The abstract should be a single paragraph that summarizes
your work. It can span multiple lines.

The abstract can include multiple paragraphs, e.g., a structured abstract with multiple sections.

Keywords: keyword1, keyword2, keyword3
```

Front Matter Elements:
- Title: First-level heading (`#`)
- Authors: Numbered list with `*` for corresponding author. Use `!` to indicate authors with equal contributions
- Author Affiliations: Nested numbered list under each author
- Abstract: Section starting with "Abstract:" followed by text (LaTeX & Markdown supported)
- Keywords: Comma-separated list after "Keywords:"

#### Metadata Blocks

For figures, tables, and code blocks, you can add metadata blocks in the cell's source:

```python
# @label: fig:example
# @caption: This is a figure caption
# @width: 0.8
# Your code here...
```

Available metadata fields:
- `label`: Reference label (auto-generated if not provided)
- `caption`: Caption text
- `width`: Width as fraction of text width (figures only)
- `height`: Height specification (figures only)

## Extension Points

Exporters can be extended or customized by:
- Creating new template files
- Adding custom preprocessors
- Implementing custom filters

For custom PDF generation implementations, inherit from the base exporter classes in the package.