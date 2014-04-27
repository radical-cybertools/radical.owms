
################################################################################
RADICAL-OWMS |version| documentation
################################################################################

RADICAL-OWMS (Tiered Resource OverlaY) is a workload manager that leverages pilot overlays as resource layer. As a workload manager, RADICAL-OWMS translates tasks into Compute Units (CUs) and soon also into Data Units (DUs). As a overlay manager, RADICAL-OWMS describes and submits pilotjobs on Distributed Computing Infrastructures (DCIs) - FutureGrid, XSEDE, and in a near future OSG. Once the scheduled pilot job(s) become available on one or more DCIs, RADICAL-OWMS schedules the CUs (and DUs) of a workload on those pilots for execution. RADICAL-OWMS takes also care of staging data in and out of the DCI before and after the execution of the tasks of the workload(s).

**Get involved or contact us:**

+-------+-------------------------------+-------------------------------------------------------------+
| |Git| | **RADICAL-OWMS on GitHub:**   | https://github.com/radical-cybertools/radical.owms/         |
+-------+-------------------------------+-------------------------------------------------------------+
| |Goo| | **RADICAL-OWMS Mailing List:**| https://groups.google.com/forum/#!forum/radical.owms-users  |
+-------+-------------------------------+-------------------------------------------------------------+

.. |Git| image:: images/github.jpg
.. |Goo| image:: images/google.png


################################################################################
Contents:
################################################################################

.. toctree::
   :numbered:
   :maxdepth: 3

   radical_owms.rst
   installation.rst
   configuration.rst
   tutorial/index.rst
   library/index.rst
   plugins/index.rst
   testing.rst
   developers/index.rst


################################################################################
Indices and tables
################################################################################

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

