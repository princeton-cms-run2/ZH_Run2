# . noSVwrapper 2016 16 16 none pow_noL v2 pow 1
year=$1
wp=$2
sys=$3
sign=$5

tagg="pow_noL"

if [[ $sign != 'OS' ]] && [[ $sign != 'SS' ]] ; then
sign='OS'
echo 'will work on the' $sign
fi


#fhadd=allGroups_${year}_OS_LT00_16noSV_${3}_${tag}${ver}${gen}.root

if [[ $4 -eq 1 ]] 

then

#if [[ ! -d /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/data ]] ; then
mkdir -p /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data
mv /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data*root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data/.
echo mv /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data*root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data/.
#fi


hadd -f allGroups_${year}_${sign}_LT00_16noSV_pow_noL_sys$3.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/*_sys${3}*.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data/data_${year}_sys${3}.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_SS/*_sys${3}.root
#hadd -f allGroups_${year}_${sign}_LT00_16noSV_pow_noL_sys$3.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/*_sys${3}*.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_${sign}/data/data_${year}_sys${3}.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_SS/*_sys${3}.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}_OSS/*.root


python mergeCatsToLLCats.py ${year} allGroups_${year}_${sign}_LT00_16noSV_pow_noL_sys$3.root  allGroups_${year}_${sign}_LT00_16noSVll_pow_noL_sys$3.root
fi

if  [[ ! -d plots_pow_noL_sys$3 ]] ; then
mkdir plots_pow_noL_sys$3
fi

#python makeStack.py -f allGroups_${year}_OS_LT00_16noSVll_pow_noL_sys$3.root  -L no -u yes -w $2 -j $3 -e pow_noL_sys$3
python makeStack.py -f allGroups_${year}_${sign}_LT00_16noSVll_pow_noL_sys$3.root  -L no -u yes -w $2 -j $3 -e pow_noL_sys$3 -s ${sign}


cp plots_pow_noL_sys$3/Multi*${year}*.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.
cp plots_pow_noL_sys$3/Stack_${year}_*.p* /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.



if [[ $year -eq 201618 ]] ; then

echo 'will make plots for all years....'

#hadd -f  allGroups_201618_${sign}_LT00_${2}noSVll_${tagg}_sys$3.root allGroups_2016_${sign}_LT00_16noSVll_pow_noL_sys$3.root  allGroups_2017_${sign}_LT00_16noSVll_pow_noL_sys$3.root  allGroups_2018_${sign}_LT00_16noSVll_pow_noL_sys$3.root

hadd -f allGroups_201618_OS_LT00_16noSV_pow_noL_sysCentral.root allGroups_2016_OS_LT00_16noSV_pow_noL_sysCentral.root allGroups_2017_OS_LT00_16noSV_pow_noL_sysCentral.root allGroups_2018_OS_LT00_16noSV_pow_noL_sysCentral.root

#python makeStack.py -f allGroups_201618_${sign}_LT00_16noSVll_${tagg}_sys$3.root -L no -u yes -w $2 -j $sys -e pow_noL_sys$3
python mergeCatsToLLCats.py 201618 allGroups_201618_${sign}_LT00_16noSV_pow_noL_sys$3.root  allGroups_201618_${sign}_LT00_16noSVll_pow_noL_sys$3.root

python makeStack.py -f allGroups_201618_OS_LT00_16noSVll_pow_noL_sysCentral.root -L no -u yes -w 16 -j Central -e pow_noL_sysCentral



#allGroups_201618_OS_LT00_16noSV_pow_noL_sysCentral.root
echo cp plots_pow_noL_sys$3/Multi*201618_*${2}_${3}*${tagg}_sys$3.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.
cp plots_pow_noL_sys$3/Multi*201618_*${2}*${tagg}_sys$3.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.

fi
