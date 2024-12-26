# Templates

Templates in LabPaper define the structure and appearance of the exported documents. They use the Jinja2 templating engine and can incorporate LaTeX for PDF output. Each template is designed to meet specific publication requirements.

## Template Organization

Templates should be organized in their own namesake directories under `labpaper/templates/`. Each template directory must contain:

- `conf.json`: Configuration file as specified by nbconvert 7.16
- Template files with `.j2` extension using appropriate Jinja2 syntax
- Any additional resources needed by the template

Example structure:
```
labpaper/templates/
└── nature/
    ├── conf.json
    ├── base.tex.j2
    ├── index.tex.j2
    ├── contents.tex.j2
    └── display.tex.j2
```

## Available Templates

### Nature Template

The Nature template is designed to work with Springer Nature's `sn-jnl` LaTeX class, producing PDF documents that conform to Nature journal specifications. The template is synchronized with the December 2023 version of the official Springer Nature LaTeX template.

#### Template Files
- `base.tex.j2`: Base LaTeX structure and common definitions
- `index.tex.j2`: Main document structure and front matter
- `contents.tex.j2`: Content processing (figures, tables, code blocks)
- `display.tex.j2`: Display elements formatting

#### Features
- Full support for Nature journal formatting requirements
- Front matter handling (title, authors, affiliations, abstract)
- Figure and table processing with proper numbering and referencing
- Code block syntax highlighting using Pygments
- Bibliography management with BibTeX
- Support for equations, cross-references, and citations
- Line numbering for referee mode
- Double spacing option for manuscript submission

#### Usage
```python
jupyter nbconvert --to nature notebook.ipynb
```

Configuration options can be set in the notebook metadata or via command line:
```python
jupyter nbconvert --to nature --NatureExporter.referee=True notebook.ipynb
```

## Creating Custom Templates

To create a custom template:

1. Create a new directory under `labpaper/templates/`:
```
labpaper/templates/custom_template/
├── conf.json
├── base.tex.j2
└── index.tex.j2
```

2. Create the `conf.json` configuration:
```json
{
    "base_template": "base",
    "mimetypes": {
        "text/latex": true
    },
    "preprocessors": {
        "pygments": {"enabled": true}
    }
}
```

3. Create template files using appropriate Jinja2 syntax:
```latex
((*- extends 'base.tex.j2' -*))

((*- block title -*))
\title{ {{- resources.metadata.name -}} }
((*- endblock title -*))
```

### Template Development Guidelines

1. **Use Appropriate Syntax**:
   - For LaTeX output, use `((*- ... -*))` for Jinja2 blocks
   - Use `{{- ... -}}` for variable interpolation
   - Escape LaTeX special characters appropriately

2. **Template Inheritance**:
   - Extend base templates when possible
   - Override only the blocks you need to modify
   - Keep common elements in base templates

3. **Resource Management**:
   - Include necessary LaTeX class files and packages
   - Handle dependencies appropriately
   - Document any external requirements

4. **Testing**:
   - Test with various input types (text, code, math, figures)
   - Verify PDF generation with different LaTeX engines
   - Check compatibility with different operating systems

### Template Variables

Templates have access to various metadata and content:

```jinja
((*- block title -*))
Title: {{ resources.metadata.name }}
Authors: {{ resources.metadata.authors | join(', ') }}
Date: {{ resources.metadata.date }}
((*- endblock title -*))
```

### Template Filters

Custom filters can be used to transform content:

```jinja
{{ cell.source | wrap_text(80) }}
{{ cell.outputs | format_output }}
```

## Extension Points

Templates can be extended or customized by:
- Creating new template files
- Adding custom filters
- Implementing custom preprocessors
- Modifying the base template structure 