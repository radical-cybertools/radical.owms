
Part 1: Introduction
====================

The Troy Python module provides ...


Installation
------------

.. warning:: Troy requires **Python >= 2.5**. It won't work with an older version of Python.


For detailed installation instructions, see `FIXME: here`.  For the scope of the
tutorial you can, however, follow the simple receipe below to set up t roy and
its dependencies.


.. code-block:: bash

    # sanity checks
    > python -V ; which virtualenv 
    Python 2.7
    /usr/local/python/2.7/bin/virtualenv

    # create and use the virtualenv
    > virtualenv ~/tutorial
    PYTHONHOME is set.  You *must* activate the virtualenv before using it
    New python executable in ~/tutorial/bin/python
    Installing setuptools............done.
    Installing pip...............done.
    > source ~/tutorial/bin/activate

    # install radical.utils from devel branch
    > pip install git+git://github.com/saga-project/radical.utils.git@devel
    ...

    # install saga-pilot from master branch
    > pip install git+git://github.com/saga-project/saga-pilot.git@master
    ...

    # install troy from master branch, this will pull the remaining dependencies
    > pip install git+git://github.com/saga-project/troy.git@master
    ...

    # ready to run the tutorial -- set verbosity to see things happening:
    # log levels: DEBUG, INFO, WARN, ERROR, CRITICAL
    > export TROY_VERBOSE=INFO


To make sure that your installation works, run the following command to check if
the troy module can be imported by the interpreter (the output of the
command below should be version number of the troy module):


.. code-block:: bash

   > python -c "import troy; print troy.version"
   2014:02:23 20:05:40 MainThread   troy.logger           : [INFO    ] troy            version: 0.0.1-569-gd89bdc0-devel
   0.0.1-569-gd89bdc0-master


The log message is triggered by setting `TROY_VERBOSE` to `INFO` or higher -- it
won't appear otherwise.

