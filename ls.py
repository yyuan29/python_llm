import glob
def ls(folder = None):
        '''
        This functions behaves just like the ls program in the shell. 
        >>> ls()
        
        '''
        if folder: 
            result = '' 
            #folder + '/*' ==> tools/*
            # glob is nondeterminsiitc; no guarantees about order of glob results
            for path in glob.glob(folder +'/*'):
                result += path
            return result
        else:
            result = ''
            for path in sorted(glob.glob['*']):
                result += path + ''
            return result.strip()
        

             
