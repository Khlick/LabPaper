# TeX Configuration

The `texmf` module in LabPaper manages TeX/LaTeX configurations and resources required for PDF generation.

## Structure

The TeX configuration files are organized as follows:

~~~
texmf/
├── tex/
│   └── latex/
│       └── labpaper/
│           ├── nature.cls
│           └── common.sty
└── fonts/
    └── opentype/
~~~

## Required Packages

Essential LaTeX packages for proper functioning:

~~~latex
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{natbib}
~~~

## Font Configuration

LabPaper uses specific fonts for professional typesetting:

~~~latex
\usepackage{fontspec}
\setmainfont{TeX Gyre Termes}
\setsansfont{TeX Gyre Heros}
\setmonofont{TeX Gyre Cursor}
~~~

## Custom Styles

You can add custom style files to extend the default configuration:

1. Create a new `.sty` file
2. Place it in the `texmf/tex/latex/labpaper/` directory
3. Reference it in your template:

~~~latex
\usepackage{custom_style}
~~~

## Installation

The TeX resources are automatically installed with the package. For manual installation:

~~~bash
# Copy files to your local texmf tree
cp -r texmf/* ~/texmf/
# Update TeX database
texhash ~/texmf
~~~ 