# Yumo's Python LLM
![doctest](https://github.com/yyuan29/python_llm/actions/workflows/doctest.yml/badge.svg)
![integration-tests](https://github.com/yyuan29/python_llm/actions/workflows/test_integration.yml/badge.svg)
![flake8](https://github.com/yyuan29/python_llm/actions/workflows/flake8.yml/badge.svg)

[![coverage](https://img.shields.io/badge/coverage-90%25-brightgreen)](#)
[![PyPI](https://img.shields.io/pypi/v/cmc-csci040-yyuan29)](https://pypi.org/project/cmc-csci040-yyuan29/)

A command-line chat agent that uses Groq's LLM API. The agent is able to hold conversations and answer questions. It can also call built-in tools: (`calculate`, `cat`, `grep`, `ls`). 

Here is a gif of a working example of my code: 
![Demo](output.gif)

## Usage
### Slash Commands

Any tool name that starts with '/' will run directly.

```
chat> /ls tools
tools/calculate.py tools/cat.py tools/grep.py tools/ls.py tools/screenshot.png tools/utils.py
chat> what files are in the tools folder?
The files in the tools folder are: calculate.py, cat.py, grep.py, ls.py, and utils.py. There is also a screenshot.png file.
```


