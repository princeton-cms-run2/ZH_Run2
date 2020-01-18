import os

for root, directories, filenames in os.walk('.'):
    for filename in filenames:
        if filename[-4:] == '.err' :
            fName = os.path.join(root,filename)
            print("file={0:s}".format(fName))
            iLast = -1 
            for i, line in enumerate(open(fName,'r').readlines()) :
                lineLower = line.lower() 
                if '====' in lineLower : continue
                if 'warning' in lineLower : continue
                if 'info in' in lineLower : continue
                if 'mass expected' in lineLower : continue
                if i > iLast+1 : print('***') 
                print("    [{0:4d}]={1:s}".format(i,line.strip()))
                iLast = i
        


 
