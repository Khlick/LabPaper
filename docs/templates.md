# Templates

Templates in LabPaper define the structure and appearance of the exported documents. They use Jinja2 templating engine and can incorporate LaTeX for PDF output.

## Available Templates

### Nature Template

The default template for Nature journal format:

~~~python
jupyter nbconvert --to nature --template naturePDF notebook.ipynb
~~~

## Template Structure

Templates are organized as follows:

~~~
templates/
├── base/
│   ├── document_class.tex.j2
│   └── base.tex.j2
└── nature/
    ├── article.tex.j2
    └── style.tex.j2
~~~

## Customization

### Template Inheritance

Create custom templates by extending existing ones:

~~~latex
((*- extends "base.tex.j2" -*))

((*- block title -*))
\title{Custom Title Format}
((*- endblock title -*))
~~~

### Template Variables

Templates can access various metadata and content:

~~~jinja
Title: {{ resources.metadata.name }}
Authors: {{ resources.metadata.authors | join(', ') }}
Date: {{ resources.metadata.date }}
~~~

## Creating New Templates

1. Create a new template directory
2. Add required template files
3. Register the template with nbconvert
4. Use appropriate Jinja2 syntax for variable substitution 