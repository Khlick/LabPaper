# LabPaper

A sophisticated Jupyter notebook exporter designed for creating academic papers. This package provides a seamless integration between Jupyter notebooks and professional academic paper formats.

## Features

- Export Jupyter notebooks to professional academic paper formats
- Support for Nature journal format
- Customizable templates and exporters
- Advanced preprocessing capabilities
- Flexible filtering system

## Installation

```bash
pip install labpaper
```

## Quick Start

Basic usage example:

```python
jupyter nbconvert --to nature your_notebook.ipynb
```

## Documentation

- [Exporters](docs/exporters.md) - Document conversion and output generation
- [Filters](docs/filters.md) - Content transformation and processing
- [Preprocessors](docs/preprocessors.md) - Pre-conversion notebook manipulation
- [Templates](docs/templates.md) - Document layout and styling
- [Embedded Resources](docs/texmf.md) - Any additional resources required by your exporter or template

## Requirements

- [Python](https://www.python.org/downloads/) ≥ 3.11
- [Jupyter](https://jupyter.org/install) ≥ 7.0.0
- nbconvert ≥ 7.16.0
- [pandoc](https://github.com/jgm/pandoc/releases) >= 3.6
- A LaTeX distribution (e.g., [MikTeX](https://miktex.org/download), [TeX Live](https://www.tug.org/texlive/), etc.)
- Other dependencies are handled automatically during installation

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/labpaper.git
   cd labpaper
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```
3. Install the package in development mode along with development dependencies:
   ```bash
   pip install -e .[dev]
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```
5. **Add New Exporters**:
   - Create a new Python file for your exporter in the `labpaper/exporters` directory.
   - Implement your exporter class by inheriting from the base exporter class provided by LabPaper.
   - Ensure your exporter handles the conversion logic specific to the desired output format.
   - Register your new exporter in the `pyproject.toml` file under the `[tool.labpaper.exporters]` section to make it available for use.

6. **Add New Filters**:
   - Create a new Python file for your filter in the `labpaper/filters` directory.
   - Implement your filter function or class, ensuring it processes the content as required.
   - Register your new filter in the `pyproject.toml` file under the `[tool.labpaper.filters]` section to integrate it into the conversion pipeline.

7. **Add New Preprocessors**:
   - Create a new Python file for your preprocessor in the `labpaper/preprocessors` directory.
   - Implement your preprocessor class by inheriting from `nbconvert.preprocessors.Preprocessor`.
   - Define the `preprocess` method to modify notebook content before conversion.
   - Register your new preprocessor in the `labpaper/preprocessors/__init__.py` file to include it in the available preprocessors list. Note that preprocessors will be refactored in a later release for better modularity.

8. **Create New Templates**:
   - Create a new subdirectory for your template in the `templates` directory.
   - Add the necessary Jinja2 template files (`.tex.j2`) to define the document structure and styling.
   - Include a `conf.json` file in your template subdirectory to specify template metadata and configuration options, following the nbconvert documentation.
   - Register your new template in the `pyproject.toml` file under the `[tool.labpaper.templates]` section to make it available for use.

9. **Place Resources in the Appropriate `texmf` Subdirectory**:
   - Organize any additional resources (e.g., `.bst` files, `.cls` files, custom style files) required for TeX/LaTeX compilation in the `texmf` directory.
   - Follow the existing directory structure within `texmf` to ensure resources are correctly located and accessible during the PDF generation process.
   - Update any relevant documentation or configuration files to reference the new resources as needed.

## Contributing

We welcome contributions to LabPaper! Here's how you can help:

- **Report Bugs**: If you find a bug, please [open an issue](https://github.com/Khlick/LabPaper/issues/new?template=bug_report.md)
- **Suggest Features**: Have an idea for a new feature? [Create a feature request](https://github.com/Khlick/LabPaper/issues/new)
- **Submit Pull Requests**: Want to contribute code? [Fork the repository](https://github.com/Khlick/LabPaper/fork) and submit a pull request

Please read our [Contributing Guidelines](.github/CONTRIBUTING.md) before submitting any contributions.

## License

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.