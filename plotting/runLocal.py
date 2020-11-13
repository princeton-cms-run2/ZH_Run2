
import os
import sys

year=str(sys.argv[1])

dataset=str(sys.argv[2])
nickName=str(sys.argv[3])

islocal=str(sys.argv[4])

sys=str(sys.argv[5])

#afout='root://cmseos.fnal.gov//store/user/alkaloge/CHANNEL/nAODv7/out_TAG/YEAR/$line'

command="python makeAllPlotsZHCondorWithSyst.py -f {2:s}_{0:s}_ZH_pow_noL.txt -a ZH -s OS --MConly  -y {0:s}  -r no -w 16 -b 16  -j {1:s} -e pow_noL -i {4:s} -t {3:s}; xrdcp testFile.root root://cmseos.fnal.gov//store/user/alkaloge/ZH/nAODv7/out_pow_noL/{0:s}/{2:s}_{0:s}_sys{1:s}.root".format(str(year), sys, dataset, nickName, islocal)
print command
os.system(command)
