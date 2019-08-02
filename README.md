# ZH_Run2

This is the ZH → (l+l−)(τ+τ) Analysis Code 


Structure 1 General
The analysis employs a set of Python scripts to read nanoAOD files. The current version is implemented in CMSSW 10 2 9. Plotting and other standard analysis tasks are done using pyROOT.
2 Directory Structure
Code and data are stored in the following set of subdirectories, the contents of which will be explained in turn in the following subsections. In the current version, the main directory on cmslpc-sl6 is: /uscms data/d2/marlow/CMSSW 10 2 9/src/
  /MC /SVfit /ZH /data /docs /funcs /pileup /plotting /sync

2.1 /ZH

This contains the script ZH.py which drives the analysis preselection. ZH.py imports three modules: tauFun.py, generalFunctions.py, 
and outTuple.py, which are discussed be- low. ZH.py runs over all six final state categories: e+e−eτ, e+e−μτ, e+e−ττ, μ+μ−eτ, μ+μ−μτ, 
and μ+μ−ττ (This will rise to eight when the eμ mode is added.) Surviving events are classified using the event.cat ntuple branch.

2.2 /funcs

This subdirectory holds the three Python modules that implement most of the analysis.
taufun.py contains functions that are specific to the H → ττ analysis, whereas the module generalFunctions.py implements functions and 
methods that could potentially be used in other analyses. The class outTuple.py implements the ntuple that is produced by the first stage 
of preselection. It implements the content and follows the naming conventions of the H → ττ synchronization 
TWiki (see URL: https://twiki.cern.ch/twiki/bin/ viewauth/CMS/HiggsToTauTauWorking2017#Synchronisation).

2.3 /SVfit

Tau-pairs are kinematically combined into Higgs candidates using a C++ code called FastMTT.cc, which is a faster version of a code 
called SVfit.cc. The .cc and .h files needed for this are stored in the SVfit subdirectory. The magic incantation that allows FastMTT.cc 
and related C++ modules into the Python environment can be found in the     init () function
of the outTuple.py class. Note that FastMTT is relatively slow, and is therefore run only on events that pass the preselection cuts.

2.4 /MC

This subdirectory holds utility scripts that select and and analyze the MC samples. The list of samples is found in MCsamples.csv. 
The scripts, found in the subsubdirectory ./MC/condor/ function as follows:

• makeMC.py reads the list of MC samples and produces an output shell script called runMC.csh.

• runMC.csh creates a set subdirectories corresponding to the processes being simulated. The names of these subdirectories, called process “nicknames” correspond to the initial substring of the DAS dataset name—e.g., the nickname for
/DY1JetsToLL M-50 TuneCP5 13TeV-madgraphMLM-pythia8/ is DY1JetsToLL. For each process it runs a script called makeCondor.py.

• makeCondor.py does a dasgoclient query to obtain a list of files corresponding to a MC dataset. For each file it prepares two scripts. In what follows we continue with the example of process nickname DY1JetsToLL.

• DY1JetsToLL 001.jdl is the script that is run to submit a job to condor. It determines which files get copied to the condor worker node and sets various other parameters associated with the condor job. 
In general there will many such scripts—i.e., DY1JetsToLL 002.jdl, DY1JetsToLL 003.jdl, etc.     

• DY1JetsToLL 001.csh is the batch script that runs on the condor worker node. It does an xRootD copy of the input data file and runs the ZH.py script on it. There is one .csh file for each .jdl file.

2.5 /pileup

This directory is structured in a way that is very similar to the MC directory described above. However, it processes the MC input files 
with a different script. In particular, it runs a script called makePileUpHisto.py that produces pileup histograms, which are used 
to carry out pileup re-weighting of the MC data (the 2017 files were not properly weighted). Note that the script called makeCondor.py 
that resides in this directory is similar to the script of the same name used in the MC directory, the files differ in detail and 
are not interchangeable. The main differences arise because different files are needed to implement the pileup histogram.

2.6 /data

Again, the structure here is very similar to the MC directory. In this case, the file that drives the process is called datasets.txt, 
which plays the role of MCsamples.csv. The scripts employed are

• makeData.pyreadsthelistofdatasamplesfromdatasets.txtandproducesanoutput shell script called runData.csh.

• runData.csh creates a set subdirectories corresponding to the data eras being run. The names of these eras play a role similar to that 
of the nicknames in the MC case.

• makeCondor.py does a dasgoclient query to obtain a list of files corresponding to a dataset. For each file it prepares two scripts. 
Again, the makeCondor.py script will be similar, but not identical to the makeCondor.py script in the MC directory. 
In what follows we continue with the example of a dataset named DoubleMuon2017B.

• DoubleMuon2016B 001.jdl is the script that is run to submit a job to condor. It determines which files get copied to the condor worker 
node and sets various other parameters associated with the condor job. In general there will many such scripts.  

• DoubleMuon2016B 001.csh is the batch script that runs on the condor worker node. It does an xRootD copy of the input data file and runs the ZH.py script on it. There is one .csh file for each .jdl file.

2.7 /sync

This directory is a small scale implementation of the MC and data directories. It contains a separate script called makeSyncNtuple.py 
that runs on the VBFHToTauTau signal sample for purposes of generating a synchronization ntuple for comparison to other analyses. 
A separate code is needed since the standard synchronization samples do not involve a Z boson and use significantly different τ selection cuts.

2.8 /plotting

This directory contains scripts that merge and analyze the ntuples produced in the prese- lection steps implemented in the MC and 
data directories. Here the notion of a “group” is introduced. This refers to the grouping of MC samples into categories such as “reducible,” 
“rare”, ZZ → 4l etc. At present, the merging and plotting is done in two stages

• makeHistosByGroup.py is the script that spins through the ntuples in the MC and data areas to make histograms. Some additional event selection and event weighting is done at this stage. Certain selections (e.g., whether the τ’s are opposite- or same-sign and the value of the LT cut are controlled by input argument.

• makeStack.py reads the ROOT file produced by makeHistosByGroup.py and produces stacked plots for final display.
 
