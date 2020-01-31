#!/bin/bash

echo "Set up user specific Kappa settings!"

if [ ${USER} == "cheidecker" ]:
    KAPPA_SE_PATH="srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/cheideck/Skimming/" 
    KAPPA_WORK_DIR="/portal/ekpbms1/home/cheidecker/kappa_work"
elif [ ${USER} == "dsavoiu" ]:
    KAPPA_SE_PATH="srm://cmssrm-kit.gridka.de:8443/srm/managerv2?SFN=/pnfs/gridka.de/cms/disk-only/store/user/dsavoiu/Skimming/"
    KAPPA_WORK_DIR="/portal/ekpbms1/home/dsavoiu/kappa_work/"
else:
    KAPPA_SE_PATH=""
    KAPPA_WORK_DIR=""
fi
