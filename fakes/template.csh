#!/bin/tcsh
source /cvmfs/cms.cern.ch/cmsset_default.csh
setenv SCRAM_ARCH slc6_amd64_gcc700
eval `scramv1 project CMSSW CMSSW_10_2_16_patch1`
cd CMSSW_10_2_16_patch1/src
eval `scramv1 runtime -csh`
echo ${_CONDOR_SCRATCH_DIR}
#cd ${_CONDOR_SCRATCH_DIR}

tar -xvf ${_CONDOR_SCRATCH_DIR}/tools.tar.gz 
cp ${_CONDOR_SCRATCH_DIR}/* .

xrdcp root://cmseos.fnal.gov//store/user/alkaloge/ZH/YEAR/FILEIN_YEAR/FILEIN_YEAR.root . 

python makeFakeRateHistosCondor.py -s ZH -y YEAR  -f FILEIN_YEAR_CHANNEL.txt -r SS


xrdcp FakeRates_test.root root://cmseos.fnal.gov//store/user/alkaloge/Fakes/out/YEAR/FILEIN_YEAR.root
