.. _chapter_installation:

************
Installation
************

Currently, RADICAL-OWMS can only be installed via pip directly from GitHub. In a near
future RADICAL-OWMS will be available from the `pypi repository <https://pypi.python.org/>`_. 


Requirements 
============

RADICAL-OWMS relies on a set of external software packages, both core and additional.
The core dependencies are automatically installed alongisde RADICAL-OWMS, while the additional dependencies need to be explicitly installed by the user.

Core dependencies:

* Python (>= 2.5, < 3.x)
* radical.utils (https://pypi.python.org/pypi/radical.utils)
* saga-python (https://pypi.python.org/pypi/saga-python)
* pymongo (https://pypi.python.org/pypi/pymongo)
* paramiko (https://pypi.python.org/pypi/paramiko/1.12.2)

Additional dependencies:

* RADICAL-Pilot (https://github.com/radical-cybertools/radical.pilot)
* BigJob        (https://pypi.python.org/pypi/BigJob)

.. note:: You will need to install at least one pilot framework - RADICAL-Pilot, BigJob, or both.  If neither is installed, a fake `local` backend will be used to run workloads on the local machine.

.. _installation_from_github:

Installation from GitHub
========================

To install RADICAL-OWMS from the stable (main) branch in a virtual environment, you will need to install at least three distinct python packages:

* RADICAL-OWMS;
* radical.pilot and/or BigJob; and
* saga-python.

open a terminal and run:

.. code-block:: bash

    > virtualenv $HOME/radical_owms_tutorial
    > source $HOME/radical_owms_tutorial/bin/activate
    > pip install --upgrade -e git://github.com/saga-project/radical.owms.git@master#egg=radical.owms

Once the installation process has completed, you can do a quick sanity check to make sure that the the packages have been installed properly. In the same virtualenv, run:

.. code-block:: bash

    > radical-owms-version
    0.0.1-569-gd89bdc0-master

This should return the version of the RADICAL-OWMS installation, similar to the above.

To install one or more pilot frameworks see the following instructions but please **DO NOT CREATE A NEW VIRTUAL ENVIRONMENT** with commands like ``virtualenv $HOME/myenv``:

*  RADICAL-Pilot (http://radical.pilot.readthedocs.org/en/latest/installation.html#id1)
*  BigJob        (http://saga-project.github.io/BigJob/)
    

Installation from Source
========================

If you are planning to contribute to the RADICAL-OWMS codebase, you can download
and install RADICAL-OWMS directly from the sources.

First, you need to check out the sources from GitHub.

.. code-block:: bash

    > git clone git@github.com:saga-project/radical.owms.git
    Cloning into 'radical.owms'...
    remote: Reusing existing pack: 4665, done.
    remote: Counting objects: 218, done.
    remote: Compressing objects: 100% (216/216), done.
    remote: Total 4883 (delta 113), reused 0 (delta 0)
    Receiving objects: 100% (4883/4883), 4.23 MiB | 433.00 KiB/s, done.
    Resolving deltas: 100% (3115/3115), done.
    Checking connectivity... done
    > cd radical.owms

Next, run the installer directly from the source directoy (assuming you have 
set up a virtualenv):

.. code-block:: bash
 
    > pip install --upgrade .

    Unpacking /home/merzky/saga/radical.owms
    Running setup.py egg_info for package from file:///home/user/radical.owms/
    ...
    ...
    ...
    Cleaning up...
