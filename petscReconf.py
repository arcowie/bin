#!/usr/bin/env python3
import argparse
import os
import subprocess as sp



def getPetscDir():
    petscDir = os.environ.get('PETSC_DIR')
    if petscDir is None:
        print(f'\nThe enviromental variable PETSC_DIR can not be found\n'
        'if you wish to continue type n, else input the absolute path where PETSc is installed\n')
    else:
        return petscDir
    value = input()
    if value.lower() == 'n':
        print(f'\nYou entered {value}, exiting script\n')
        exit()
    else:
        counter = 0
        while counter == 0:
            print(f'\nYou entered {value}\nIf this is correct type y or type n to reinput path\n')
            value =input ()
            if value.lower() == 'y':
                return value
            else:
                print(f'\nPlease enter the new path\n')
                value = input()
             
        
def getArches(arches, petscDir):
    """
    This function takes two parameters, arches and petscDir and returns a list of valid arches as a list of strings
    The default behavior is when the values of arches is None.  Then the funciton will use os.listdir in the director
    that was provided in petscDir and return a list with all directories that begin with arch.

    If arches is not None, then it will compare the list of arches with the results from os.listdir and return a list
    of all arch names that are valid, ie that were found using os.listdir.  The function will output which arch names
    were not found.  If no valid arches were found it will exit.

    Parameters:
    arches (str): Default is None, otherwise a list of arch names as strings.
    petscDir (str): Contains a string with the absolute path to PETSc.

    Returns:
    str: List of valid arches
    """
    archListTemp = []
    archListSub = []
    for entry in os.listdir(petscDir):
        if 'arch' in entry:
            archListTemp.append(entry)
    if arches == None:
        if len(archListTemp)==0:
            print(f'No valid arches were found in path: {petscDir}\n'
            'This could be because you have not created any using ./configure or'
            ' Your arches do not start with arch.  Please check your path.\n'
            'if your arches do not start with arch you will have to input them'
            'individually using the command line argument -a or --arches\n'
            'exiting')
            exit()
        else:
            return archListTemp
    else:
        for item in arches:
            if item in archListTemp:
              archListSub.append(item)
            else:
                print(f'Specified arch: [{item}] not found.\n')
        if len(archListSub) == 0:
            print(f'None of the specified arches: {arches} found.\nExiting')
            exit()
        else:
            return archListSub  


def runMake(arch, petscDir):
    """
    This function is run if the make argument passed to main is 1.  It takes two parameters, arch and petscDir
    and runs make on the arch.  This is the deafult behavior of the script.

    Parameters:
    arch (str): The current arch being rebuild.
    petscDir (str): Contains a string with the absolute path to PETSc.

    Returns:
    None
    """
    #text that is checked to see if the make was successful
    makeTestWorked = '# No test results in'
    print(f'\nOn arch: {arch}\nRunning make\n')
    result = sp.run(['make', '-j','8','-f', './gmakefile', 'test', 'search="dm_impls_plex_test-ex5_0"' ], cwd=petscDir, capture_output=True, text=True)
    if makeTestWorked in result.stdout:
        print(f'\nMake worked\n')

