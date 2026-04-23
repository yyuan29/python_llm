# Yumo's Python LLM
![doctest](https://github.com/yyuan29/python_llm/actions/workflows/doctest.yml/badge.svg)
![integration-tests](https://github.com/yyuan29/python_llm/actions/workflows/test_integration.yml/badge.svg)
![flake8](https://github.com/yyuan29/python_llm/actions/workflows/flake8.yml/badge.svg)
![Python Tests](https://github.com/yyuan29/python_llm/actions/workflows/coverage.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/cmc-csci040-yyuan29)](https://pypi.org/project/cmc-csci040-yyuan29/)

A command-line chat agent that uses Groq's LLM API. The agent is able to hold conversations and answer questions. It can also call built-in tools: (`calculate`, `cat`, `grep`, `ls`). 

Here is a gif of a working example of my code: 

![Demo](output.gif)

## Usage
### Slash Commands

Any tool name that starts with '/' will run directly.


`/ls` should give you all the files in a specific folder:
```
chat> /ls tools
tools/calculate.py tools/cat.py tools/grep.py tools/ls.py tools/screenshot.png tools/utils.py
chat> what files are in the tools folder?
The files in the tools folder are: calculate.py, cat.py, grep.py, ls.py, and utils.py. There is also a screenshot.png file.
```

`/calculate` should give you all the files in a specific folder:
```
chat> /calculate 2*6
12
```

`/grep` searches your codebase with regex and feeds the output into the conversation:
```
chat> /grep ^def test_projects/project001/markdown_compiler/__main__.py
def main():
```
`/cat` returns the raw files:
```
chat> /cat tools/calculate.py
def calculate(self):
    """
    Evaluate a mathematical expression.
...
```
`/compact` summarizes the entire conversation:
```
chat> Hello!
Hello, it's nice to meet you. How can I assist you today?
chat> My name is Yumo. How are you?
Nice to meet you, Yumo. I'm functioning well, thank you for asking, and I'm here to help with any questions or topics you'd like to discuss.
chat> What does the utils.py file do?
The `utils.py` file is a common Python module that contains various utility functions, often used across multiple projects or scripts, to perform tasks such as data manipulation, file operations, string processing, and more.
chat> /compact
Yumo asked about the purpose of a Python file named `utils.py`, and I explained that it typically contains utility functions for tasks like data manipulation and file operations.
```

### Agent in Action
This shows the creation of a greet.py file in the docsum folder. 
```
chat> Create a greet.py file that has a hello.py function
[feature-work 5307955] [docchat] update file
 1 file changed, 1 insertion(+), 1 deletion(-)
Committed files: ['greet.py']

Doctest Results:
1 item had no tests:
    greet
0 tests in 1 item.
0 passed.
Test passed.
```

This following example hence will delete the greet.py file. 
```
chat> delete greet.py
[feature-work e237a7a] [docchat] rm greet.py
 2 files changed, 2 insertions(+), 1 deletion(-)
 delete mode 100644 greet.py
Removed: ['greet.py']
```