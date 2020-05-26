#simple script to get the nAOD v6 using csv as input
#. find_v6.sh file.csv year


era=""
if [[ $2 -eq 2016 ]] ;then
era=RunIISummer16
fi

if [[ $2 -eq 2017 ]] ;then
era=Fall17
fi

if [[ $2 -eq 2018 ]] ;then
era=Autumn18
fi



while read line 
do


data=`echo $line | awk -F "," '{print $7}' | awk -F "/" '{print $2}'`

#echo will try $data

#echo dasgoclient --query="dataset=/$data*/*$era*AODv6*/NANO*" --limit=0
dasgoclient --query="dataset=/$data*/*${era}*AODv6*/NANO*" --limit=0

done<$1