def runReconf(arch, clean, addArguments, petscDir):
    """
    This function is run if the reconfig argument passed to main is 1.  It takes four parameters, arch, clean,
    addArguments, petscDir.  It runs the PETSc reconfigure script for the arch specified in arch and adds 
    additional arguments or does it --with-clean depending on the values in addArguments and clean.

    Parameters:
    arch (str): The current arch being reconfigured.
    clean (int): Default 0.  If it is 1 then --with-clean is added to the arguments for the reconfigure script.
    addArguments (str): Default is None.  Otherwise it contains a list of additional argument for the reconfigure script.
    petscDir (str): Contains a string with the absolute path to PETSc.

    Returns:
    None
    """
    
    subDir =  os.sep + 'lib' + os.sep + 'petsc' + os.sep + 'conf' +os.sep
    reconf='reconfigure-' + arch + '.py'
    
    print(f'Running {reconf}')

    tempArgs = []
    optArgs = ''
    if addArguments is not None:
        for arg in addArguments:
            tempArgs.append('--'+arg)
        optArgs = ' '.join(tempArgs)

    if clean == 1:
        cleanArg = '--with-clean'
    else:
        cleanArg = ''
    
    result = sp.run([petscDir+os.sep+arch+subDir+reconf, optArgs, cleanArg], capture_output=True, text=True, cwd=petscDir)
    print(result)
    result = sp.run(['make', 'PETSC_DIR='+petscDir, 'PETSC_ARCH='+arch, 'all'], capture_output=True, text=True, cwd=petscDir)
    result = sp.run(['make', 'PETSC_DIR='+petscDir, 'PETSC_ARCH='+arch, 'check'], capture_output=True, text=True, cwd=petscDir)
    
    if 'Error' in result.stdout:
        print(f'\nAn Error occured when checking PETSc libraries for arch: {arch}\n')
        print(result.stdout)
    else:
        print(f'\nPETSc checks were successful\n')
        print(result.stdout) 

def main(make, reconfig=0, clean=0, addArguments=None, arches=None):
    
    #Needed because parse_args passes a list if a command line argument is specified and passes
    #a single value if the default is used.
    if type(make) is list:
        make = make[0]
    if type(clean) is list:
        clean = clean[0]
    if type(reconfig) is list:
        reconfig = reconfig[0]

    if make==0 and reconfig==0:
        print(f'Both the make and reconfig arguments are 0.  One of these must be set to 1\n'
                'Please input m for make, r for reconfigure, or n to exit\n')
        result = input()
        if result.lower() == 'm':
            make = 1
        elif result.lower() == 'r':
            reconfig = 1
        elif result.lower() == 'n':
            print('Exiting')
            exit()
        else:
            print(f'Invalid input of: {result} inputed\nExiting')
            exit()
    
    petscDir = getPetscDir()
    
    
    #code assumes that the os.sep is not included at the end of the directory
    if petscDir[-1] == os.sep:
        petscDir = petscDir[1:len(petscDir)-1]
 

    #Used even arches are specified as this function also ensures that specified arches exist
    archList = getArches(arches, petscDir)


    for arch in archList:
        #Sets the enviromental variable PETSC_ARCH to the current arch being worked on
        os.environ['PETSC_ARCH']=arch
        if make == 1:
            runMake(arch, petscDir)
        if(reconfig == 1 or clean == 1 or addArguments !=None):
            runReconf(arch, clean, addArguments, petscDir)


if __name__ == "__main__":
    cmdLine = argparse.ArgumentParser(description='This is a script to rebuild or reconfigure PETSc arches\n'  
                                        'Note it is assumed that all arches start with arch')
    cmdLine.add_argument('-m', '--make', nargs=1, type=int, default=1, choices=[0,1], 
                            help='This is the default option and will run make on PETSc arches')
    cmdLine.add_argument('-r', '--reconfig', nargs=1, type=int, default=0, choices=[0,1],
                            help='Use this command line option to run the reconfigure script in ')
    cmdLine.add_argument('-c', '--clean', nargs=1, type=int, default=0, choices=[0,1], 
                            help='This will cause a reconfigure with a clean state\nCAUTION: everything in the arch will be deleted')
    cmdLine.add_argument('-aa', '--addArguments', nargs='*', type=str, default=None, 
                            help='Add arguments when reconfiguring\nNOTE: requires reconfig script to be run.')
    cmdLine.add_argument('-a', '--arches', nargs='*', type=str, default=None, 
                            help='Specify arches to run make or reconfig on. The Default is all arches')

    cmdLineArgs = cmdLine.parse_args()

    main(cmdLineArgs.make, cmdLineArgs.reconfig, cmdLineArgs.clean, cmdLineArgs.addArguments, cmdLineArgs.arches)
