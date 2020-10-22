import os
import os.path
import sys

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-m","--merge",default='ZH',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-e","--extraTag",default='pow_noL',type=str,help="pow_noL or pow_wL")
    parser.add_argument("-o","--overideSyst",default='',type=str,help="overide sys")
    return parser.parse_args()


args = getArgs()
era = str(args.year)

scaleSyst = ["Central"]

scale = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']


for i, sys in enumerate(scale) :
    scaleSyst.append(sys+'Up')
    scaleSyst.append(sys+'Down')

jes=['jesAbsolute', 'jesAbsolute_{0:s}'.format(str(era)), 'jesBBEC1', 'jesBBEC1_{0:s}'.format(str(era)), 'jesEC2', 'jesEC2_{0:s}'.format(str(era)), 'jesFlavorQCD', 'jesHF', 'jesHF_{0:s}'.format(str(era)), 'jesRelativeBal', 'jesRelativeSample_{0:s}'.format(str(era)), 'jesHEMIssue', 'jesTotal', 'jer']

jesSyst=[]
for i, sys in enumerate(jes) :
    jesSyst.append(sys+'Up')
    jesSyst.append(sys+'Down')

otherS=['NLOEWK','PreFire','tauideff_pt20to25', 'tauideff_pt25to30', 'tauideff_pt30to35', 'tauideff_pt35to40', 'tauideff_ptgt40', 'scale_met_unclustered'] 
OtherSyst=[]
for i, sys in enumerate(otherS) :
    OtherSyst.append(sys+'Up')
    OtherSyst.append(sys+'Down')

sysall = scaleSyst + jesSyst + OtherSyst


if str(args.overideSyst) != '' : sysall=[args.overideSyst]

sign='SS'

ver='noL'
gen='pow'

eosdir='/eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/'

for sys in sysall : 

    fout ='FakeRates_{0:s}_SS_sys{1:s}.root'.format(era,sys)

    if str(args.merge.lower())=='1' or str(args.merge.lower()) == 'yes': 

	#amkdir /eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/${year}/ZZpow
	#mv /eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/${year}/ZZTo4L_ext* /eos/uscms/store/user/alkaloge/Fakes/nAODv7/out_noL/${year}/ZZpow
        if sys == 'Central' : 
	    command="hadd -f {0:s} {3:s}/{1:s}/*_sys{2:s}.root".format(fout, era,sys,eosdir)
	#command="mkdir -p  {3:s}/{1:s}/data_{1:s}; mv  {3:s}/{1:s}/data*root {3:s}/{1:s}/data_{1:s}/. ; *_sys{2:s}.root".format(fout, era,sys,eosdir)
        #os.system(command)
	#command="hadd -f {0:s} {3:s}/{1:s}/*_sys{2:s}.root {3:s}/{1:s}/data_{1:s}/data_sys{2:s}".format(fout, era,sys,eosdir)
        else : 
	    command="hadd -f {0:s} {3:s}/{1:s}/*_sys{2:s}.root {3:s}/{1:s}/data_{1:s}_sysCentral.root".format(fout, era,sys,eosdir)
        os.system(command)
        print command


    #echo python plotFakeRateHistos${l}.py -y $year -r $sign -w 16 -e "${extra}"
    command='python plotFakeRateHistos.py -y {0:s} -r SS -w 16 -e pow_noL -s {1:s} -f {2:s}; cp *{0:s}*pow_noL_sys{1:s}.png *{0:s}*pow_noL_sys{1:s}.pdf /publicweb/a/alkaloge/plots/ZH_2017/.'.format(era,sys,fout)
    os.system(command)
    print command
