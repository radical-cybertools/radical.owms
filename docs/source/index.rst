
################################################################################
Troy |version| documentation
################################################################################

TROY (Tiered Resource OverlaY) is a workload manager that leverages pilot overlays as resource layer. As a workload manager, TROY translates tasks into Compute Units (CUs) and soon also into Data Units (DUs). As a overlay manager, TROY describes and submits pilotjobs on Distributed Computing Infrastructures (DCIs) - FutureGrid, XSEDE, and in a near future OSG. Once the scheduled pilot job(s) become available on one or more DCIs, TROY schedules the CUs (and DUs) of a workload on those pilots for execution. TROY takes also care of staging data in and out of the DCI before and after the execution of the tasks of the workload(s).

**Get involved or contact us:**

+-------+-----------------------+-----------------------------------------------------+
| |Git| | **Troy on GitHub:**   | https://github.com/saga-project/troy/               |
+-------+-----------------------+-----------------------------------------------------+
| |Goo| | **Troy Mailing List:**| https://groups.google.com/forum/#!forum/troy-users  |
+-------+-----------------------+-----------------------------------------------------+

.. |Git| image:: images/github.jpg
.. |Goo| image:: images/google.png


################################################################################
Contents:
################################################################################

.. toctree::
   :numbered:
   :maxdepth: 3

   troy.rst
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
