import glob
import optparse
import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
from os.path import basename
import sys

standartPassedFilePath = "passedCheck.txt"

# parses arguments
#=====================================================================================================================
parser = optparse.OptionParser()
parser.add_option("-d" ,"--directory"       ,dest="directory"       ,action="store"     ,type="string",metavar="FILE"
                                            ,help="directory that contains header files")

parser.add_option("-s" ,"--silent"          ,dest="silent"          ,action="store_true"
                                            ,help="removes all output")

parser.add_option("-v" ,"--verbose"         ,dest="verbose"         ,action="store_true"
                                            ,help="print extra information")

parser.add_option("-f" ,"--showOnlyFailed"  ,dest="showOnlyFailed"  ,action="store_true"
                                            ,help="passed files are no longer displayed")

parser.add_option("-c" ,"--compiler"        ,dest="compiler"        ,action="store"     ,type='string'
                                            ,help="not implemented yet")

parser.add_option("-i" ,"--ignore"          ,dest="ignored"         ,action="store"     ,type='string'
                                            ,help="file that contains the names of headers that should be ignored")

parser.add_option(      "--CXX"             ,dest="CXX"             ,action="store"     ,type='string'
                                            ,help="")

parser.add_option(      "--CFLAGS"          ,dest="CFLAGS"          ,action="store"     ,type='string'
                                            ,help="")

parser.add_option(      "--clean"          ,dest="clean"           ,action="store_true"
                                            ,help="")


options,args =  parser.parse_args()
#=====================================================================================================================

#colour class for coloured output
class bcolors:
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'      # Used for checks from last iteration
    OKGREEN   = '\033[92m'      # Used for newly passed
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'      # Used for error
    ENDC      = '\033[0m'       # Used to reset colour
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'

#loads and returns list of files that should be ignored when testing
def loadIgnored(ignoredFileName=".checkIgnore"):
    ignored = []
    if os.path.isfile(ignoredFileName):
        ignoredFile = open(ignoredFileName)
        ignored = [ x.strip('\t').strip('\n') for x in ignoredFile.readlines()]
        ignoredFile.close()

    return ignored

#load files in src folder and remove ignored from list
def createFileList(ignored,srcFolder):
    if srcFolder == None:
        srcFolder = os.getcwd()

    allFiles=glob.glob(srcFolder + "/*.h")
    cleanedFiles = [x for x in allFiles if basename(x) not in ignored]
    if len(cleanedFiles) == 0:
        print(bcolors.FAIL + "Error: " + bcolors.ENDC + "no files found in '" + srcFolder +"'")
        sys.exit(-2)

    return cleanedFiles

#util function for grouping output into rows
def grouped(iterable, n):
    return [zip(*[iter(iterable)]*n)]

#saves file name of files that successfully compiled as txt
def savePassed(passedFiles,filename=standartPassedFilePath):
    savefile = open("passedCheck.txt", 'w+')
    for passed in passedFiles:
        savefile.write(passed + "\n")
    savefile.close()

#loads txt file in which previously passed files are saved
def loadPassed(passedFileName=standartPassedFilePath):
    passed = []
    if os.path.isfile(passedFileName):
        file = open(passedFileName, 'r')
        passed = [ x.strip('\t').strip('\n') for x in file.readlines()]
        file.close()

    return passed

#prints separator line if not silent
def printSeparator():
    if not options.silent:
        print("-" * paddingEntire)

#paddings for results
paddingResult = 40
paddingName = 40
paddingEntire= paddingResult + paddingName

def evalOptions():
    ignored = []
    if options.ignored:
        ignored=loadIgnored(options.ignored)

    dir = None
    if options.directory:
        dir = options.directory

    return ignored, dir


def run():
    passedFiles = loadPassed()
    failedFiles = []
    showOnlyFailed = options.showOnlyFailed
    allPassed = True

    ignored, srcFolder = evalOptions()

    if options.verbose:
        print("Checking headers in: "+ options.directory)

    for file in createFileList(ignored, srcFolder) :
        name = basename(file)
        CXX="-std=c++11 -DgFortran -DCDO" 
        compilerCommand = "g++  -o hc_"+ name + ".gch "+ CXX + " "
        logFileName = "hc_" +name + ".log"

        if name not in passedFiles:
            log = open(logFileName,'wb+')
            command = compilerCommand + file
            process = subprocess.Popen(command.split(), cwd=os.getcwd(),stdout=log,stderr=log)
            output, error = process.communicate()

            if (process.returncode != 0):
                #show file failed
                if not options.silent:
                    print((name + ": "   ).ljust(paddingName)
                          + bcolors.FAIL + ("FAIL   " 
                          + bcolors.ENDC + str(process.returncode)).ljust(paddingResult))
                failed =True
                allPassed = False
                failedFiles.append(name)
            else:
                #show file passed
                if not showOnlyFailed or options.verbose:
                    if not options.silent:
                        print((name + ": "   ).ljust(paddingName)
                              + bcolors.OKGREEN + "OK".ljust(paddingResult) +
                              bcolors.ENDC)

                #delete log file if no error happend
                removeCommand = "rm " + logFileName
                subprocess.Popen(removeCommand.split(), cwd=os.getcwd())

                passedFiles.append(name)
                savePassed(passedFiles)
        else:
            #show file already checked
            if not options.silent and not showOnlyFailed:
                print((name + ": "   ).ljust(paddingName)
                      + bcolors.OKBLUE + "OK from previous run".ljust(paddingResult) +
                      bcolors.ENDC)

        #reset failed marker for next iteration
        failed = False

    printSeparator()

    if len(ignored) > 0 and not options.silent:
        print(bcolors.WARNING + "Warning:"+ bcolors.ENDC + " ignored the following files specified in '.checkIgnore'" )
        for file in ignored:
            print(" ".ljust(4) + file)

    if not allPassed and not options.silent:
        print(bcolors.FAIL + "Failed:"+ bcolors.ENDC)
        preFormatFailedFiles = [failedFiles[i:i + 3] for i in range(0, len(failedFiles), 3)]
        for row in preFormatFailedFiles:
            outStr = "".ljust(4)
            for fileName in row:
                outStr += fileName.ljust(25)
            print(outStr)
    else:
        if not options.silent:
            print(bcolors.OKGREEN + "SUCCESS" + bcolors.ENDC)
        removeCommand = "rm " + standartPassedFilePath
        subprocess.Popen(removeCommand.split(), cwd=os.getcwd())

    printSeparator()
    savePassed(passedFiles)

    if not allPassed:
        return -1
    return 0


def main():
    if options.clean:
        removeCommand = "rm -f" + " hc_*.gch hc_*.log passedCheck.txt"
        subprocess.Popen(removeCommand, shell=True, cwd=(os.getcwd()+"/"))
        return 0
    else:
        return run()

if __name__ == "__main__":
    instanceID = main()
    sys.exit(instanceID)
