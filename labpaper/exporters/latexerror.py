class LatexFailed(IOError):
    """Exception for failed latex run.
    
    From nbconvert.exporters.pdf.LatexFailed
    """
    def __init__(self, output):
        self.output = output

    def __str__(self):
        return f'PDF creating failed, captured latex output:\n{self.output}'