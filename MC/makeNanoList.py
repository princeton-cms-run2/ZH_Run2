import os 
outLines = []
for j, line in enumerate(open('SamCondor.csv','r').readlines()) :
    #dataset = '/' + line.split('/')[1] + '/RunIIFall17*/NANOAODSIM'
    dataset = line.strip() 
    query = '"child dataset={0:s}"'.format(dataset)
    print("\nQuery={0:s}".format(query))
    command = "dasgoclient --query={0:s} --limit=0 > dataset.txt".format(query)
    os.system(command)
    outLine = '{0:s},'.format(dataset) 
    for i, nanodataset in enumerate(open('dataset.txt','r').readlines()) :
        if '102X' in nanodataset :
            outLine += '{0:s},'.format(nanodataset.strip())
            print(" Result {0:d}={1:s}".format(i,outLine)) 
    outLines.append(outLine.rstrip(',') + '\n')
    #if j > 2 : break

sampleLines = []
for line in outLines :
    nickName = line.split('_')[0].lstrip('/')
    try :
        sampleName = line.split(',')[1].strip()
    except IndexError :
        print("Missing sample for {0:s}".format(nickName))
        sampleName = ''
        
    sampleLines.append('{0:s}, , , , , ,{1:s}\n'.format(nickName,sampleName))
    
open('MC_10_2_X.csv','w').writelines(outLines)
open('MCSample_102X.csv','w').writelines(sampleLines)

    


    
    
