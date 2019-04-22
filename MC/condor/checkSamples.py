import sys
import glob
import os

files = glob.glob('*')
print("files={0:s}".format(str(files)))
for file in files :
    if not os.path.isdir(file) : continue
    os.chdir(file) 
    f_ntup = glob.glob('*.ntup')
    f_root = glob.glob('*.root')
    print("In {0:16s} Nntup={1:2d} Nroot={2:2d}".format(file,len(f_ntup),len(f_root)))
    os.chdir('..')


