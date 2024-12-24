# Exporters

The exporters module in LabPaper provides the core functionality for converting Jupyter notebooks into various academic paper formats. Currently, it focuses on the Springer Nature format with plans for additional formats in the future.

## Available Exporters

### SpringerNaturePDF

The primary exporter that converts notebooks into Nature journal format PDF documents.

~~~python
jupyter nbconvert --to nature your_notebook.ipynb
~~~

## Configuration

Exporters can be configured through notebook metadata or command-line arguments:

~~~python
{
  "labpaper": {
    "title": "Your Paper Title",
    "authors": [
      "First Author",
      "Second Author"
    ],
    "affiliations": [
      "University One",
      "University Two"
    ]
  }
}
~~~

## Extension Points

Exporters can be extended or customized by:
- Creating new template files
- Adding custom preprocessors
- Implementing custom filters

For custom implementations, inherit from the base exporter classes in the package. 