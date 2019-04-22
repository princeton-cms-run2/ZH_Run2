python makeHistosByGroup.py --sign SS --LTcut 0.
python makeHistosByGroup.py --sign OS --LTcut 0.
python makeHistosByGroup.py --sign SS --LTcut 75.
python makeHistosByGroup.py --sign OS --LTcut 75.

python makeStack.py -c all -w nowait -f allGroups_2017_SS_LT00.root
python makeStack.py -c all -w nowait -f allGroups_2017_SS_LT75.root
python makeStack.py -c all -w nowait -f allGroups_2017_OS_LT00.root
python makeStack.py -c all -w nowait -f allGroups_2017_OS_LT75.root




