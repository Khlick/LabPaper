# Filters

Filters in LabPaper are specialized functions that transform content during the export process. They provide fine-grained control over how different elements are rendered in the final document.

## Core Filters

The package includes several built-in filters for common transformations:

- Text formatting and styling
- Citation processing
- Figure and table handling
- Mathematical equation formatting
- Code block styling

## Usage in Templates

Filters can be used in templates using the Jinja2 pipe syntax:

~~~jinja
{{ cell.source | format_math }}
{{ metadata.authors | format_authors }}
~~~

## Custom Filters

You can create custom filters by:

1. Creating a new Python function
2. Registering it with the template engine
3. Using it in your templates

Example of a custom filter:

~~~python
def custom_format(text):
    # Your formatting logic here
    return formatted_text

c.LabPaperTemplate.filters = {
    'custom_format': custom_format
}
~~~ 