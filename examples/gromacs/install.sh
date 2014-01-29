export INSTALL_ROOT=/tmp/troy
export INSTALL_VE=$HOME/.virtualenv/pristine

rm -rf $INSTALL_VE
virtualenv-2.7 $INSTALL_VE
. $INSTALL_VE/bin/activate

mkdir $INSTALL_ROOT
    
# those 2 don't like pip:
easy_install apache-libcloud
easy_install threadpool
    
cd   $INSTALL_ROOT
test -e troy || git clone git@github.com:saga-project/troy.git
cd   troy
git  checkout devel
#git  checkout fix/resource_configuration
#git  checkout fix/data_staging
git  pull
yes  | pip  uninstall troy
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
