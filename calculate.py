
def calculate(self, expression):
        """Standard calculator tool."""
        try:
            return str(eval(expression, {"__builtins__": None}, {}))
        except Exception as e:
            return f"Error: {e}"