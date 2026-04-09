import glob
def ls(folder = None):
        '''
        This functions behaves just like the ls program in the shell. 
        >>> ls()
        'README.md chat.py dist htmlcov pyproject.toml requirements.txt tools'

        >>> ls('tools')
        'tools/__pycache__ tools/calculate.py tools/cat.py tools/grep.py tools/ls.py'
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
        
        

             
