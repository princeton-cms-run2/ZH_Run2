#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc820
eval `scramv1 project CMSSW CMSSW_10_6_4`
cd CMSSW_10_6_4/src
eval `scramv1 runtime -sh`
echo ${_CONDOR_SCRATCH_DIR}
#cd ${_CONDOR_SCRATCH_DIR}

tar -xvf ${_CONDOR_SCRATCH_DIR}/tools.tar.gz 
cp ${_CONDOR_SCRATCH_DIR}/* .

rm -fr TauPOG
git clone https://github.com/cms-tau-pog/TauIDSFs TauPOG/TauIDSFs

eval `scramv1 runtime -sh`
scram b -j 8

xrdcp root://cmseos.fnal.gov//store/user/alkaloge/CHANNEL/nAODv7/YEAR/FILEIN_YEAR/FILEIN_YEAR.root . 



#xrdcp testCHANNEL_TAG.root root://cmseos.fnal.gov//store/user/alkaloge/CHANNEL/nAODv7/out_TAG/YEAR/FILEIN_YEAR.root

python runLocal.py YEAR FILEIN NICKNAME 0

echo done!

#ls NICKNAME*.root > files
#cat files
#sed -i 's/NICKNAME_YEAR.root/d' files

#echo "again....."

#cat files
#while read line
#do

#xrdcp $line root://cmseos.fnal.gov//store/user/alkaloge/CHANNEL/nAODv7/out_TAG/YEAR/$line

#done<files
