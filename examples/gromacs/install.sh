
# try to deactivate any lingering virtualenv
deactivate || true

export OLDPWD=`pwd`
export INSTALL_ROOT=$OLDPWD/radical_owms_install/
export INSTALL_VE=$OLDPWD/radical_owms_virtualenv/

rm    -rf  $INSTALL_VE
virtualenv $INSTALL_VE
source     $INSTALL_VE/bin/activate
mkdir -p   $INSTALL_ROOT
    
# those 2 don't like pip on futuregrid:
easy_install apache-libcloud
easy_install threadpool

    
cd   $INSTALL_ROOT
test -e radical.owms || git clone git@github.com:saga-project/radical.owms
cd   radical.owms
git  checkout devel
git  pull
yes  | pip  uninstall radical.owms
pip  install .
    
cd   $INSTALL_ROOT
test -e bigjob || git clone git@github.com:saga-project/BigJob.git bigjob
cd   bigjob/
git  checkout develop
git  pull
yes  | pip  uninstall bigjob
pip  install .
    
cd   $INSTALL_ROOT
test -e saga-pilot    || git clone git@github.com:saga-project/saga-pilot.git
cd   saga-pilot/
git  checkout devel
git  pull
yes  | pip  uninstall saga-pilot
pip  install .

cd   $INSTALL_ROOT
test -e saga-python   || git clone git@github.com:saga-project/saga-python.git
cd   saga-python/
git  checkout devel
git  pull
yes  | pip  uninstall saga-python
pip  install .

cd   $INSTALL_ROOT
test -e radical.utils || git clone git@github.com:saga-project/radical.utils.git
cd   radical.utils/
git  checkout devel
git  pull
yes  | pip  uninstall radical.utils
pip  install .

cd $OLDPWD
echo
echo "-------------------------------------"
echo " Ready to run gromacs_demo.py"
echo " Please read leading comments first!"
echo "-------------------------------------"
echo

