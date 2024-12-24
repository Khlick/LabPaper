# LabPaper

A sophisticated Jupyter notebook exporter designed for creating academic papers in Tufte style. This package provides a seamless integration between Jupyter notebooks and professional academic paper formats.

## Features

- Export Jupyter notebooks to professional academic paper formats
- Tufte-style design principles
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
- [TeX Configuration](docs/texmf.md) - TeX/LaTeX setup and configuration

## Requirements

- Python ≥ 3.11
- Jupyter ≥ 7.0.0
- nbconvert ≥ 7.16.0
- pandoc >= 3.6
- A LaTeX distribution (e.g., TeX Live, MiKTeX)
- Other dependencies are handled automatically during installation

## Development

1. Clone the repository
2. Create a virtual environment
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the BSD License - see the [LICENSE](LICENSE) file for details.