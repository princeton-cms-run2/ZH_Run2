import os
import os.path
import sys
import fileinput
import subprocess

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-f","--inFileName",default='file.csv',type=str,help="Data taking period, 2016, 2017 or 2018")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)

eospath='/eos/uscms/store/user/alkaloge/'

for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    ds = vals[0]
    if '#' in ds : continue
    command = "cp template.csh condor_{0:s}_{1:s}_{2:s}.csh".format(ds,era,sel)
    os.system(command)
    command = "cp template.jdl condor_{0:s}_{1:s}_{2:s}.jdl".format(ds,era,sel)
    os.system(command)
    
    
   

    subprocess.call(["sed -i  's/FILEIN/{0:s}/g' condor_{0:s}_{1:s}_{2:s}.csh".format(ds,era,sel)], shell=True)
    subprocess.call(["sed -i  's/FILEIN/{0:s}/g' condor_{0:s}_{1:s}_{2:s}.jdl".format(ds,era,sel)], shell=True)

    subprocess.call(["sed -i  's/YEAR/{1:s}/g' condor_{0:s}_{1:s}_{2:s}.csh".format(ds,era,sel)], shell=True)
    subprocess.call(["sed -i  's/YEAR/{1:s}/g' condor_{0:s}_{1:s}_{2:s}.jdl".format(ds,era,sel)], shell=True)

    subprocess.call(["sed -i  's/CHANNEL/{2:s}/g' condor_{0:s}_{1:s}_{2:s}.csh".format(ds,era,sel)], shell=True)
    subprocess.call(["sed -i  's/CHANNEL/{2:s}/g' condor_{0:s}_{1:s}_{2:s}.jdl".format(ds,era,sel)], shell=True)

    #command = "sed -i "'"s/FILEIN/{0:s}/g"'" condor_{0:s}_{1:s}_{2:s}.csh".format(ds,era,sel)

    #outLines = []
    #outLines.append("{0:s}\n".format(ds)
    open(ds+'_'+era+'_'+sel+'.txt','w').writelines(line)


    command = "chmod 777 condor_{0:s}_{1:s}_{2:s}.jdl".format(ds,era,sel)
    os.system(command)
    command = "chmod 777 {0:s}_{1:s}_{2:s}.txt".format(ds,era,sel)
    os.system(command)

    cf = os.path.isfile('{0:s}/{1:s}/out/{2:s}/{3:s}_{2:s}.root'.format(eospath,sel,era,ds))

    if cf :
        print 'looks like you have it', ds, era, sel
    else :
        command = "condor_submit condor_{0:s}_{1:s}_{2:s}.jdl".format(ds,era,sel)
        #os.system(command)
        print command
        

