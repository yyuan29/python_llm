import glob
def ls(folder = None):
        '''
        This functions behaves just like the ls program in the shell. 
        >>> ls()
        'README.md __pycache__ chat.py dist empty.txt htmlcov pyproject.toml requirements.txt t_bin t_dir t_txt test1.txt test2.txt tools utf16.txt'

        >>> ls('tools')
        'tools/__pycache__ tools/calculate.py tools/cat.py tools/grep.py tools/ls.py tools/screenshot.png'
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
        
        

             
