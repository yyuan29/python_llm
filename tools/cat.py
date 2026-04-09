import os

def cat(self, path):
        if os.path.isabs(path) or ".." in path:
            return "Error: Absolute paths or directory traversal not allowed."
        
        for encoding in ['utf-8', 'utf-16']:
            try:
                with open(path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                return f"Error: File '{path}' not found."
            except Exception as e:
                return f"Error: {e}"
        return "Error: Could not decode file (likely binary)."