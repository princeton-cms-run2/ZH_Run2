
import os
import sys

year=str(sys.argv[1])

dataset=str(sys.argv[2])
nickName=str(sys.argv[3])

islocal=str(sys.argv[4])

'''
sysT = ["Central"]

sysall = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']

upS=sysall
downS=sysall

for i, sys in enumerate(sysall) :
    sysT.append(sys+'Up')
    sysT.append(sys+'Down')


#sysT = ["scale_eUp"]

#sysT = ["Central", 'scale_eUp']
#sysT = ["Central"]

if 'Run' in dataset or 'data' in dataset : sysT = ["Central"]
#sysT = ["Central"]

#for i, sys in enumerate(sysT) :
'''
sys=str(sys.argv[5])


command="python makeAllPlotsZHCondorWithSyst.py -f {2:s}_{0:s}_ZH_pow_noL.txt -a ZH -s OS --MConly  -y {0:s}  -r no -w 16 -b 16  -j {1:s} -e pow_noL -i {4:s} -t {3:s}; mv testFile.root {2:s}_{0:s}_sys{1:s}.root".format(str(year), sys, dataset, nickName, islocal)
print command
os.system(command)

