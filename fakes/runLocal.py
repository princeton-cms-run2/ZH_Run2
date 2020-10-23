
import os
import sys

year=str(sys.argv[1])

dataset=str(sys.argv[2])
nickName=str(sys.argv[3])

islocal=str(sys.argv[4])

sys=str(sys.argv[5])


#python makeFakeRateHistosCondornoL.py -s ZH -y 2016  -f ZZTo4L_2016_Fakes.txt -r SS -i yes -t ZZ

#command="python makeFakeRateHistosCondornoL.py  -f {2:s}_{0:s}.txt -s ZH -r SS  -y {0:s}  -i {4:s} -t {3:s}  ; mv FakeRates_test.root {2:s}_{0:s}_sys{1:s}.root".format(str(year), sys, dataset, nickName, islocal)
command="python makeFakeRateHistosCondornoL.py  -f {2:s}_{0:s}.txt -s ZH -r SS  -y {0:s}  -i {4:s} -t {3:s}  ; xrdcp FakeRates_test.root root://cmseos.fnal.gov//store/user/alkaloge/Fakes/nAODv7/out_noL/{0:s}/{2:s}_{0:s}_sys{1:s}.root".format(str(year), sys, dataset, nickName, islocal)
print command
os.system(command)

