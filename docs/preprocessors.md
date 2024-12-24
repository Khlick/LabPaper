# Preprocessors

Preprocessors in LabPaper modify notebook content before the conversion process begins. They handle tasks like code execution, markdown processing, and content validation.

## Available Preprocessors

### PythonMarkdownPreprocessor

Processes Python code within markdown cells, allowing for dynamic content generation.

~~~python
# In a markdown cell
{python}
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3]})
print(f"Data shape: {df.shape}")
{/python}
~~~

### PythonCodePreprocessor

Handles Python code cells, managing execution and output formatting.

## Configuration

Preprocessors can be configured in your Jupyter configuration:

~~~python
c.LabPaperExporter.preprocessors = [
    'labpaper.preprocessors.PythonMarkdownPreprocessor',
    'labpaper.preprocessors.PythonCodePreprocessor'
]
~~~

## Custom Preprocessors

Create custom preprocessors by inheriting from `nbconvert.preprocessors.Preprocessor`:

~~~python
from nbconvert.preprocessors import Preprocessor

class CustomPreprocessor(Preprocessor):
    def preprocess_cell(self, cell, resources, index):
        # Your preprocessing logic here
        return cell, resources
~~~ 