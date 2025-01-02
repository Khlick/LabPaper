"""Springer Nature PDF exporter."""
import os
import re
import copy
from traitlets import Unicode, List, Bool, default
from traitlets.config import Config
from nbformat.notebooknode import NotebookNode

from .base import LabPaperBaseExporter
from .utils.author import parse_authors_section
from .utils.code_parser import parse_metadata_content
from .utils.resolvers import resolve_boolean, resolve_string

# TODO: Add support for markdown images as figures

class SpringerNaturePDF(LabPaperBaseExporter):
    """Springer Nature PDF exporter that uses sn-jnl class."""
    
    _figure_count = 0
    _table_count = 0
    export_from_notebook = "Springer Nature PDF"
    output_mimetype = "application/pdf"
    
    # Metadata processing configuration
    process_metadata = Bool(
        True,
        help="Whether to process and transform cell metadata"
    ).tag(config=True)
    
    execute_notebook = Bool(
        True,
        help="Whether to execute the notebook before processing"
    ).tag(config=True)
    
    bibliography_style = Unicode(
        default_value='sn-nature',
        help="BibTeX style to use for citations"
    ).tag(config=True)
    
    latex_class = Unicode(
        default_value='sn-jnl',
        help="LaTeX class to use for the document"
    ).tag(config=True)
    
    latex_engine = Unicode(
        default_value='pdflatex',
        help="LaTeX engine to use (pdflatex recommended)",
    ).tag(config=True)
    
    latex_command = List(
        trait=Unicode(),
        default_value=["{filename}", "-shell-escape", "-interaction=nonstopmode"],
        help="Shell command used to compile latex."
    ).tag(config=True)

    bib_command = List(
        ["bibtex", "{filename}"],
        help="Shell command used to run bibtex."
    ).tag(config=True)
    
    figure_placement = Unicode(
        default_value='htbp',
        help="LaTeX placement for figures"
    ).tag(config=True)
    
    separate_fig_and_tab_page = Bool(
        default_value=False,
        help="Whether to separate figures and tables onto separate pages using the endfloat package"
    ).tag(config=True)
    
    referee = Bool(
        default_value=False,
        help="Whether to use the referee option for the document class"
    ).tag(config=True)
    
    line_numbers = Bool(
        default_value=False,
        help="Whether to show line numbers in the code blocks"
    ).tag(config=True)
    
    no_bib = Bool(
        default_value=False,
        help="Whether to suppress the bibliography"
    ).tag(config=True)
    
    @property
    def default_config(self):
        """Default configuration for LabPaper base exporter"""
        c = Config({
            'labpaper.preprocessors.PygmentizePreprocessor': {'enabled': True},
            'ExecutePreprocessor': {'enabled': self.execute_notebook,'metadata':{'path':"./"}}
        })
        if super().default_config:
            c2 = super().default_config.copy()
            c2.merge(c)
            c = c2
        return c
    
    @default('metadata_tags')
    def _metadata_tags(self):
        return {
            'figure': ['figure', 'plot'],
            'table': ['table', 'tabular'],
            'stable': ['stable','sideways', 'sidewaystable'],
            'equation': ['equation', 'math'],
            'code': ['code', 'listing'],
            'hide': ['hide', 'hidden', 'no-display'],
            'show': ['show', 'display', 'visible', 'echo'],
        }
    
    @default('extra_template_basedirs')
    def _extra_template_basedirs(self):
        """Return the paths to the templates."""
        return [
            os.path.abspath(
                os.path.join(
                    os.path.dirname(
                        os.path.dirname(__file__)
                        ), 
                    "templates"
                    )
                )
        ]
    
    @default("file_extension")
    def _file_extension_default(self):
        return ".tex"
    
    @default("template_name")
    def _template_name_default(self):
        """Default to the nature template"""
        return 'nature'

    @default('template_file')
    def _template_file_default(self):
        """Default to nature/index.tex.j2"""
        return 'index.tex.j2'
    
    def __init__(self, config=None, **kw):
        default_config = self.default_config
        if config:
            default_config.merge(config)
        
        config_traits = self._resolve_traits(default_config)
        super().__init__(config=config_traits, **kw)
   
    def _resolve_traits(self, config):
        """
        Resolve traitlets configurations.
        Property -> Configs conversions
        """
        # Resolve execute_notebook to a boolean
        config.ExecutePreprocessor.enabled = resolve_boolean(
            config.SpringerNaturePDF.execute_notebook,
            self.execute_notebook
            )
        # Resolve figure placement to a string
        self.figure_placement = resolve_string(
            config.SpringerNaturePDF.figure_placement,
            self.figure_placement
        )
        # Resolve separate_fig_and_tab_page to a boolean
        self.separate_fig_and_tab_page = resolve_boolean(
            config.SpringerNaturePDF.separate_fig_and_tab_page,
            self.separate_fig_and_tab_page
        )
        # Resolve referee to a boolean
        self.referee = resolve_boolean(
            config.SpringerNaturePDF.referee,
            self.referee
        )
        # Resolve line_numbers to a boolean
        self.line_numbers = resolve_boolean(
            config.SpringerNaturePDF.line_numbers,
            self.line_numbers
        )
        # Resolve bibliography_style to a string
        bibstyle = resolve_string(
            config.SpringerNaturePDF.bibliography_style,
            self.bibliography_style
        )
        # Resolve no_bib to a boolean
        self.no_bib = resolve_boolean(
            config.SpringerNaturePDF.no_bib,
            self.no_bib
        )
        # Dynamically parse .bst file names from texmf/bibtex/bst/ using self._get_texmf_path()
        texmf_bst_directory = os.path.join(self._get_texmf_path(), 'bibtex', 'bst')
        valid_bibstyles = []
        for root, _, files in os.walk(texmf_bst_directory):
            for file in files:
                if file.endswith('.bst'):
                    valid_bibstyles.append(os.path.splitext(file)[0])

        if bibstyle not in valid_bibstyles:
            self.log.warning(f"Invalid bibliography style '{bibstyle}', defaulting to 'sn-nature'")
            bibstyle = 'sn-nature'
        self.bibliography_style = bibstyle
        
        return config
    
    # Parent Overrides
    def process_cell_tags(self, tags):
        """Process cell tags according to Springer Nature mappings."""
        processed = {category: False for category in self._metadata_tags()}
        
        # Set hide to True by default
        processed['hide'] = True
        
        for tag in tags:
            # Process other tags
            for category, matches in self._metadata_tags().items():
                if tag in matches:
                    processed[category] = True
                    break
            
            # Check for show tags first
            if tag in self._metadata_tags()['show']:
                processed['hide'] = False
                continue
            
        
        return processed
        
    # Base methods for subclasses to implement, these tend to need super() calls
    def process_notebook_metadata(self, nb):
        """Process notebook-level metadata."""
        nb = super().process_notebook_metadata(nb)
        metadata = self._get_metadata_handle(nb) # labpaper
        
        # Check first cell for front matter
        if len(nb.cells) > 0 and nb.cells[0].cell_type == 'markdown':
            first_cell = nb.cells[0]
            
            # Look for title in first level header
            title_match = re.match(r'^#\s+(.+)$', first_cell.source, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
                self.log.info(f"Found title in first cell: {title}")
                metadata.title = title
                # Remove the title line from the cell source
                first_cell.source = re.sub(r'^#\s+.+\n?', '', first_cell.source, flags=re.MULTILINE)
            
            # Parse authors and affiliations
            authors, affiliations = parse_authors_section(first_cell.source)
            if authors:
                metadata.authors = [NotebookNode(author.__dict__) for author in authors]
                metadata.affiliations = [NotebookNode(affil.__dict__) for affil in affiliations]
                
            # Parse other metadata (abstract, keywords, date)
            abstract_match = re.search(
                r'^Abstract:\s*\n((?:.|\n)*?)(?=\n^(Keywords:|Date:)|\Z)',
                first_cell.source,
                re.MULTILINE
            )
            if abstract_match:
                metadata.abstract = abstract_match.group(1).strip()
                
            keywords_match = re.search(
                r'^Keywords:\s*(.+?)(?:\n\n|$)',
                first_cell.source,
                re.MULTILINE
            )
            if keywords_match:
                metadata.keywords = [k.strip() for k in keywords_match.group(1).split(',')]
                
            date_match = re.search(
                r'^Date:\s*(.+?)(?:\n\n|$)',
                first_cell.source,
                re.MULTILINE
            )
            if date_match:
                metadata.date = date_match.group(1).strip()
            # Remove the first cell contents after parsing
            first_cell.source = ''

        # Process remaining front matter
        front_matter = nb.metadata.get('front_matter', {})
        metadata.update({
            'title': metadata.get('title', front_matter.get('title', '')),
            'author': (f"{metadata.authors[0].given_name} {metadata.authors[0].surname}" 
                      if metadata.get('authors') else front_matter.get('author', '')),
            'date': metadata.get('date', front_matter.get('date', '\\today')),
            'abstract': metadata.get('abstract', front_matter.get('abstract', '')),
            'keywords': metadata.get('keywords', front_matter.get('keywords', '')),
            'document_class': 'sn-jnl',
            'separate_fig_and_tab_page': self.separate_fig_and_tab_page,
            'figure_placement': self.figure_placement,
            'referee': self.referee,
            'line_numbers': self.line_numbers,
            'bibliography_style': self.bibliography_style
        })
        
        
        return nb
    
    def process_cell_metadata(self, nb): 
        """Process metadata for all cells."""
        nb = super().process_cell_metadata(nb)
        
        # Loop through cells, gather processed tags, parse figures and tables
        for cell in nb.cells:
            metadata = self._get_metadata_handle(cell)
            tags = metadata.get('processed_tags', {})
            
            # Process figures
            if self._has_figure_content(cell) or tags.get('figure', False):
                # Process code
                if tags.get('show', False):
                    self._process_code(cell, metadata, 'fig')
                else:
                    self._process_figure(cell, metadata)
            
            # Process tables
            if tags.get('table', False) or tags.get('stable', False):
                # Process code
                if tags.get('show', False):
                    self._process_code(cell, metadata, 'tab')
                else:
                    self._process_table(cell, metadata)
            
            # Process code
            if tags.get('show', False) and not (tags.get('figure', False) or tags.get('table', False) or tags.get('stable', False)):
                self._process_code(cell, metadata, 'code')
                
        return nb
    
    # FIGURE PROCESSING -------------------------------------------------------#
    def _has_figure_content(self, cell):
        if cell.cell_type == 'markdown':
            # Check for markdown image syntax with common image extensions
            return bool(re.search(
                r'!\[.*?\]\(.*?\.(?:png|jpe?g|gif|tiff?|bmp|eps|pdf)\)',
                cell.source,
                re.IGNORECASE
            ))
        elif cell.cell_type == 'code' and hasattr(cell, 'outputs'):
            return any(
                output.get('output_type') == 'display_data' and 
                any(mime.startswith('image/') for mime in output.get('data', {}))
                for output in cell.outputs
            )
        return False
    
    def _process_figure(self, cell, metadata):
        """Process figure metadata."""
        float_metadata, updated_source = parse_metadata_content(cell.source, is_markdown=cell.cell_type == 'markdown')
        cell.source = updated_source
        
        self._figure_count += 1
        
        # Generate label if not provided
        if not float_metadata.get('label'):
            float_metadata['label'] = f'fig:{self._figure_count:02d}'
        
        if cell.cell_type == 'markdown':
            metadata.update(float_metadata)
        else:
            # Process code cell outputs
            for output in cell.outputs:
                if 'metadata' not in output:
                    output.metadata = NotebookNode()
                output.metadata.update(float_metadata)
        return copy.deepcopy(float_metadata)
                    
    
    # TABLE PROCESSING --------------------------------------------------------#
    def _process_table(self, cell, cell_metadata):
        """Process table metadata."""
        float_metadata, updated_source = parse_metadata_content(cell.source, is_markdown=cell.cell_type == 'markdown')
        cell.source = updated_source
        
        self._table_count += 1
        
        # Generate label if not provided
        if not float_metadata.get('label'):
            float_metadata['label'] = f'tab:{self._table_count}'
        
        if cell.cell_type == 'markdown':
            cell_metadata.update(float_metadata)
        else:
            # Process code cell outputs
            for output in cell.outputs:
                if 'metadata' not in output:
                    output.metadata = NotebookNode()
                output.metadata.update(float_metadata)
        return copy.deepcopy(float_metadata)
    
    # CODE PROCESSING --------------------------------------------------------#
    def _process_code(self, cell, cell_metadata, float_type):
        """Process code metadata."""
        # Increment figure counter for all code blocks
        self._figure_count += 1
        current_float_count = self._figure_count

        # Handle figures and tables
        if float_type == 'fig':
            float_metadata = self._process_figure(cell, cell_metadata)
            float_metadata['caption'] = f'Source code for Fig.~\\ref{{{float_metadata["label"]}}}'
        elif float_type == 'tab':
            float_metadata = self._process_table(cell, cell_metadata)
            float_metadata['caption'] = f'Source code for Table~\\ref{{{float_metadata["label"]}}}'
        else:
            # Standalone code: parse metadata and update source
            float_metadata, updated_source = parse_metadata_content(cell.source, is_markdown=False)
            cell.source = updated_source
            float_metadata.setdefault('label', f'code:{current_float_count:02d}')
            float_metadata.setdefault('caption', 'Source Code.')

        # Update metadata
        if float_type in ('fig', 'tab'):
            float_metadata['label'] = f'code:{float_metadata["label"]}'

        cell_metadata.update(float_metadata)
        return copy.deepcopy(float_metadata)
