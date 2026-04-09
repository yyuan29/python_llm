import os
import re
import glob

def grep(self, pattern, path):
        """Searches for regex matches in files matching the glob."""
        if os.path.isabs(path) or ".." in path:
            return "Error: Access denied."
        
        results = []
        # Find all files matching the glob (e.g., *.txt)
        for fpath in sorted(glob.glob(path, recursive=True)):
            if os.path.isdir(fpath): continue
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for line in f:
                        if re.search(pattern, line):
                            results.append(line.strip())
            except:
                continue
        return "\n".join(results)