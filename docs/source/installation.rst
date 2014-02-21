.. _chapter_installation:

************
Installation
************

Currently, TROY can only be installed via pip directly from GitHub. In a near future TROY will be available from the `pypi repository <https://pypi.python.org/>`_. 

Requirements 
============

TROY relies on a set of external software packages, both core and additional. The core packages are installed automatically as dependencies, while the additional packages need to be explicitly installed by the user.

Core packages:

* Python >= 2.5, < 3.x
* setuptools (https://pypi.python.org/pypi/setuptools)
* saga-python (https://pypi.python.org/pypi/saga-python)
* radical.utils (https://pypi.python.org/pypi/radical.utils)

Additional packages:

* sagapilot (https://github.com/saga-project/saga-pilot)
* BigJob (https://pypi.python.org/pypi/BigJob)
* paramiko (https://pypi.python.org/pypi/paramiko)

.. note:: You will need to install at least one pilot framework - sagapilot,  BigJob, or both.

Installation from GitHub
========================

To install TROY from the stable (main) branch in a virtual environment, 
open a terminal and run:

.. code-block:: bash

    virtualenv $HOME/myenv
    source $HOME/myenv/bin/activate
    pip install --upgrade -e git://github.com/saga-project/troy.git@master#egg=troy

Next, you can do a quick sanity check to make sure that the the packages have
been installed properly. In the same virtualenv, run:

.. code-block:: bash

    troy-version

This should return the version of the TROY installation, e.g., `0.X.Y`.

Installation from Source
========================

If you are planning to contribute to the TROY codebase, you can download
and install TROY directly from the sources.

First, you need to check out the sources from GitHub.

.. code-block:: bash

    git@github.com:saga-project/troy.git

Next, run the installer directly from the source directoy (assuming you have 
set up a vritualenv):

.. code-block:: bash
 
    python setup.py install

Optionally, you can try to run the unit tests:

.. code-block:: bash

    python setup.py test

.. note:: More on testing can be found in chapter :ref:`chapter_testing`.