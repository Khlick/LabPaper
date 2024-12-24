"""Custom filters to be used with IPython nbconvert."""
import re

__all__ = ['newline_block', 'latex_internal_references','comment_lines']

def newline_block(text):
    """ Filter that makes sure that a block will always start with a newline """
    return r"""
{0:s}
""".format(text)


def latex_internal_references(text):
    """Take markdown text and replace instances of
    '[blah](#anchor-ref)' with 'autoref{anchor-ref}'
    """
    ref_pattern = re.compile(r'\[(?P<text>.*?)\]\(#(?P<reference>.*?)\)')
    replacement = r'\\autoref{\g<reference>}'

    return ref_pattern.sub(replacement, text)

def comment_lines(text, comment_char="%"):
    """Adds a comment character and space to every line of the text."""
    lines = text.splitlines()
    return "\n".join(f"{comment_char} {line}" for line in lines)