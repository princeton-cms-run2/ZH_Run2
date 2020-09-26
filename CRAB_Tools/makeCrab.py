
import os

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default=0,type=int,help="Print level.")
    defDS = '/VBFHToTauTau_M125_13TeV_powheg_pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM '
    parser.add_argument("--dataSet",default=defDS,help="Data set name.") 
    parser.add_argument("--nickName",default='MCpileup',help="Data set nick name.") 
    parser.add_argument("-m","--mode",default='anaXRD',help="Mode (script to run).")
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-c","--concatenate",default=1,type=int,help="On how many files to run on each job")
    parser.add_argument("-s","--selection",default='ZH',type=str,help="select ZH or AZH")
    parser.add_argument("-j","--doSystematics",default='yes',type=str,help="do JME systematics")
    return parser.parse_args()

def beginBatchScript(baseFileName, Systematics) :
    outLines = ['#!/bin/sh\n']
    outLines.append("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
    outLines.append("export SCRAM_ARCH=slc7_amd64_gcc820\n")
    outLines.append("workdir=`pwd`\n")
    outLines.append("cmsrel CMSSW_10_6_4\n")
    #outLines.append("eval `scramv1 project CMSSW CMSSW_10_6_4`\n")
    outLines.append("cd CMSSW_10_6_4/src\n")
    outLines.append("eval `scramv1 runtime -sh`\n")
    outLines.append("cmsenv\n")
    #outLines.append("git clone https://github.com/cms-tau-pog/TauIDSFs TauPOG/TauIDSFs\n")
    outLines.append("cp ${workdir}/* .\n")
    outLines.append("tar -zxvf taupog.tar.gz\n")
    outLines.append("scram b -j 4\n")
    if Systematics :
        outLines.append("git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools\n")
        outLines.append("cp branchselection.py PhysicsTools/NanoAODTools/python/postprocessing/framework/.\n")
        outLines.append("cp keep_and_drop.txt PhysicsTools/NanoAODTools/python/postprocessing/framework/.\n") 
        outLines.append("cd PhysicsTools/NanoAODTools\n")
        outLines.append("scram b -j 4\n")
    outLines.append("cd ${workdir}/CMSSW_10_6_4/src/\n")
    outLines.append("echo this is the working dir ${workdir}\n")
    #outLines.append("python -c '"'import PSet; print "'"\n"'".join(list(PSet.process.source.fileNames))'"'\n")
    return outLines

def getFileName(line) :
    tmp = line.split()[0].strip(',')
    fileName = tmp.strip()
    return fileName


args = getArgs()
era = str(args.year)
doJME  = args.doSystematics.lower() == 'true' or args.doSystematics.lower() == 'yes' or args.doSystematics == '1'

runDir=os.getcwd()
period="B"
if 'Run2016' in args.dataSet or 'Run2017' in args.dataSet or 'Run2018' in args.dataSet: 
    poss = args.dataSet.find("Run")
    period = args.dataSet[int(poss)+7:int(poss)+8]
    print 'will set up', poss, period

  

# sample query 
# dasgoclient --query="file dataset=/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8*/*/NANOAOD*" --limit=0   

query = '"file dataset={0:s}"'.format(args.dataSet)

if "USER" in str(args.dataSet) : query = '"file dataset={0:s}"'.format(args.dataSet+" instance=prod/phys03")

command = "dasgoclient --query={0:s} --limit=0  > fileList.txt".format(query)
print("Running in {0:s} mode.  Command={1:s}".format(args.mode,command))
os.system(command)
    
files = open('fileList.txt','r').readlines()
if len(files) < 1 :
    print("***In makeCondor.py: Empty fileList.txt")
    exit()

scriptList = [] 
outList = [] 
file=[]
dataset=[]

mjobs=args.concatenate


for nFiles, file in enumerate(files) :
    fileName=getFileName(file)
    dataset.append(fileName)

dirr='/uscms_data/d3/alkaloge/ZH/CMSSW_10_6_4/src'
dirMC = dirr+"/MC/"
dirZH = dirr+"/ZH/"
dirData = dirr+"/data/"
funcsDir = dirr+"/funcs/"
SVFitDir = dirr+"/SVFit/"
toolsDir = dirr+"/tools/"

counter=0

executable = str(args.selection)
if 'ZH' in str(args.selection) : executable='ZH'

ptBins=[10,20,30,40,50,75,100,150,200,5000]
if not doJME : ptBins=[1000]

doWeights=2

#mjobs = len(dataset) * (len(ptBins)-1)

if len(ptBins) > 1 : mjobs = 1

for nFile in range(0, len(dataset),mjobs) :

    for ipT in range(len(ptBins)-1):

	pt = ptBins[ipT]
	ptN = ptBins[ipT+1]
	if ipT >0 : doWeights=0

        
	#print("nFile={0:d} file[:80]={1:s}".format(nFile,file[:80]))
	#scriptName = "{0:s}_{1:03d}_{2:s}of{3:s}.sh".format(args.nickName,nFile+1, str(ipT+1), str(len(ptBins)-1))
	scriptName = "{0:s}_{1:03d}_{2:s}of{3:s}.sh".format(args.nickName,nFile+1, str(ipT+1), str(len(ptBins)-1))
	print("scriptName={0:s}".format(scriptName))
	outLines = beginBatchScript(scriptName,doJME)

	#outLines.append("tar -zxvf SFs.tar.gz\n")
	outLines.append("cp MCsamples_*csv MCsamples.csv\n")
	outLines.append("cp cuts_{0:s}.yaml cuts.yaml\n".format(args.selection))

	fileName = getFileName(file)
	maxx = mjobs
	if counter+mjobs > len(dataset) : 
	    #print 'should include', nFile, -nFile-mjobs + len(dataset)+1, 'from ', len(dataset), counter, maxx
	    maxx = len(dataset)-counter
	    #for j in range(0,mjobs) :
	for j in range(0,mjobs) :
	    #print 'shoud see', nFile+maxx, maxx, len(dataset)
            if len(dataset) == 1 :  fileloop=dataset[nFile:nFile+1][0]
            else :  fileloop=dataset[nFile:nFile+maxx][j-1]
            #fileloop=dataset[nFile:nFile+maxx][j]
	    if 'lpcsusyhiggs' not in fileName : outLines.append("xrdcp root://cms-xrd-global.cern.ch/{0:s} inFile.root\n".format(fileloop)) 
	    else : outLines.append("xrdcp root://cmsxrootd.fnal.gov/{0:s} inFile.root\n".format(fileloop)) 

	    outFileName = "{0:s}_{1:03d}.root".format(args.nickName,nFile+j)
 	    infile = "inFile.root"

            
   	    if doJME : 

		outLines.append("sed -i 's/MIN/{0:s}/g' make_jme.py  \n".format(str(pt)))
		outLines.append("sed -i 's/MAX/{0:s}/g'  make_jme.py \n".format(str(ptN)))


		if ipT== 0 : outLines.append("python {6:s}.py -f {4:s} -o {0:s}_{8:s}of{9:s} --nickName {1:s} -y {2:s} -s {3:s} -w {7:s} -j {5:s}\n".format(outFileName,args.nickName, args.year, args.selection,infile, args.doSystematics, executable, str(doWeights),str(ipT+1), str(len(ptBins)-1)))

		if 'Run2016' in fileloop or 'Run2017' in fileloop or 'Run2018' in fileloop : 
		    outLines.append("python make_jme.py False {0:s} {1:s}\n".format(str(args.year), str(period)))
		else : 
		    outLines.append("python make_jme.py True {0:s} {1:s}\n".format(str(args.year), str(period)))

		infile = "inFile_Skim.root"


		outLines.append("python {6:s}.py -f {4:s} -o {0:s}_{7:s}of{8:s} --nickName {1:s} -y {2:s} -s {3:s} -w 0 -j {5:s}\n".format(outFileName,args.nickName, args.year, args.selection,infile, args.doSystematics, executable, str(ipT+1), str(len(ptBins)-1)))


	    else : 
		outLines.append("python {6:s}.py -f {4:s} -o {0:s} --nickName {1:s} -y {2:s} -s {3:s} -w 1 -j {5:s}\n".format(outFileName,args.nickName, args.year, args.selection,infile, args.doSystematics, executable))
	
	    outLines.append("rm inFile*.root\n")

        if ipT == 0 :	outLines.append("hadd -f -k all_{0:s}_{1:03d}_{2:s}of{3:s}.root *ntup* *weights*\n".format(args.nickName,nFile+1,str(ipT+1), str(len(ptBins)-1)))
        else :	outLines.append("hadd -f -k all_{0:s}_{1:03d}_{2:s}of{3:s}.root *ntup* \n".format(args.nickName,nFile+1,str(ipT+1), str(len(ptBins)-1)))
	outLines.append("rm *.pyc\nrm *.so\nrm *.pcm\nrm *cc.d\n")
	outLines.append("rm *ntup* *.so\nrm *.pcm\nrm *cc.d\n")
	outLines.append("cp  all*root ${workdir}/.\n")
        if ipT == 0 : 
            outLines.append("cp  *weights* {0:s}.weights; cp {0:s}.weights ../../. \n".format(args.nickName))
        #outLines.append("cmsRun -j FrameworkJobReport.xml -p pset.py\n")
        outLines.append("python -c \"import PSet; print \'\\n\'.join(list(PSet.process.source.fileNames))\" ")
	print("Writing out file = {0:s}".format(scriptName))
	open(scriptName,'w').writelines(outLines)
	scriptList.append(scriptName)
        outList.append('all_{0:s}_{1:03d}_{2:s}of{3:s}.root'.format(args.nickName,nFile+1,str(ipT+1), str(len(ptBins)-1)))
    counter += mjobs
            

# now that .csh files have been generated make a list of corresponding .jdl files





for ifile, file, in enumerate(scriptList) :
    base = file[:-4] 
    ff = outList[ifile].replace('all_','')
    ff = ff.replace('.root', '')
    outLines = ['from CRABClient.UserUtilities import config\n']
    outLines.append('from WMCore.Configuration import Configuration\n')
    outLines.append( 'config = config()\n')
    outLines.append('config.General.requestName = \'ntuples_{0:s}\'\n'.format(ff))
    outLines.append('config.General.workArea = \'../../Crab_projects_{0:s}\'\n'.format(args.year))
    outLines.append('config.General.transferOutputs = True\n')
    outLines.append('config.General.transferLogs = True\n')
    outLines.append('config.JobType.pluginName = \'PrivateMC\'\n')
    outLines.append('config.JobType.psetName = \'pset.py\'\n')
    outLines.append('config.JobType.scriptExe = \'{0:s}/../../ZH/{1:s}_{2:s}/{3:s}\' \n'.format(os.getcwd(),args.nickName,args.year,file))




    outLines.append('config.JobType.inputFiles =[ \'{0:s}{1:s}.py\', '.format(dirZH,executable))
    outLines.append('\'{0:s}MC_{1:s}.root\', \'{0:s}data_pileup_{1:s}.root\', \'{0:s}MCsamples_{1:s}.csv\', \'{0:s}cuts_{2:s}.yaml\', '.format(dirMC,args.year, args.selection, executable))
    outLines.append('\'{0:s}tauFun2.py\', \'{0:s}generalFunctions.py\', \'{0:s}outTuple.py\', \'{0:s}Weights.py\','.format(funcsDir))
    outLines.append('\'{0:s}FastMTT.h\', \'{0:s}MeasuredTauLepton.h\', \'{0:s}svFitAuxFunctions.h\','.format(SVFitDir)) 
    outLines.append('\'{0:s}FastMTT.cc\', \'{0:s}MeasuredTauLepton.cc\', \'{0:s}svFitAuxFunctions.cc\','.format(SVFitDir))
    outLines.append('\'{0:s}make_jme.py\', \'{0:s}branchselection.py\', \'{0:s}keep_and_drop.txt\', \'{0:s}taupog.tar.gz\', \'{0:s}pset.py\', \'{0:s}FrameworkJobReport.xml\']\n'.format(toolsDir))

    if ifile == 0 :    outLines.append('config.JobType.outputFiles = [\'{0:s}\', \'{1:s}.weights\']\n'.format(outList[ifile], args.nickName))
    else :    outLines.append('config.JobType.outputFiles = [\'{0:s}\']\n'.format(outList[ifile]))
    outLines.append('config.JobType.allowUndistributedCMSSW = True\n')
    outLines.append('config.JobType.maxJobRuntimeMin = 3000\n')
    outLines.append('config.Data.inputDBS = \'global\'\n')
    outLines.append('config.Data.splitting = \'EventBased\'\n')
    outLines.append('config.Data.unitsPerJob = 1\n')
    outLines.append('config.Data.totalUnits = 1\n')
    outLines.append('config.Data.publication = False\n')
    outLines.append('config.Data.outputDatasetTag = \'{0:s}_{1:s}\'\n'.format(str(args.nickName), str(args.year)))
    #outLines.append('config.Data.outputDatasetTag = \'/store/group/lpcsusyhiggs/ntuples/nAODv7/ZH/{0:s}\'\n'.format(str(args.year)))

    outLines.append('config.Data.outLFNDirBase = \'/store/group/lpcsusyhiggs/ntuples/nAODv7/ZH/\'\n')
    outLines.append('config.section_(\'Site\')\n')
    outLines.append('config.Site.storageSite = \'T3_US_FNALLPC\'\n')

    open('crab_{0:s}.py'.format(ff),'w').writelines(outLines)


    
