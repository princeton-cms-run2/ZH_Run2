
import os
import sys

year=str(sys.argv[1])

dataset=str(sys.argv[2])
nickName=str(sys.argv[3])

islocal=str(sys.argv[4])

syst=str(sys.argv[5])

btag=str(sys.argv[6])

subrange=str(sys.argv[7])

sign=str(sys.argv[8])

if sign=='' : sign== 'OS'
#if sign=='SS' : 
#    btag== 'no'
    #if 'data' not in dataset : nickName='VR'




#afout='root://cmseos.fnal.gov//store/user/alkaloge/CHANNEL/nAODv7/out_TAG/YEAR/$line'

command="python makeAllPlotsZHCondorWithSyst.py -f {2:s}_{0:s}_ZH_pow_noL.txt -a ZH -s {7:s} --MConly  -y {0:s}  -r no -w 16 -j {1:s} -e pow_noL -i {4:s} -t {3:s} -b {5:s} -x {6:s}".format(str(year), syst, dataset, nickName, islocal, btag, subrange,sign)

os.system(command)

print command

if subrange == "0" :
    command="xrdcp testFile.root root://cmseos.fnal.gov//store/user/alkaloge/ZH/nAODv7/out_pow_noL/{0:s}_{6:s}/{2:s}_{0:s}_sys{1:s}.root".format(str(year), syst, dataset, nickName, islocal, btag,sign)
else : 
    command="xrdcp testFile.root root://cmseos.fnal.gov//store/user/alkaloge/ZH/nAODv7/out_pow_noL/{0:s}_{7:s}/{2:s}_{0:s}_sys{1:s}_{6:s}.root".format(str(year), syst, dataset, nickName, islocal, btag, subrange,sign)

print command
os.system(command)

