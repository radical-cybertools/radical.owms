#!/usr/bin/env python


import sys
import troy


# This example creates a simple workload, and a simple overlay, and runs them
# through the Troy WorkloadManager.


# create workload
td1 = troy.TaskDescription     ({troy.TAG            : 'one',
                                 troy.EXECUTABLE     : '/bin/sleep', 
                                 troy.ARGUMENTS      : ['10']})

td2 = troy.TaskDescription     ({troy.TAG            : 'two',
                                 troy.EXECUTABLE     : '/bin/sleep', 
                                 troy.ARGUMENTS      : ['20']})

rel = troy.RelationDescription ({troy.HEAD           : 'one',
                                 troy.TAIL           : 'two',
                                 troy.RELATION_TIME  : troy.SEQUENTIAL_END,
                                 troy.RELATION_SPACE : None})

wl = troy.Workload ()
wl.add_task     ([td1, td2])
wl.add_relation (rel)
wl._dump ()

troy.WorkloadManager.register_workload(wl)

# # create overlay
# pd1 = troy.PilotDescription ({troy.RESOURCE : 'local',
#                               troy.SLOTS    : '1'})
# 
# ol = troy.Overlay ()
# ol.add_pilot (pd1)
# ol._dump ()
# 
# # run overlay
# ol.schedule ()                        # DESCRIBED   -> SCHEDULED
# ol.dispatch ()                        # SCHEDULED   -> DISPATCHED

# run workload
wlm = troy.WorkloadManager ()
wlm.translate_workload (wl.id)             # DESCRIBED   -> TRANSLATED
wlm.bind_workload      (wl.id, None)       # TRANSLATED  -> BOUND
wlm.dispatch_workload  (wl.id, None)       # SCHEDULED   -> DISPATCHED

wl.wait ([troy.COMPLETED, troy.FAILED]) #  DISPATCHED -> COMPLETED | FAILED
wl._dump ()

# # tear down overlay
# ol.cancel ()                          # DISPATCHED  -> CANCELLED

