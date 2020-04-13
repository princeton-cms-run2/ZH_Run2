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
#sys.args are  sys.argv[3]= isdata, , sys.argv[1]= era, sys.argv[2]=period
jmeCorrections = createJMECorrector(sys.argv[3], str(sys.argv[1]), str(sys.argv[2]), "Total", True, "AK4PFchs", False)

fnames=["./inFile.root"]
#p=PostProcessor(".",fnames,"Jet_pt>150","",[jetmetUncertainties2016(),exampleModuleConstr()],provenance=True)
p=PostProcessor(".",fnames,"","",[jmeCorrections()],provenance=True)
p.run()
