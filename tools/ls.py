import glob
def ls(folder = None):
        '''
        This functions behaves just like the ls program in the shell. 
        >>> ls()
        'README.md __pycache__ calculate.py cat.py chat.py dist grep.py htmlcov ls.py pyproject.toml requirements.txt'

        >>> ls('tools')
        'tools/__pycache__ tools/ls.py'
        '''
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
        
        

             
