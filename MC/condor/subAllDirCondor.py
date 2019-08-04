import sys
import glob
import os

files = glob.glob('ZHTo*')
for file in files :
    if not os.path.isdir(file) : continue
    os.chdir('./{0:s}'.format(file))
    print("cwd={0:s}".format(os.getcwd())) 
    jdls = glob.glob('*.jdl')
    for jdl in jdls :
        command = "condor_submit {0:s}".format(jdl)
        print("Command={0:s}".format(command))
        os.system(command)
    os.chdir('..')
    print("cwd={0:s}".format(os.getcwd()))

