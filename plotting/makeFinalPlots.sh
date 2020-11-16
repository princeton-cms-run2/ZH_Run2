# . noSVwrapper 2016 16 16 none pow_noL v2 pow 1
year=$1
wp=$2
sys=$3

#fhadd=allGroups_${year}_OS_LT00_16noSV_${3}_${tag}${ver}${gen}.root

if [[ $4 -eq 1 ]] 

then

#if [[ ! -d /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/data ]] ; then
mkdir -p /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/data
mv /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/data*root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/data/.
#fi


hadd -f allGroups_${year}_OS_LT00_16noSV_pow_noL_sys$3.root /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/*_sys${3}.root  /eos/uscms/store/user/alkaloge/ZH/nAODv7/out_pow_noL/${year}/data/data_${year}_sys${3}.root


python mergeCatsToLLCats.py ${year} allGroups_${year}_OS_LT00_16noSV_pow_noL_sys$3.root  allGroups_${year}_OS_LT00_16noSVll_pow_noL_sys$3.root
fi

if  [[ ! -d plots_pow_noL_sys$3 ]] ; then
mkdir plots_pow_noL_sys$3
fi

#python makeStack.py -f allGroups_${year}_OS_LT00_16noSVll_pow_noL_sys$3.root  -L no -u yes -w $2 -j $3 -e pow_noL_sys$3
python makeStack.py -f allGroups_${year}_OS_LT00_16noSVll_pow_noL_sys$3.root  -L no -u yes -w $2 -j $3 -e pow_noL_sys$3


cp plots_pow_noL_sys$3/Multi*${year}*.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.
cp plots_pow_noL_sys$3/Stack_${year}_*.p* /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.



if [[ $year -eq 20168 ]] ; then

hadd -f  allGroups_201618_OS_LT00_${2}noSVll_${tagg}_sys$3.root allGroups_2016_OS_LT00_16noSVll_pow_noL_sys$3.root  allGroups_2017_OS_LT00_16noSVll_pow_noL_sys$3.root  allGroups_2018_OS_LT00_16noSVll_pow_noL_sys$3.root

python makeStack.py -f allGroups_201618_OS_LT00_${2}noSVll_${3}_${tagg}_sys$3.root -L no -u yes -w $2 -j $sys -e pow_noL_sys$3

echo cp plots_pow_noL_sys$3/Multi*201618_*${2}_${3}*${tagg}_sys$3.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.
cp plots_pow_noL_sys$3/Multi*201618_*${2}*${tagg}_sys$3.pdf /publicweb/a/alkaloge/plots/ZH/nAODv7/Final/.

fi
