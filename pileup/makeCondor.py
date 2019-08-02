def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    defDS = '/VBFHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM '
    parser.add_argument("--dataSet",default=defDS,help="Data set name.") 
    parser.add_argument("--nickName",default='MCpileup',help="Data set nick name.") 
    parser.add_argument("-m","--mode",default='anaXRD',help="Mode (script to run).")
    return parser.parse_args()

def beginBatchScript(baseFileName) :
    outLines = ['#!/bin/tcsh\n']
    outLines.append("source /cvmfs/cms.cern.ch/cmsset_default.csh\n")
    outLines.append("setenv SCRAM_ARCH slc6_amd64_gcc700\n")
    outLines.append("eval `scramv1 project CMSSW CMSSW_10_2_9`\n")
    outLines.append("cd CMSSW_10_2_9/src/\n")
    outLines.append("eval `scramv1 runtime -csh`\n")
    outLines.append("echo ${_CONDOR_SCRATCH_DIR}\n")
    outLines.append("cd ${_CONDOR_SCRATCH_DIR}\n")
    return outLines

def getFileName(line) :
    tmp = line.split()[0].strip(',')
    fileName = tmp.strip()
    return fileName

import os

args = getArgs()

# sample query 
# dasgoclient --query="file dataset=/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8*/*/NANOAOD*" --limit=0   
query = '"file dataset={0:s}"'.format(args.dataSet)
command = "dasgoclient --query={0:s} --limit=0 > fileList.txt".format(query)
print("Running in {0:s} mode.  Command={1:s}".format(args.mode,command))
os.system(command)
    
files = open('fileList.txt','r').readlines()
if len(files) < 1 :
    print("***In makeCondor.py: Empty fileList.txt")
    exit()

scriptList = [] 
for nFile, file in enumerate(files) :
    print("nFile={0:d} file[:80]={1:s}".format(nFile,file[:80]))

    scriptName = "{0:s}_{1:03d}.csh".format(args.nickName,nFile+1)
    print("scriptName={0:s}".format(scriptName))
    outLines = beginBatchScript(scriptName)
    fileName = getFileName(file)

    outFileName = "{0:s}_{1:03d}.root".format(args.nickName,nFile+1)
    outLines.append("xrdcp root://cms-xrd-global.cern.ch/{0:s} inFile.root\n".format(fileName)) 
    outLines.append("python makePileUpHisto.py -f inFile.root -o {0:s}\n".format(outFileName))
    outLines.append("mv inFile.csv {0:s}\n".format(outFileName.replace(".root",".csv")))
    outLines.append("rm inFile.root\n")
    outLines.append("rm *.pyc\nrm *.so\nrm *.pcm\nrm *cc.d\n")
    
    print("Writing out file = {0:s}".format(scriptName))
    open(scriptName,'w').writelines(outLines)
    scriptList.append(scriptName)
            

# now that .csh files have been generated make a list of corresponding .jdl files

dir = '/uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/pileup/'
funcsDir = '/uscms_data/d3/alkaloge/ZH/CMSSW_10_2_9/src/funcs/'

for file in scriptList :
    base = file[:-4] 
    outLines = ['universe = vanilla\n']
    outLines.append('Executable = {0:s}\n'.format(file))
    outLines.append('Output = {0:s}.out\n'.format(base))
    outLines.append('Error = {0:s}.err\n'.format(base))
    outLines.append('Log = {0:s}.log\n'.format(base))
    outLines.append('transfer_input_files = {0:s}makePileUpHisto.py, {0:s}data_pileup_2017.root,'.format(dir))
    outLines.append('{0:s}tauFun.py, {0:s}generalFunctions.py \n '.format(funcsDir))
    outLines.append('should_transfer_files = YES\n')
    outLines.append('when_to_transfer_output = ON_EXIT\n')
    outLines.append('x509userproxy = $ENV(X509_USER_PROXY)\n')
    outLines.append('Queue 1\n')
    open('{0:s}.jdl'.format(base),'w').writelines(outLines)

    




    
    
