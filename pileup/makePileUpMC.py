
# generate a runMC.csh script that creates the .csh and .jdl files
# to process MC data 

import os

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--inFile",default='MCsamples_2017.csv',help="Input file name.") 
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    return parser.parse_args()

args = getArgs() 
outLines = []
era=str(args.year)
cwd = os.getcwd()
for line in open(args.inFile,'r').readlines() :
    nickname = line.split(',')[0]
    #print("\n\n\n line.split(',')={0:s}".format(str(line.split(','))))
    dataset = line.split(',')[6].replace(' ','_').strip()
    if len(dataset) < 2 : continue
    #print("\n***line.split()={0:s}".format(str(line.split(','))))
    print("nickname={0:s} \n dataset={1:s}".format(nickname,dataset))

    mode = 'anaXRD'
    
    outLines.append("mkdir {0:s}_{1:s}\ncd {0:s}_{1:s}\n".format(nickname,era))
    outLines.append("python ../makeCondor.py --dataSet {0:s} --nickName {1:s} --mode {2:s} -y {3:s}\n".format(dataset,nickname, mode, args.year))
    outLines.append("cd {0:s}\n".format(cwd))

fOut=("runMC_{0:s}.csh").format(args.year) 
open(fOut,'w').writelines(outLines)



    
    
