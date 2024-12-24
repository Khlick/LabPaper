"""
Preprocessors for handling different input formats.
"""
from traitlets import Unicode, List
from nbconvert.preprocessors import Preprocessor
from nbconvert.preprocessors.execute import CellExecutionError
import re
from contextlib import redirect_stdout, redirect_stderr
import io
from pygments.formatters import LatexFormatter
import matplotlib.pyplot as plt  # Import pyplot here
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before any other matplotlib imports

class PygmentizePreprocessor(Preprocessor):
    
    style = Unicode("abap", help="Name of the pygments style to use").tag(config=True)
    
    def preprocess(self, nb, resources):
        # Generate Pygments definitions for Latex
        resources.setdefault("latex", {})
        resources["latex"].setdefault(
            "pygments_definitions", LatexFormatter(style=self.style).get_style_defs()
        )
        resources["latex"].setdefault("pygments_style_name", self.style)
        return nb, resources

class PythonMarkdownPreprocessor(Preprocessor):
    
    date = Unicode(
        None,
        help=("Date of the LaTeX document"),
        allow_none=True,
    ).tag(config=True)

    title = Unicode(None, help=("Title of the LaTeX document"), allow_none=True).tag(config=True)

    author_names = List(
        Unicode(),
        default_value=None,
        help=("Author names to list in the LaTeX document"),
        allow_none=True,
    ).tag(config=True)
    
    def preprocess(self, nb, resources):
        
        if self.author_names is not None:
            nb.metadata["authors"] = [{"name": author} for author in self.author_names]

        if self.date is not None:
            nb.metadata["date"] = self.date

        if self.title is not None:
            nb.metadata["title"] = self.title
        
        # Get the global namespace from the notebook's cells
        global_ns = {
            'plt': plt
        }
        # First pass: determine if the notebook has any markdown cells with {{ expr }} patterns
        has_markdown_with_expr = False
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                if re.search(r'\{\{\s*(.*?)\s*\}\}', cell.source):
                    has_markdown_with_expr = True
                    break
        if not has_markdown_with_expr:
            return nb, resources
        # Second pass: execute code cells to build up the namespace
        for index, cell in enumerate(nb.cells):
            if cell.cell_type == 'code' and not ('skip-execution' in cell.metadata.get('tags', [])):
                try:
                    # Create string buffer to capture output
                    stdout_buffer = io.StringIO()
                    stderr_buffer = io.StringIO()
                    
                    # Execute the code cell and capture output
                    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                        exec(cell.source, global_ns)
                        # Close any open figures to prevent display
                        plt.close('all')
                        
                except CellExecutionError as e:
                    self.log.debug(f"Execution error in cell {index} (execution count {cell.execution_count}): {str(e)}")
                    self.log.debug(f"Cell source:\n{cell.source[:200]}")
                except Exception as e:
                    self.log.debug(f"Warning: Failed to execute cell {index} for namespace: {str(e)}")
                    self.log.debug(f"Cell source:\n{cell.source[:200]}")
        
        # Third pass: process markdown cells
        for index, cell in enumerate(nb.cells):
            nb.cells[index], resources = self.preprocess_cell(cell, resources, index, global_ns)
            
        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index, global_ns):
        if cell.cell_type == 'markdown':
            # Regular expression to find {{ expr }} patterns
            pattern = r'\{\{\s*(.*?)\s*\}\}'
            
            def evaluate_expression(match):
                expr = match.group(1)
                try:
                    # Capture and suppress output during evaluation
                    stdout_buffer = io.StringIO()
                    stderr_buffer = io.StringIO()
                    
                    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                        result = eval(expr, global_ns)
                    return str(result)
                except Exception as e:
                    self.log.debug(f"Warning: Failed to evaluate expression '{expr}' in cell {cell_index}: {str(e)}")
                    return f"{{{{ {expr} }}}}"  # Keep original if evaluation fails
            
            # Replace all expressions in the markdown
            cell.source = re.sub(pattern, evaluate_expression, cell.source)
            
        return cell, resources
