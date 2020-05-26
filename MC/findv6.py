import os 
import sys
outLines = []

era={'2016':'RunIISummer16', '2017':'Fall17', '2018':'Autumn18'}


for j, line in enumerate(open('MCsamples_2017_ZH.csv','r').readlines()) :
    dataset = line.split('/')[1] 
    query = 'dataset=/{0:s}*/*{1:s}*AODv6*/NANO* --limit=0'.format(dataset,era[str(sys.argv[1])])
    command = "dasgoclient --query={0:s}".format(query)
    #print command
    os.system(command)


    


    
    
