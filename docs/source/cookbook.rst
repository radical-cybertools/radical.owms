
CookBook
********


Quick Installation Guide
-------------------------------------

```
#  we need the python and git module loaded 
[merzky@i136 ~]$ module load git python
git version 1.7.8.3 loaded
Python version 2.7 loaded

[merzky@i136 ~]$ python -V
Python 2.7

[merzky@i136 ~]$ which virtualenv
/N/soft/python/2.7/bin/virtualenv

[merzky@i136 ~]$ virtualenv ve
PYTHONHOME is set.  You *must* activate the virtualenv before using it
New python executable in ve/bin/python
Installing setuptools............done.
Installing pip...............done.

# use the virtualenv
[merzky@i136 ~]$ source ve/bin/activate


# these two don't install cleanly via pip on india, so use easy_install
(ve)[merzky@i136 ~]$ easy_install apache-libcloud threadpool
...

# we need radical.utils from master branch
(ve)[merzky@i136 ~]$ pip install git+git://github.com/saga-project/radical.utils.git@master

# install troy and remaining dependencies.  'pip install' cannot access provate
# github repos on india, so we have to clone first
(ve)[merzky@i136 ~]$ git clone git@github.com:saga-project/troy.git 
Cloning into 'troy'...
remote: Counting objects: 2677, done.
remote: Compressing objects: 100% (1185/1185), done.
remote: Total 2677 (delta 1467), reused 2632 (delta 1422)
Receiving objects: 100% (2677/2677), 2.85 MiB | 3.49 MiB/s, done.
Resolving deltas: 100% (1467/1467), done.

# now install
(ve)[merzky@i136 ~]$ pip install --upgrade troy/
...


# ready to run the demo -- set verbosity to see things happening:
(ve)[merzky@i136 ~]$ export TROY_VERBOSE=DEBUG
(ve)[merzky@i136 ~]$ python troy/examples/phase1_demo_2.py 


```


Caveats:
--------

```
# If a 'pip install' command complains about 
#     Permission denied: '/tmp/pip-build/....'
# then add the following flag to the pip command line:
#     --build=/tmp/pip-build-`id -un`
# which will then use the respective temp dir.  You may want to clean that dir
# up after installation.


# If a 'pip install' command complains about 
#     CompressionError: bz2 module is not available
# then use 'easy_install' for that specific module.

# If after one of the above problems, 'pip install' complains about
#     pkg_resources.DistributionNotFound: setuptools==2.0
# then you are screwed -- pip corrupted your virtualenv.
# Remove everything and start over from fresh...

```
