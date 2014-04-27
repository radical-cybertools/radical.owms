.. _chapter_testing:

*******
Testing
*******

Along with RADICAL-OWMS's functionalities, we develop also a growing set of unit 
tests. The unit test source code can be found in ``radical.owms/tests``. You 
can run the unit tests directly from the source directory without having
to install RADICAL-OWMS first:

.. code-block:: bash

    RADICAL_OWMS_VERBOSE=debug \
    python setup.py test

.. note:: 

    If you run the same command in an environment where RADICAL-OWMS is already
    installed, the unit tests will test the installed version instead of the 
    source version. 

Remote Testing 
==============
The RADICAL-OWMS unit tests use pilot agents launched on the local machine (`localhost`) by default. However, it is possible to run a subset of the  unit tests (``radical.owms/tests/remote/``) on a remote machine. Remote testing can  be controlled via a set of environment variables:

	+-------------------------------------------+---------------------------------------------------------------+
	| Environment Variable                      | What                                                          |
	+===========================================+===============================================================+
	| ``RADICALPILOT_TEST_REMOTE_RESOURCE``     | The name (key) of the resource.                               |
	+-------------------------------------------+---------------------------------------------------------------+
	| ``RADICALPILOT_TEST_REMOTE_SSH_USER_ID``  | The user ID on the remote system.                             |
	+-------------------------------------------+---------------------------------------------------------------+
	| ``RADICALPILOT_TEST_REMOTE_SSH_USER_KEY`` | The SSH key to use for the connection.                        |
	+-------------------------------------------+---------------------------------------------------------------+
	| ``RADICALPILOT_TEST_REMOTE_WORKDIR``      | The working directory on the remote system.                   |
	+-------------------------------------------+---------------------------------------------------------------+
	| ``RADICALPILOT_TEST_REMOTE_CORES``        | The number of cores to allocate.                              |
	+-------------------------------------------+---------------------------------------------------------------+
	| ``RADICALPILOT_TEST_REMOTE_NUM_CUS``      | The number of Compute Units to run.                           |
	+-------------------------------------------+---------------------------------------------------------------+
	| ``RADICALPILOT_TEST_TIMEOUT``             | Set a timeout in minutes after which the tests will terminate.|
	+-------------------------------------------+---------------------------------------------------------------+

So if for example you want to run the unit tests on Futuregrid's `India cluster <http://manual.futuregrid.org/hardware.html>`_, run:

.. code-block:: bash

    RADICALPILOT_VERBOSE=debug \
    RADICALPILOT_TEST_REMOTE_SSH_USER_ID=oweidner # optional \
    RADICALPILOT_TEST_REMOTE_RESOURCE=futuregrid.INDIA \
    RADICALPILOT_TEST_REMOTE_WORKDIR=/N/u/oweidner/radical.pilot.sandbox \
    RADICALPILOT_TEST_REMOTE_CORES=32 \
    RADICALPILOT_TEST_REMOTE_NUM_CUS=64 \
    python setup.py test

.. note:: 
 
    Be aware that it can take quite some time for pilots to get scheduled on the remote system. You can set ``RADICALPILOT_TEST_TIMEOUT`` to force the tests to abort after a given number of minutes.
