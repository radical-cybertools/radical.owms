TROY - Tiered Resource OverlaY
****

.. automodule:: troy

TROY is a workload manager that uses pilot overlays as resource layer. As a workload manager, TROY takes care of translating tasks into Compute Units (CUs) and (soon) Data Units (DUs). As a overlay manager, TROY describes and submits pilotjobs on Distributed Computing Infrastructures (DCIs) - FutureGrid, XSEDE, and (soon) OSG. Once the scheduled pilotjobs becomes available on the remote DCI, TROY schedules the CUs (and DUs) of a workload on those pilots for execution.

TROY architecture is depicted in Figure 1. 

Figure 1.

* **Planner**. The user-facing module of TROY, the planner takes care of recieving the workload; check whether its execution is viable given the available resources; and create the two objects workload and overlay to pass respectively to the Workload Manager and the Overlay Manager. 
* **Workload Manager**. Takes care of translating the workload passed by the Planner into a set of units, possibily of different nature - compute and data. This translation is based on the intrinsic characteristics of the given workload and on the current state of the resource overlays - i.e. pilotjobs are already available or need to be created from scratch. 
* **Unit Scheduler**. Recieves a set of units and pilots as input and returns a mapping of units over the pilot(s) composing the overlay. Different scheduling algorithms may be used, *round robin* and *load balancing* being the one currently available.
* **Unit Dispatcher**. It intefaces with the pilot system  and takes care of distributing the units over one or more pilots following the mapping produced by the Unit Shceduler.
* **Overlay Manager**. 
* **Pilot Scheduler**.
* **Pilot Provisioner**.

TROY offers:

* **Convenience**.
* **Functionalities**.
* **Performance**.
