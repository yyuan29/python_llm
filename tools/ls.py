from tools.utils import is_path_safe
import glob

def ls(folder = "."):
        '''
        This function behaves like the ls program in the shell.

        >>> output = ls()
        >>> isinstance(output, str)
        True
        >>> len(output) > 0
        True

        # check that files are prefixed with "./"
        >>> all(item.startswith("./") for item in output.split())
        True

        # test listing a known folder
        >>> output = ls('tools')
        >>> isinstance(output, str)
        True
        >>> all(item.startswith("tools/") for item in output.split())
        True

        # unsafe path (absolute)
        >>> ls('/etc')
        'Error: unsafe path'

        # unsafe path (directory traversal)
        >>> ls('../secret')
        'Error: unsafe path'

        >>> output = ls("")
        >>> isinstance(output, str)
        True
        >>> len(output) > 0
        True
        '''

        if not is_path_safe(folder):
            return "Error: unsafe path"
        
        if folder: 
            result = '' 
            #folder + '/*' ==> tools/*
            # glob is nondeterminsiitc; no guarantees about order of glob results
            result = sorted(glob.glob(folder + '/*'))
            return ' '.join(result)
        else:
            result = ''
            result = sorted(glob.glob('*'))
            return ' '.join(result)