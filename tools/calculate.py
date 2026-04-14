def calculate(self):
    """
    Evaluate a mathematical expression.
    >>> calculate("1 + 2")
    '3'

    >>> calculate("5 * 2")
    '10'

    >>> calculate("8 / 2")
    '4.0'

    >>> calculate("7 / 0")
    'Error: division by zero'
    """
    try:
        return str(eval(self, {"__builtins__": None}, {}))
    except Exception as e:
        return f"Error: {e}"
