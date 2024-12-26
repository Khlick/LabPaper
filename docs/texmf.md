# TeX Configuration

The `texmf` directory contains extra resources required by LabPaper.

## Structure

The texmf directory is organized as follows:

```
texmf/
├── bibtex/
│   └── bst/
│       └── ...
└── tex/
    └── latex/
        └── .../
```

## Custom LaTeX Classes

For any LaTeX package or class, you may add it to the `texmf/tex/latex/<class>/` directory and include them in your custom exporter or template. Currently, the Springer Nature LaTeX class is supported, along with the Springer Nature BibTex style files (`texmf/bibtex/bst/`).
