#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
##soon to be deprecated
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
##new way of using jme uncertainty
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *

#from  exampleModule import *

##Function parameters
##(isMC=True, dataYear=2016, runPeriod="B", jesUncert="Total", redojec=False, jetType = "AK4PFchs", noGroom=False)
##All other parameters will be set in the helper module
#sys.args are  sys.argv[1]= isdata, , sys.argv[2]= era, sys.argv[3]=period
if sys.argv[1] =='False' : jmeCorrections = createJMECorrector(False, str(sys.argv[2]), str(sys.argv[3]), "Total", True, "AK4PFchs", False)
if sys.argv[1] =='True' :  jmeCorrections = createJMECorrector(True, str(sys.argv[2]), str(sys.argv[3]), "Total", True, "AK4PFchs", False)

fnames=["./inFile.root"]
#p=PostProcessor(".",fnames,"Jet_pt>150","",[jetmetUncertainties2016(),exampleModuleConstr()],provenance=True)
#p=PostProcessor(".",fnames,"Jet_pt>250 && abs(Jet_eta)<4.7001","",[jmeCorrections()],provenance=True)
p=PostProcessor(".",fnames,"","",[jmeCorrections()],provenance=True)
p.run()
