"""
Preprocessors for handling different input formats.
"""
from traitlets import Unicode, List

from nbconvert.preprocessors import Preprocessor
from nbconvert.preprocessors.execute import CellExecutionError
from pygments.formatters import LatexFormatter

import re
from contextlib import redirect_stdout, redirect_stderr
import io
import logging

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
    def __init__(self, **kw):
        super().__init__(**kw)
        self._global_ns = {'plt': plt}  # Initialize global_ns here

    @property
    def global_ns(self):
        return self._global_ns

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

    def has_inline(self, cell):
        if cell.cell_type == 'markdown':
            return bool(re.search(r'\{\{\s*(.*?)\s*\}\}', cell.source))
        elif cell.cell_type == 'code':
            return bool(re.search(r'#.*\{\{\s*(.*?)\s*\}\}.*', cell.source))
        return False

    def execute_code(self, code, cell_index):
        try:
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, self.global_ns)
                plt.close('all')
            stdout_content = stdout_buffer.getvalue()
            stderr_content = stderr_buffer.getvalue()
            if stderr_content:
                self.log.critical(f"Cell {cell_index} stderr:\n{stderr_content}")
            return stdout_content
        except CellExecutionError as e:
            self.log.warning(f"Execution error in cell {cell_index}: {str(e)}")
        except Exception as e:
            self.log.warning(f"Failed to execute cell {cell_index}: {str(e)}")
        return ""

    def execute_cell(self, cell, cell_index):
        if cell.cell_type == 'code' and ('skip-execution' not in cell.metadata.get('tags', [])):
            self.execute_code(cell.source, cell_index)

    def evaluate_expression(self, expr, cell_index):
        try:
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                result = eval(expr, self.global_ns)
            return str(result)
        except Exception as e:
            self.log.warning(f"Warning: Failed to evaluate expression '{expr}' in cell {cell_index}: {str(e)}")
            return f"{{{{ {expr} }}}}"

    def execute_inline(self, cell, cell_index):
        pattern = r'\{\{\s*(.*?)\s*\}\}'

        def evaluate_expression(match):
            expr = match.group(1)
            return self.evaluate_expression(expr, cell_index)

        if cell.cell_type == 'markdown':
            cell.source = re.sub(pattern, evaluate_expression, cell.source)
        elif cell.cell_type == 'code':
            lines = cell.source.split('\n')
            processed_lines = []
            for line in lines:
                stripped = line.lstrip()
                if stripped.startswith('#'):
                    comment_text = stripped[1:]
                    processed_comment = re.sub(pattern, evaluate_expression, comment_text)
                    processed_line = line[:len(line)-len(stripped)] + '#' + processed_comment
                    processed_lines.append(processed_line)
                else:
                    processed_lines.append(line)
            cell.source = '\n'.join(processed_lines)

    def preprocess(self, nb, resources):
        if self.author_names is not None:
            nb.metadata["authors"] = [{"name": author} for author in self.author_names]
        if self.date is not None:
            nb.metadata["date"] = self.date
        if self.title is not None:
            nb.metadata["title"] = self.title

        # First pass: check for inline expressions
        has_expr = False
        for cell in nb.cells:
            has_expr = self.has_inline(cell)
            if has_expr:
                break
        if not has_expr:
            return nb, resources

        # Second pass: execute code cells to build up the namespace
        for index, cell in enumerate(nb.cells):
            self.execute_cell(cell, index)

        # Third pass: process inline contents
        for index, cell in enumerate(nb.cells):
            self.execute_inline(cell, index)

        return nb, resources
