import sys
import glob
import os

files = glob.glob('ZZ4L*2018')
print("files={0:s}".format(str(files)))
for file in files :
    print("file={0:s} isDir={1}".format(file,os.path.isdir(file)))
    if not os.path.isdir(file) : continue
    os.chdir(file) 
    print("cwd={0:s}".format(os.getcwd()))
    #cmd = "python  ../hadnano2.py {0:s}.root *.ntup *.weights".format(file)
    cmd = "hadd -f -k  {0:s}.root all*.root ".format(file)
    print("cmd={0:s}".format(cmd))
    cf = os.path.isfile('{0:s}.root'.format(file))
    os.system(cmd) 
    #if not cf :  os.system(cmd) 
    #else : print '{0:s}.root is in place'.format(file)
    os.chdir('..')


