"""Base exporter class for LabPaper."""
import os
import sys
import shutil
import subprocess
from tempfile import TemporaryDirectory

from traitlets import Bool, Unicode, List, default, Instance
from traitlets.config import Config
import logging

# NBConvert
from nbconvert.exporters import LatexExporter
from nbformat.notebooknode import NotebookNode
from nbconvert.utils import _contextlib_chdir

# Local Imports
from .latexerror import LatexFailed
from labpaper import filters as labpaper_filters

custom_filters = {
    "comment_lines": labpaper_filters.comment_lines,
    "newline_block": labpaper_filters.newline_block,
    "latex_internal_references": labpaper_filters.latex_internal_references,
}

def prepend_to_env_search_path(varname, value, envdict):
    """Add value to the environment variable varname in envdict

    e.g. prepend_to_env_search_path('BIBINPUTS', '/home/sally/foo', os.environ)
    """
    if not value:
        return  # Nothing to add

    envdict[varname] = value + os.pathsep + envdict.get(varname, "")

class LabPaperBaseExporter(LatexExporter):
    """Base exporter class for LabPaper that extends nbconvert's LaTeX exporter."""
    def __init__(self, config=None, **kw):
        super().__init__(config=config, **kw)
        self.log = logging.getLogger(__name__)
        
    # Metadata processing configuration
    process_metadata = Bool(
        True,
        help="Whether to process and transform cell metadata"
    ).tag(config=True)
    
    bibliography_style = Unicode(
        default_value='plain',
        help="BibTeX style to use for citations"
    ).tag(config=True)
    
    latex_class = Unicode(
        default_value='article',
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
    
    no_bib = Bool(
        default_value=False,
        help="Whether to suppress the bibliography"
    ).tag(config=True)
    
    # Location to find local files as well
    texinputs = Unicode(help="texinputs dir. A notebook's directory is added")
    writer = Instance("nbconvert.writers.FilesWriter", args=(), kw={"build_directory": "."})

    @property
    def default_config(self):
        """Default configuration for LabPaper base exporter"""
        # Ensure WindowsSelectorEventLoopPolicy to avoid Tornado warnings
        import sys
        import asyncio
        if sys.platform.startswith("win32") and asyncio.get_event_loop_policy().__class__.__name__ != "WindowsSelectorEventLoopPolicy":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        c = Config({
            'labpaper.preprocessors.PythonMarkdownPreprocessor': {'enabled': True},
            'ExtractAttachmentsPreprocessor': {'enabled': True},
            'ExtractOutputPreprocessor': {'enabled': True},
            'SVG2PDFPreprocessor': {'enabled': True},
            'LatexPreprocessor': {'enabled': True},
            'SphinxPreprocessor': {'enabled': True},
            'HighlightMagicsPreprocessor': {'enabled': True},
            'ExecutePreprocessor': {'enabled': True,'metadata':{'path':"./"}},
            'TagRemovePreprocessor': {'enabled': True,'remove_cell_tags':['remove-cell'],'remove_input_tags':['no-display']},
        })
        if super().default_config:
            c2 = super().default_config.copy()
            c2.merge(c)
            c = c2
        return c
    
    @default('preprocessors')
    def _preprocessors_default(self):
        """Default preprocessors"""
        return [
            'labpaper.preprocessors.PythonMarkdownPreprocessor'
        ]
    
    def default_filters(self):
        """Default filters"""
        yield from super().default_filters()
        yield from custom_filters.items()
    
    def _init_resources(self, resources):
        """Initialize resources dict with labpaper-specific settings."""
        resources = super()._init_resources(resources)
        resources.update({'labpaper': NotebookNode()})
        return resources

    
    def _preprocess(self, nb, resources):
        """Preprocess notebook with metadata handling."""
        if self.process_metadata:
            nb = self.process_notebook_metadata(nb)
        nb, resources = super()._preprocess(nb, resources)
        nb = self.process_cell_metadata(nb)
        return nb, resources
    
    # Utility methods
    def _get_metadata_handle(self, obj):
        """Get metadata handle from the object."""
        obj.metadata["labpaper"] = obj.metadata.get('labpaper', NotebookNode())
        return obj.metadata.labpaper
    
    def _has_citations(self, nb):
        """Check if notebook contains citations."""
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                # Check for common citation patterns
                if '\\cite{' in cell.source:
                    return True
        return False

    def _has_bibliography_command(self, nb):
        """Check if notebook already contains bibliography LaTeX commands."""
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                if '\\bibliography{' in cell.source:
                    self.log.debug(f"Bibliography command found in cell with index {nb.cells.index(cell)}")
                    return True
            elif cell.cell_type == 'code':
                # Check outputs for LaTeX that might contain bibliography commands
                if hasattr(cell, 'outputs'):
                    for output in cell.outputs:
                        if output.output_type in ('display_data', 'execute_result'):
                            if 'text/latex' in output.data:
                                latex_output = output.data['text/latex']
                                if '\\bibliography{' in latex_output:
                                    return True
        return False
    
    def _get_texmf_path(self):
        """Get the path to the package's texmf directory."""
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "texmf"))
    
    def _run_command(self, command_list, filename, count=1):
        """Run a command count times."""
        command = [c.format(filename=filename) for c in command_list]
        
        cmd = shutil.which(command[0])
        if cmd is None:
            link = "https://nbconvert.readthedocs.io/en/latest/install.html#installing-tex"
            msg = (
                f"{command[0]} not found on PATH, if you have not installed "
                f"{command[0]} you may need to do so. Find further instructions "
                f"at {link}."
            )
            raise OSError(msg)
        shell = sys.platform == "win32"
        if shell:
            command = subprocess.list2cmdline(command)  # type:ignore[assignment]
        env = os.environ.copy()
        prepend_to_env_search_path("TEXINPUTS", self.texinputs, env)
        prepend_to_env_search_path("BIBINPUTS", self.texinputs, env)
        prepend_to_env_search_path("BSTINPUTS", self.texinputs, env)

        self.log.info(f"Running {command[0]} {count} time(s): {command}")
        for _ in range(count):
            try:
                completed_process = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=shell,  # noqa: S603
                    env=env,
                    check=True,
                    text=True
                )
                out = completed_process.stdout
                if completed_process.returncode != 0:
                    self.log.critical("%s failed: %s\n%s", command[0], command, out)
                    return False  # failure
            except subprocess.CalledProcessError as e:
                self.log.error(f"Command failed with output:\n{e.output}")
                raise LatexFailed(e.output)
        return True
            
    

    # Base methods for subclasses to implement, these tend to need super() calls
    def process_notebook_metadata(self, nb):
        """Process notebook-level metadata."""
        metadata = self._get_metadata_handle(nb)
        
        has_citations = self._has_citations(nb)
        has_bib_commands = self._has_bibliography_command(nb)
        self._needs_bibliography = has_citations and not has_bib_commands
        
        if has_citations and not has_bib_commands:
            bib_cell = NotebookNode({
                'cell_type': 'markdown',
                'metadata': NotebookNode({'labpaper': NotebookNode({'auto_bibliography': True})}),
                'source': '% Start references section on new page\n\\clearpage\n\n'
            })
            nb.cells.append(bib_cell)
        
        metadata.update({
            'has_citations': has_citations,
            'has_bibliography_section': has_bib_commands,
            'needs_bibliography': has_citations and not has_bib_commands,
            'bibliography_style': self.bibliography_style,
            'latex_class': self.latex_class
        })
        
        return nb
    
    def process_cell_metadata(self, nb): 
        """Process metadata for all cells."""
        for cell in nb.cells:
            if not hasattr(cell, 'metadata'):
                cell.metadata = NotebookNode()
            
            metadata = self._get_metadata_handle(cell)
            tags = cell.metadata.get('tags', [])
            metadata.update({
                'processed_tags': self.process_cell_tags(tags),
                'cell_type': cell.cell_type,
            })
        return nb
    
    def from_notebook_node(self, nb, resources=None, **kw):
        """Convert a notebook to PDF and organize output files."""
        latex, resources = super().from_notebook_node(nb, resources=resources, **kw)
        
        # Get notebook information
        notebook_name = resources['metadata'].get('name', 'notebook')
        notebook_path = os.path.abspath(resources['metadata'].get('path', ''))
        self.texinputs = notebook_path
        
        # Check for bibliography
        if not hasattr(self, '_needs_bibliography'):
            has_citations = self._has_citations(nb)
            has_bib_commands = self._has_bibliography_command(nb)
            self._needs_bibliography = has_citations and not has_bib_commands        

        # Create output directory with same name as notebook
        output_dir = os.path.join(notebook_path, notebook_name)
        os.makedirs(output_dir, exist_ok=True)
        with TemporaryDirectory() as td:
            # Copy LaTeX support files
            self.setup_support_files(td,notebook_name,notebook_path)
            
            with _contextlib_chdir.chdir(td):
                # Write latex to temporary directory
                tex_file = f"{notebook_name}.tex"
                with open(tex_file, 'w', encoding='utf-8') as f:
                    f.write(latex)
                
                # Copy any additional resources (like images)
                if resources.get('outputs', None):
                    for filename, data in resources['outputs'].items():
                        dest = os.path.join(td, filename)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        with open(dest, 'wb') as f:
                            f.write(data)
                
                # Copy all files to output directory before compilation
                for file in os.listdir(td):
                    src = os.path.join(td, file)
                    dst = os.path.join(output_dir, file)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                
                # Now compile
                try:
                    self.compile_latex(tex_file)
                    
                    # Copy generated PDF to notebook directory
                    pdf_file = os.path.splitext(tex_file)[0] + '.pdf'
                    if not os.path.isfile(pdf_file):
                        raise LatexFailed("PDF file not produced")
                    self.log.info("PDF successfully created")
                    with open(pdf_file, "rb") as f:
                        pdf_data = f.read()
                except Exception as e:
                    self.log.error(f"LaTeX compilation failed: {str(e)}")
                    self.log.info(f"LaTeX source files are available in: {output_dir}")
                    raise
                finally:
                    self.log.info(f"Cleaning up temporary directory: {td}")
                    shutil.rmtree(td, ignore_errors=True)
                    self.log.info(f"LaTeX source files are available in: {output_dir}")
                
        # convert output extension to pdf
        # the writer above required it to be tex
        resources["output_extension"] = ".pdf"
        # clear figure outputs and attachments, extracted by latex export,
        # so we don't claim to be a multi-file export.
        resources.pop("outputs", None)
        resources.pop("attachments", None)

        return pdf_data, resources

    def setup_support_files(self, td, notebook_name, notebook_path):
        """Setup support files in temporary directory."""
        texmf_path = self._get_texmf_path()
        latex_path = os.path.join(texmf_path, 'tex/latex')
        bibtex_path = os.path.join(texmf_path, 'bibtex/bst')
        gen_dest = lambda name: os.path.join(td,f"{name}")
        # Prepare Bibliography
        if self._needs_bibliography:
            self.log.info("Setting up bibliography")
            # List of possible bib file locations
            bib_locations = [
                # Same name as notebook
                os.path.join(notebook_path, f"{notebook_name}.bib"),
                # references.bib in same directory
                os.path.join(notebook_path, "references.bib"),
                # bibliography.bib in same directory
                os.path.join(notebook_path, "bibliography.bib")
            ]
            # Try to find and copy the first available bib file
            bib_success = False
            for bib_path in bib_locations:
                if os.path.exists(bib_path):
                    self.log.info(f"Found bibliography file: {bib_path}")
                    shutil.copy2(bib_path, os.path.join(td, 'references.bib'))
                    bib_success = True
                    break
            if not bib_success:
                self.log.warning("No bibliography file found. Looked for: \n" + "\n".join(f"- {loc}" for loc in bib_locations))
                self._needs_bibliography = False
            # Check for bibliography style file
            style_matches = [f for f in os.listdir(bibtex_path) 
                            if f.startswith(f"{self.bibliography_style}.") 
                            and os.path.isfile(os.path.join(bibtex_path, f))]
            if style_matches:
                style_file = style_matches[0]
                style_path = os.path.join(bibtex_path, style_file)
                self.log.info(f"Found bibliography style file: {style_path}")
                shutil.copy2(style_path, gen_dest(style_file))
            else:
                self.log.debug(f"Bibliography style '{self.bibliography_style}' not found in package, assuming it is built-in")
        # Check if we need to copy a custom latex class
        class_dir = os.path.join(latex_path, self.latex_class)
        if os.path.isdir(class_dir):
            self.log.info(f"Found LaTeX class directory: {class_dir}")
            for filename in os.listdir(class_dir):
                src_path = os.path.join(class_dir, filename)
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, gen_dest(filename))
        else:
            self.log.debug(f"LaTeX class '{self.latex_class}' not found in package, assuming it is built-in")

    def compile_latex(self, tex_file):
        """Compile LaTeX file."""
        has_bib = self._needs_bibliography
        tex_base = os.path.splitext(tex_file)[0]
        latex_command = [self.latex_engine] + self.latex_command
        self.log.info(f"Running LaTeX command: {latex_command}")
        self._run_command(latex_command, tex_file)
        if not self.no_bib:
            if has_bib and self._run_command(self.bib_command, tex_base):
                self._run_command(latex_command, tex_file)
            
        self.log.info(f"Running LaTeX command again: {latex_command}")
        self._run_command(latex_command, tex_file)

    # Abstract methods for subclasses to implement
    def process_cell_tags(self, tags): return {}
