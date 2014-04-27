.. _chapter_tutorial_setup:

******************************
RADICAL-OWMS Tutorial - Setup
******************************

In order to go through this tutorial you will have to use either a MAC OSX or a Linux OS and you will need to use a terminal. In order to setup the environment where to execute the tutorial open a terminal and do the following:

1. Create a directory where to run the tutorial:

.. code-block:: bash

	> mkdir radical_owms_tutorial

2. Move into the tutorial directory:

.. code-block:: bash

	> cd radical_owms_tutorial

3. Download the repository containing the tutorial code and configuration files.

.. code-block:: bash

	> curl -L -o radical_owms_tutorial_examples.tgz https://github.com/radical-cybertools/radical.owms/raw/master/tutorial/radical_owms_tutorial_examples.tgz
	
4. Uncompress and untar the repository into your working directory:

.. code-block:: bash

	> tar xvfz radical_owms_tutorial_examples.tgz
	
5. Move into the directory with the examples for this tutorial:

.. code-block:: bash

	> cd radical_owms_tutorial_examples/
	
6. Install RADICAL-OWMS following the instructions at: 

	:ref:`installation_from_github` 
	
   and then come back to this page.

7. Set up your account on FutureGrid and XSEDE so that you can ssh into their resources with a **passwordless** ssh key. The following commands need to execute without errors once you have substituted ``<your_login_name>`` with your real login name:

.. code-block:: bash

	> ssh <your_login_name>@sierra.futuregrid.org
	> ssh <your_login_name>@stampede.tacc.xsede.org


Now you are ready for the first part of the RADICAL-OWMS tutorial :ref:`chapter_tutorial_01`.
 
