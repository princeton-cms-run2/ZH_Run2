import os
import os.path
import sys
import fileinput
import subprocess

def getArgs() :
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-y","--year",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-s","--selection",default=2017,type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-f","--inFileName",default='file.csv',type=str,help="Data taking period, 2016, 2017 or 2018")
    parser.add_argument("-e","--extraTag",default='pow_noL',type=str,help="pow_noL or pow_wL")
    return parser.parse_args()


args = getArgs()
era = str(args.year)
sel = str(args.selection)
tag= str(args.extraTag)

eospath='/eos/uscms/store/user/alkaloge/{0:s}/nAODv7/'.format(sel)



command = "mkdir -p /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/{0:s}/data_{0:s}".format(era)
os.system(command)

sysT = ["Central"]

sysall = ['scale_e', 'scale_m_etalt1p2', 'scale_m_eta1p2to2p1', 'scale_m_etagt2p1',
'scale_t_1prong', 'scale_t_1prong1pizero', 'scale_t_3prong', 'scale_t_3prong1pizero']

upS=sysall
downS=sysall

for i, sys in enumerate(sysall) :
    sysT.append(sys+'Up')
    sysT.append(sys+'Down')



for line in open(args.inFileName,'r').readlines() :
    vals = line.split(',')
    ds = vals[0]
    nickName=vals[1]
    if 'Run' in ds or 'data' in ds : sysT = ["Central"]
    if '#' in ds : continue



    for ic, sys in enumerate(sysT) :
        filejdl = 'condor_{0:s}_{1:s}_{2:s}_{3:s}_sys{4:s}.jdl'.format(ds,era,sel,tag, sys)
        filesh = 'condor_{0:s}_{1:s}_{2:s}_{3:s}_sys{4:s}.sh'.format(ds,era,sel,tag, sys)

	command = "cp Templates/template.sh {0:s}".format(filesh)
	os.system(command)
	command = "cp Templates/template.jdl {0:s}".format(filejdl)
	os.system(command)
	
	
       
	subprocess.call(["sed -i  's/SYSTEMATICHERE/{1:s}/g' {0:s}".format(filesh,sys)], shell=True)
	subprocess.call(["sed -i  's/SYSTEMATICHERE/{1:s}/g' {0:s}".format(filejdl,sys)], shell=True)

	subprocess.call(["sed -i  's/FILEIN/{1:s}/g' {0:s}".format(filesh,ds)], shell=True)
	subprocess.call(["sed -i  's/FILEIN/{1:s}/g' {0:s}".format(filejdl,ds)], shell=True)

	subprocess.call(["sed -i  's/YEAR/{1:s}/g' {0:s}".format(filesh,era)], shell=True)
	subprocess.call(["sed -i  's/YEAR/{1:s}/g' {0:s}".format(filejdl,era)], shell=True)

	subprocess.call(["sed -i  's/CHANNEL/{1:s}/g' {0:s}".format(filesh,sel)], shell=True)
	subprocess.call(["sed -i  's/CHANNEL/{1:s}/g' {0:s}".format(filejdl,sel)], shell=True)

	subprocess.call(["sed -i  's/NICKNAME/{1:s}/g' {0:s}".format(filesh,nickName)], shell=True)
	subprocess.call(["sed -i  's/NICKNAME/{1:s}/g' {0:s}".format(filejdl,nickName)], shell=True)


	subprocess.call(["sed -i  's/TAG/{1:s}/g' {0:s}".format(filesh,tag)], shell=True)
	subprocess.call(["sed -i  's/TAG/{1:s}/g' {0:s}".format(filejdl,tag)], shell=True)


	#subprocess.call(["sed -i  's/YEAR/{1:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.sh".format(ds,era,sel,tag)], shell=True)
	#subprocess.call(["sed -i  's/YEAR/{1:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.jdl".format(ds,era,sel,tag)], shell=True)

	#subprocess.call(["sed -i  's/CHANNEL/{2:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.sh".format(ds,era,sel,tag)], shell=True)
	#subprocess.call(["sed -i  's/CHANNEL/{2:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.jdl".format(ds,era,sel,tag)], shell=True)

	#subprocess.call(["sed -i  's/NICKNAME/{4:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.sh".format(ds,era,sel,tag, nickName)], shell=True)
	#subprocess.call(["sed -i  's/NICKNAME/{4:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.jdl".format(ds,era,sel,tag, nickName)], shell=True)

	#subprocess.call(["sed -i  's/TAG/{3:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.sh".format(ds,era,sel,tag)], shell=True)
	#subprocess.call(["sed -i  's/TAG/{3:s}/g' condor_{0:s}_{1:s}_{2:s}_{3:s}.jdl".format(ds,era,sel,tag)], shell=True)

	#command = "sed -i "'"s/FILEIN/{0:s}/g"'" condor_{0:s}_{1:s}_{2:s}_{3:s}.sh".format(ds,era,sel,tag)

	#outLines = []
	#outLines.append("{0:s}\n".format(ds)
	open(ds+'_'+era+'_'+sel+'_'+tag+'.txt','w').writelines(line)


	command = "chmod 777 {0:s}".format(filejdl)
	os.system(command)
	command = "chmod 777 {0:s}".format(filesh)
	os.system(command)


	command = "mv  {0:s}_{1:s}_{2:s}_{3:s}.txt Jobs/.".format(ds,era,sel,tag)
	os.system(command)
	command = "mv  {0:s} Jobs/.".format(filejdl)
	os.system(command)
	command = "mv  {0:s} Jobs/.".format(filesh)
	os.system(command)

        fileout='{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)

	#/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/2016/
	cf =os.path.isfile('/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)) #ZHToTauTau_2016_sysscale_t_3prong1pizeroUp.root

	if cf :   print 'looks like you have it this in eos', ds, era, sel, tag, sys , '/eos/uscms/store/user/alkaloge/ZH/nAODv7/out_{4:s}/{2:s}/{3:s}_{2:s}_sys{5:s}.root'.format(eospath,sel,era,ds,tag,sys)
	else :   print 'this is missing..... eos', ds, era, sel, tag, sys
	#print  '{0:s}/out_{4:s}/{2:s}/{3:s}_{2:s}.root'.format(eospath,sel,era,ds,tag)
	command = "cd Jobs;condor_submit {0:s} ;cd ..".format(filejdl)
	#if 'ZZTo' in ds or '4L'  in ds: os.system(command)
	cf = os.path.isfile("{0:s}.submitted".format(filejdl))
	if not cf : 
	    #os.system(command)
	    com="touch {0:}.submitted".format(filejdl)
	    #os.system(com)
	#print command
	    

