import glob
import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
from os.path import basename

standartPassedFilePath = "passedCheck.txt"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def loadIgnored():
    ignoredFile = open(".checkIgnore")
    ignored = [ x.strip('\t').strip('\n') for x in ignoredFile.readlines()]
    ignoredFile.close()
    return ignored

#load files in src folder and remove ignored from list
def createFileList(ignored=[],srcFolder="../"):
    allFiles=glob.glob(srcFolder + "*.h")
    cleanedFiles = [x for x in allFiles if basename(x) not in ignored]
    return cleanedFiles

def loadPassed(fileName=standartPassedFilePath):
    passed = []
    if os.path.isfile(fileName):
        file = open(fileName, 'r')
        passed = [ x.strip('\t').strip('\n') for x in file.readlines()]
        file.close()
    return passed

def savePassed(passedFiles,filename=standartPassedFilePath):
    savefile = open("passedCheck.txt", 'w+')
    for passed in passedFiles:
        savefile.write(passed + "\n")
    savefile.close()

paddingResult = 40
paddingName = 40
paddingEntire= paddingResult + paddingName
def main():
    passedFiles = loadPassed()
    failedFiles = []
    showPassed = False
    allPassed = True

    ignored=loadIgnored()
    compilerCommand = "g++ -std=c++11 -DgFortran -DCDO "

    for file in createFileList(ignored) :
        name = basename(file)
        logFileName = "hc_" +name + ".log"
        log = open(logFileName,'wb+')

        if name not in passedFiles:
            command = compilerCommand + file
            process = subprocess.Popen(command.split(), cwd=os.getcwd(),stdout=log,stderr=log)
            output, error = process.communicate()
            if (process.returncode != 0):
                print((name + ": "   ).ljust(paddingName)
                      + bcolors.FAIL + ("FAIL   " 
                      + bcolors.ENDC + str(process.returncode)).ljust(paddingResult))
                failed =True
                allPassed = False
                failedFiles.append(name)
            else:
                if showPassed:
                    print((name + ": "   ).ljust(paddingName)
                          + bcolors.OKGREEN + "OK".ljust(paddingResult) +
                          bcolors.ENDC)
                    removeCommand = "rm " + logFileName
                    subprocess.Popen(removeCommand.split(), cwd=os.getcwd())

                passedFiles.append(name)
        else:
            print((name + ": "   ).ljust(paddingName)
                  + bcolors.OKBLUE + "OK from previous run".ljust(paddingResult) +
                  bcolors.ENDC)
            removeCommand = "rm " + logFileName
            subprocess.Popen(removeCommand.split(), cwd=os.getcwd())

        failed = False

    print("-" * paddingEntire)
    print(bcolors.WARNING + "Warning:"+ bcolors.ENDC + " ignored the following files specified in '.checkIgnore'" )
    for file in ignored:
        print(" ".ljust(6) + file)
    if not allPassed:
        print(bcolors.FAIL + "Failed:"+ bcolors.ENDC)
        for file in failedFiles:
            print(" ".ljust(6) + file)
    else:
        print(bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC)
        removeCommand = "rm " + standartPassedFilePath
        subprocess.Popen(removeCommand.split(), cwd=os.getcwd())

    print("-" * paddingEntire)


    savePassed(passedFiles)

if __name__ == "__main__":
    main()
