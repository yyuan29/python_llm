# Yumo's Python LLM
![doctest](https://github.com/yyuan29/python_llm/actions/workflows/doctest.yml/badge.svg)
![integration-tests](https://github.com/yyuan29/python_llm/actions/workflows/test_integration.yml/badge.svg)
![flake8](https://github.com/yyuan29/python_llm/actions/workflows/flake8.yml/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/cmc-csci040-yyuan29)](https://pypi.org/project/cmc-csci040-yyuan29/)
<!-- coverage badge? -->

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
chat> /grep ^def tools/*.py
def calculate(self):
def cat(path):
def compact(chat):
def grep(pattern, path):
def ls(folder="."):
def is_path_safe(path):
```
`/cat` returns the raw files:
```
chat> /cat tools/calculate.py
def calculate(self):
    """
    Evaluate a mathematical expression.
...
```
