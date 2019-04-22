import sys
import glob
import os

fileSpec = sys.argv[1]
files = glob.glob(fileSpec)
for file in files :
    if file[-4:] == '.jdl' :
        command = "condor_submit {0:s}".format(file)
        print("Command={0:s}".format(command))
        os.system(command)
    else :
        print("Invalid file={0:s}".format(file))


        
