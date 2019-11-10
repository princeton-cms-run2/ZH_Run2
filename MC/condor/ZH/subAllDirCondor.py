import sys
import glob
import os
import os.path

files = glob.glob('*_2016')
#files = glob.glob('*2017*')
for file in files :
    if not os.path.isdir(file) : continue
    os.chdir('./{0:s}'.format(file))
    print("cwd={0:s}".format(os.getcwd())) 
    jdls = glob.glob('*.jdl')
    for jdl in jdls :
        ff=jdl.replace('jdl','ntup')
        #print("Command={0:s}".format(command))
        cf = os.path.isfile('{0:s}'.format(ff))
        if  cf : print 'The .root exists:', ff, ' I wont submit'
        else: 
            command = "condor_submit {0:s}".format(jdl)
            print 'sending...', ff
            os.system(command)
    os.chdir('..')
    print("cwd={0:s}".format(os.getcwd()))

