#!/bin/bash

export PS1=' $'

##################################################################
# adjust these vars
export ROOT=`pwd`/experiments/
export USERID=merzky
export WORKDIR=/N/u/$USERID/agent
##################################################################


export TROY_VERBOSE=DEBUG
export RADICAL_VERBOSE=DEBUG
export BIGJOB_COORD=redis://ILikeBigJob_wITH-REdIS@gw68.quarry.iu.teragrid.org:6379
export SINON_COORD=mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/
export COORDINATION_URL=$BIGJOB_COORD

###############################################################################
# prepare virtualenv
echo 'prepare virtualenv'
mkdir -p $ROOT
cd       $ROOT
# deactivate || true  # why doesn't this work?
test -d ve || virtualenv ve
source ve/bin/activate


###############################################################################
echo -n "(re)install all packages? [Y/n] "
read answer
if [ "$answer" = "n" ]; then
    echo 'skip install'
else
    echo 'install packages'
    cd  $ROOT

    # those 2 don't like pip:
    easy_install apache-libcloud
    easy_install threadpool

    cd   $ROOT
    test -e troy          || git clone git@github.com:saga-project/troy.git
    cd   troy
    git  checkout devel
    git  pull
    yes  | pip  uninstall troy
    pip  install .

    cd   $ROOT
    test -e bigjob        || git clone git@github.com:saga-project/BigJob.git bigjob
    cd   bigjob/
    git  checkout develop
    git  pull
    yes  | pip  uninstall bigjob
    pip  install .

    cd   $ROOT
    test -e saga-pilot    || git clone git@github.com:saga-project/saga-pilot.git
    cd   saga-pilot/
    git  checkout master
    git  pull
    yes  | pip  uninstall sinon
    pip  install .

    cd   $ROOT
    test -e saga-python   || git clone git@github.com:saga-project/saga-python.git
    cd   saga-python/
    git  checkout devel
    git  pull
    yes  | pip  uninstall saga-python
    pip  install .

    cd   $ROOT
    test -e radical.utils || git clone git@github.com:saga-project/radical.utils.git
    cd   radical.utils/
    git  checkout devel
    git  pull
    yes  | pip  uninstall radical.utils
    pip  install .
fi # install


###############################################################################
echo -n "run sinon experiment? [Y/n] "
read answer
if [ "$answer" = 'n' ]; then
    echo 'skip sinon experiment'
else
    echo 'run  sinon experiment'
    cd   $ROOT/troy
    echo bin/owms.py -cc 75 -tc 4 -rwd $WORKDIR -sce $SINON_COORD  -P sinon  -u $USERID
         bin/owms.py -cc 75 -tc 4 -rwd $WORKDIR -sce $SINON_COORD  -P sinon  -u $USERID
fi


###############################################################################
echo -n "run bigjob experiment? [Y/n] "
read answer
if [ "$answer" = 'n' ]; then
    echo 'skip bigjob experiment'
else
    echo 'run  bigjob experiment'
    cd   $ROOT/troy
    echo bin/owms.py -cc 75 -tc 4 -rwd $WORKDIR -bce $BIGJOB_COORD -P bigjob -u $USERID
         bin/owms.py -cc 75 -tc 4 -rwd $WORKDIR -bce $BIGJOB_COORD -P bigjob -u $USERID
fi

###############################################################################

