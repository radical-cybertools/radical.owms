#!/usr/bin/env python

"""
Handle link-down case
"""

import sys
import getopt
import Queue
import threading
import logging
import socket
import datetime
import time
import os
import xml.etree.ElementTree as ET
import re
import traceback

try:
    import paramiko
except ImportError:
    logging.critical("Bundle Agent depends on paramiko package installation.")

class AgentState(object):
    Up = "Up"
    Down = "Down"
    Fault = "Fault"

class MoabAgent(threading.Thread):
    #TODO provide brief description
    #Cluster attributes
    my_type = 'moab/torque'
    torque_version = ''
    moab_version = ''
    alive_nodes = 0
    alive_procs = 0
    busy_nodes = 0
    busy_procs = 0
    free_nodes = 0
    free_procs = 0
    # queue
    # | name | Max Wallclock Limit | HARD MAXPROC constraint
        # Up Nodes | Free Nodes | Processors per Node (ncpus) | Up Processors |
        # Free Processors | Started Flag | Enabled Flag |
    # Only display queues that are non-acl_user_enable
    queue_info = {}
    cmd_prefix = ''
    # Mark this cluster as heterogenerous, needs check per node np, different
    # queue may have different set of nodes.
    h_flag = False

    #Agent attributes
    purgetime = 300
    sampling_interval = 270 #completed job 5:00
    max_walltime = 0
    admin_level = 1
    state = AgentState.Down
    state_reason_code = ""
    queue = None
    ssh = None
    _timer = None
    job_trace = None

    use_built_in = False
    # job run-time history
    # {
    #   (class, group, user, num_nodes, num_cores, wall_time) : [ last1_JobID, last2_JobID2 ],
    #   ...
    # }
    rtime_lkup_tbl = {}
    # {
    #   JobID1 : [ run_time, finish_time ]
    #   ...
    # }
    rtime_tbl = {}

    def __init__(self, credential, verbose=0, db_dir=None, use_built_in=False):
        #TODO provide brief description
        #TODO provide these commands through 'init.script'
        self.hostname = credential['hostname']
        self.state = AgentState.Down
        self.use_built_in = use_built_in

        #Setup the logger
        #self.logger = logging.getLogger(__name__)
        self.logger = logging.getLogger(self.hostname)
        if not self.logger.handlers:
            fmt = '%(asctime)-15s {} %(name)-8s %(levelname)-8s %(funcName)s:%(lineno)-4s %(message)s'.format(self.hostname)
            formatter = logging.Formatter(fmt)
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        self.set_verbosity(verbose)
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warn = self.logger.warn
        self.error = self.logger.error
        self.critical = self.logger.critical

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            #TODO use key= here
            self.ssh.connect( hostname=self.hostname,
                              port=credential.get('port', 22),
                              username=credential.get('username'),
                              password=credential.get('password'),
                              key_filename=credential.get('key_filename') )
        except Exception as e:
            self.error(str(e.__class__) + str(e))
            raise
        else:
            self.info("Connected to {}".format(self.hostname))

        if credential.get('h_flag') == 'True':
            self.h_flag = True

        #Check if torque/moab is running on this cluster
        exit_status1, stdout1, stderr1 = self.run_cmd("qstat")
        exit_status2, stdout2, stderr2 = self.run_cmd("showq")

        if exit_status1 != 0 or exit_status2 != 0:
            exit_status, stdout, stderr = self.run_cmd("module list")
            if 'command not found' in stderr:
                exit_status, stdout, stderr = self.run_cmd("source /etc/profile.d/modules.sh; module list")
                if 'No such file' in stderr or 'command not found' in stderr:
                    err_msg = "Unable to locate 'module' on {}: {}".format(self.hostname, stderr)
                    self.error(err_msg)
                    raise Exception(err_msg)
                else:
                    self.cmd_prefix += "source /etc/profile.d/modules.sh > /dev/null 2>&1; "
            #module ready

            if 'torque' not in stdout:
                exit_status, stdout, stderr = self.run_cmd("module load torque")
                #if 'Unable to locate' in stderr and 'torque' in stderr:
                if exit_status != 0:
                    err_msg = "Unable to locate 'torque' on {}: {}".format(self.hostname, stderr)
                    self.error(err_msg)
                    raise Exception(err_msg)
                else:
                    self.cmd_prefix += "module load torque > /dev/null 2>&1; "
            #torque ready

            exit_status, stdout, stderr = self.run_cmd("module list")
            if 'moab' not in stdout:
                exit_status, stdout, stderr = self.run_cmd("module load moab")
                #if 'Unable to locate' in stderr and 'moab' in stderr:
                if exit_status != 0:
                    err_msg = "Unable to locate 'moab' on {}: {}".format(self.hostname, stderr)
                    self.error(err_msg)
                    raise Exception(err_msg)
                else:
                    self.cmd_prefix += "module load moab > /dev/null 2>&1; "
            #moab ready

            ##Finding version info
            #stdin, stdout, stderr = self.ssh.exec_command(
            #    self.cmd_prefix + "module list")
            #status = stdout.channel.recv_exit_status()
            #output_str = ''.join(stdout.readlines())
            #output_str += ''.join(stderr.readlines())
            #pos_1 = output_str.find('torque')
            #pos_2 = pos_1
            #for c in output_str[pos_1:]:
            #    if not c.isdigit():
            #        pos_2 += 1
            #    else:
            #        break
            #pos_3 = pos_2
            #for c in output_str[pos_2:]:
            #    if not c.isspace():
            #        pos_3 += 1
            #    else:
            #        break
            #self.torque_version = output_str[pos_2:pos_3]

            #pos_1 = output_str.find('moab')
            #pos_2 = pos_1
            #for c in output_str[pos_1:]:
            #    if not c.isdigit():
            #        pos_2 += 1
            #    else:
            #        break
            #pos_3 = pos_2
            #for c in output_str[pos_2:]:
            #    if not c.isspace():
            #        pos_3 += 1
            #    else:
            #        break
            #self.moab_version = output_str[pos_2:pos_3]

        self.state = AgentState.Up

        #Run qstat once to get queue configuration
        self.get_queue_info()

        #Run showq once to get # of node/proc(s)
        #self.exec_showq1()
        self.get_np_num()

        if not self.use_built_in:
            self.load_runtime_history(db_dir)

        if not self.use_built_in:
            _ts = time.time()
            _st = datetime.datetime.fromtimestamp(_ts).strftime('%Y-%m-%d_%Hh%Mm%Ss.%f')
            job_trace_filename = 'job_trace_{}_{}'.format(self.hostname, _st)
            self.job_trace = open(os.path.join(db_dir, job_trace_filename), "w")
            self.job_trace.write('{}\n'.format(self.hostname))
            self.exec_showq3()
        #Start sampling thread
        threading.Thread.__init__(self, name=self.hostname + " bundle agent")
        self.queue = Queue.Queue()
        self.setDaemon(True)
        self.start()

        if not self.use_built_in:
            #Set peoriodical sampling timer
            self._timer = threading.Timer(self.sampling_interval, self.sampling_timer)
            self._timer.setDaemon(True)
            self._timer.start()

    def __del__(self):
        self.info("Delete moab cluster on {0}".format(self.hostname))
        self.close()

    def cluster_type(self):
        return self.my_type

    def cluster_version(self):
        version = {}
        version['torque_version'] = self.torque_version
        version['moab_version'] = self.moab_version
        return version

    def cluster_state(self):
        return self.state

    def num_procs(self):
        return self.alive_procs

    def num_nodes(self):
        return self.alive_nodes

    def workload(self):
        try:
            # call get_np_num to refresh cluster workload information
            self.get_np_num()
        except ClusterSideFatalError:
            pass
        except Exception as e:
            logging.error('Caught exception: ' + str(e.__class__) + ': ' + str(e))
        if self.h_flag is True:
            return {
                'alive_nodes' : self.alive_nodes,
                'alive_procs' : self.alive_procs,
                'busy_nodes' : self.busy_nodes,
                'busy_procs' : self.busy_procs,
                'free_nodes' : self.free_nodes,
                'free_procs' : self.free_procs,
                'per_pool_workload' : self.properties_nodes
                }
        else:
            return {
                'alive_nodes' : self.alive_nodes,
                'alive_procs' : self.alive_procs,
                'busy_nodes' : self.busy_nodes,
                'busy_procs' : self.busy_procs,
                'free_nodes' : self.free_nodes,
                'free_procs' : self.free_procs
                }

    def run_cmd(self, cmd, timeout=30):
        try:
            chan = self.ssh.get_transport().open_session()
            chan.settimeout(timeout)
            #chan.set_combine_stderr(True)
            chan.exec_command(self.cmd_prefix + cmd)

            stdout = ''
            while True:
                recv_buf = chan.recv(65536)
                if len(recv_buf) == 0:
                    break
                else:
                    stdout += recv_buf

            stderr = ''
            while True:
                recv_buf = chan.recv_stderr(65536)
                if len(recv_buf) == 0:
                    break
                else:
                    stderr += recv_buf

            exit_status = chan.recv_exit_status()
        except socket.timeout:
            self.error("Timeout executing '%s' after %d seconds" % (cmd, timeout))
            chan.close()
            raise
        else:
            return exit_status, stdout, stderr

    def exec_showq1(self):
        exit_status, stdout, stderr = self.run_cmd("showq --xml")
        if exit_status != 0:
            self.state = AgentState.Fault
            self.state_reason_code = stderr
            err_msg = "showq --xml return code {}: {}".format(exit_status, stderr)
            self.error(err_msg)
            raise Exception(err_msg)
        elif self.state is AgentState.Fault:
            self.state = AgentState.Up
            self.state_reason_code = ''

        root = ET.fromstring(stdout)
        cluster = root.find('cluster')
        self.alive_nodes = int(cluster.attrib['LocalUpNodes'])
        self.alive_procs = int(cluster.attrib['LocalUpProcs'])
        self.busy_nodes = int(cluster.attrib['LocalActiveNodes'])
        self.busy_procs = int(cluster.attrib['LocalAllocProcs'])
        self.free_nodes = int(cluster.attrib['LocalIdleNodes'])
        self.free_procs = int(cluster.attrib['LocalIdleProcs'])

    def exec_showq2(self):
        exit_status, stdout, stderr = self.run_cmd("showq --xml")
        if exit_status != 0:
            self.state = AgentState.Fault
            self.state_reason_code = stderr
            err_msg = "showq --xml: " + stderr
            self.error(err_msg)
            raise Exception(err_msg)
        elif self.state is AgentState.Fault:
            self.state = AgentState.Up
            self.state_reason_code = ''

        root = ET.fromstring(stdout)
        cluster = root.find('cluster')
        cur_alive_nodes = int(cluster.attrib['LocalUpNodes'])
        cur_busy_nodes = int(cluster.attrib['LocalActiveNodes'])
        cur_avail_nodes = int(cluster.attrib['LocalIdleNodes'])

        cur_time = int(cluster.attrib['time'])
        running_list = []
        queueing_list = []
        for queue in root.iter('queue'):
            if queue.attrib['option'] == 'active':
                for job in queue.findall('job'):
                    #temp solution for clusters don't report ReqNodes
                    if 'ReqNodes' in job.attrib:
                        ReqNodes = int(job.attrib['ReqNodes'])
                    else:
                        ReqNodes = int(job.attrib['ReqProcs']) / 8 + (1 if int(job.attrib['ReqProcs']) % 8 else 0)
                    running_list.append( {
                        'JobID':job.attrib['JobID'],
                        'Class':job.attrib['Class'],
                        'Group':job.attrib['Group'],
                        'User':job.attrib['User'],
                        'JobName':job.attrib['JobName'],
                        'ReqNodes':ReqNodes,
                        'ReqProcs':int(job.attrib['ReqProcs']),
                        'StartTime':int(job.attrib['StartTime']),
                        'WallClock':int(job.attrib['ReqAWDuration'])
                        }
                    )
            elif queue.attrib['option'] == 'eligible':
                for job in queue.findall('job'):
                    if job.attrib['JobName'] == 'poweroff':
                        continue
                    #temp solution for clusters don't report ReqNodes
                    if 'ReqNodes' in job.attrib:
                        ReqNodes = int(job.attrib['ReqNodes'])
                    else:
                        ReqNodes = int(job.attrib['ReqProcs']) / 8 + (1 if int(job.attrib['ReqProcs']) % 8 else 0)
                    queueing_list.append( {
                        'JobID':job.attrib['JobID'],
                        'Class':job.attrib['Class'],
                        'Group':job.attrib['Group'],
                        'User':job.attrib['User'],
                        'JobName':job.attrib['JobName'],
                        'ReqNodes':ReqNodes,
                        'ReqProcs':int(job.attrib['ReqProcs']),
                        'WallClock':int(job.attrib['ReqAWDuration']),
                        'Priority':int(job.attrib['StartPriority'])
                        }
                    )
        return cur_time, cur_alive_nodes, cur_busy_nodes, cur_avail_nodes, running_list, queueing_list

    def exec_showq3(self):
        exit_status, stdout, stderr = self.run_cmd("showq -c --xml")
        if exit_status != 0:
            self.state = AgentState.Fault
            self.state_reason_code = stderr
            err_msg = "showq -c --xml: " + stderr
            self.error(err_msg)
            raise Exception(err_msg)
        elif self.state is AgentState.Fault:
            self.state = AgentState.Up
            self.state_reason_code = ''

        root = ET.fromstring(stdout)
        for queue in root.iter('queue'):
            if 'option' not in queue.attrib:
                pass
            elif queue.attrib['option'] == 'completed':
                _purgetime = int(queue.attrib['purgetime'])
                if self.purgetime != _purgetime:
                    self.warn('purgetime changed from {} to {}'.format(self.purgetime, _purgetime))
                    if _purgetime < 30:
                        self.warn("purgetime {} is too short! Can't set an approporiate sampling time".format(_purgetime))
                    else:
                        self.purgetime = _purgetime
                        sampling_interval = _purgetime*9/10
                for job in queue.findall('job'):
                    _JobID = job.attrib['JobID']
                    if _JobID not in self.rtime_tbl:
                        #begin critical area
                        self.rtime_tbl[_JobID] = [int(job.attrib['AWDuration']), int(job.attrib['CompletionTime'])]
                        if 'ReqNodes' in job.attrib:
                            _job_signature = ( job.attrib['Class'],
                                               job.attrib['Group'],
                                               job.attrib['User'],
                                               int(job.attrib['ReqNodes']),
                                               int(job.attrib['ReqProcs']),
                                               int(job.attrib['ReqAWDuration']) )
                        else:
                            _job_signature = ( job.attrib['Class'],
                                               job.attrib['Group'],
                                               job.attrib['User'],
                                               int(job.attrib['ReqProcs']),
                                               int(job.attrib['ReqAWDuration']) )
                        if _job_signature in self.rtime_lkup_tbl:
                            if int(job.attrib['CompletionTime']) > self.rtime_tbl[self.rtime_lkup_tbl[_job_signature][0]][1]:
                                self.rtime_lkup_tbl[_job_signature][1] = self.rtime_lkup_tbl[_job_signature][0]
                                self.rtime_lkup_tbl[_job_signature][0] = _JobID
                            elif int(job.attrib['CompletionTime']) > self.rtime_tbl[self.rtime_lkup_tbl[_job_signature][1]][1]:
                                self.rtime_lkup_tbl[_job_signature][1] = _JobID
                        else:
                            self.rtime_lkup_tbl[_job_signature] = [_JobID, -1]
                        self.debug('found newly completed job {} - {}: {}'.format(_JobID, _job_signature, self.rtime_tbl[_JobID]))
                        if 'ReqNodes' in job.attrib:
                            self.job_trace.write('JobID={} JobName={} DRMJID={} Class={} Group={} User={} ReqNodes={} ReqProcs={} ReqAWDuration={} State={} CompletionCode={} SubmissionTime={} StartTime={} CompletionTime={} SuspendDuration={} AWDuration={}\n'.format(
                                job.attrib['JobID'], job.attrib['JobName'], job.attrib['DRMJID'], job.attrib['Class'], job.attrib['Group'], job.attrib['User'], job.attrib['ReqNodes'], job.attrib['ReqProcs'], job.attrib['ReqAWDuration'], job.attrib['State'], job.attrib['CompletionCode'], job.attrib['SubmissionTime'], job.attrib['StartTime'], job.attrib['CompletionTime'], job.attrib['SuspendDuration'], job.attrib['AWDuration']))
                        else:
                            self.job_trace.write('JobID={} JobName={} DRMJID={} Class={} Group={} User={} ReqProcs={} ReqAWDuration={} State={} CompletionCode={} SubmissionTime={} StartTime={} CompletionTime={} SuspendDuration={} AWDuration={}\n'.format(
                                job.attrib['JobID'], job.attrib['JobName'], job.attrib['DRMJID'], job.attrib['Class'], job.attrib['Group'], job.attrib['User'], job.attrib['ReqProcs'], job.attrib['ReqAWDuration'], job.attrib['State'], job.attrib['CompletionCode'], job.attrib['SubmissionTime'], job.attrib['StartTime'], job.attrib['CompletionTime'], job.attrib['SuspendDuration'], job.attrib['AWDuration']))
                        self.job_trace.flush()
                        #end critical area

    # run pbsnodes -a to collect info of node status
    def get_nodes_stat(self):
        exit_status, stdout, stderr = self.run_cmd("pbsnodes -a -x")
        if exit_status != 0:
            # TODO print call stack
            err_msg = "cmd 'pbsnodes' return code {}: {}".format(exit_status, stderr)
            self.error(err_msg)
            raise Exception(err_msg)
        root = ET.fromstring(stdout)
        #cur_alive_nodes = cur_busy_nodes = cur_avail_nodes = 0
        #{name : [state, np, properties]}
        alive_node_list={}
        for node in root.findall('Node'):
            state = node.find('state').text
            if state == 'free' or state == 'job-exclusive':
                alive_node_list[node.find('name').text] = [state, int(node.find('np').text), node.find('properties').text]
        return alive_node_list

    def get_np_num(self):
        if self.h_flag is False:
            self.exec_showq1()
        else:
            nl = self.get_nodes_stat()
            properties_nodes = {}
            for k, v in nl.items():
                state = v[0]
                np = v[1]
                properties = v[2]
                if properties in self.queue_features.values():
                    if properties not in properties_nodes:
                        properties_nodes[properties] = {
                            'np' : np,
                            'alive_nodes' : 0,
                            'alive_procs' : 0,
                            'busy_nodes' : 0,
                            'busy_procs' : 0,
                            'free_nodes' : 0,
                            'free_procs' : 0 }
                    if state == 'free': #Why cannot use 'is' here?
                        properties_nodes[properties]['free_nodes'] += 1
                        properties_nodes[properties]['free_procs'] += np
                    elif state == 'job-exclusive':
                        properties_nodes[properties]['busy_nodes'] += 1
                        properties_nodes[properties]['busy_procs'] += np
                    properties_nodes[properties]['alive_nodes'] += 1
                    properties_nodes[properties]['alive_procs'] += np
            self.properties_nodes = properties_nodes
            self.free_nodes = sum([v['free_nodes'] for k, v in properties_nodes.items()])
            self.free_procs = sum([v['free_procs'] for k, v in properties_nodes.items()])
            self.busy_nodes = sum([v['busy_nodes'] for k, v in properties_nodes.items()])
            self.busy_procs = sum([v['busy_procs'] for k, v in properties_nodes.items()])
            self.alive_nodes = self.free_nodes + self.busy_nodes
            self.alive_procs = self.free_procs + self.busy_procs

    #find out reservations
    def exec_showres(self, alive_node_list):
        exit_status, stdout, stderr = self.run_cmd("showres -n --xml")
        if exit_status != 0:
            # TODO print call stack
            err_msg = "cmd 'showres' return code {}: {}".format(exit_status, stderr)
            self.error(err_msg)
            raise Exception(err_msg)
        resv_list = {}
        root = ET.fromstring(stdout)
        for node in root.findall('node'):
            node_name=node.attrib['name']
            if node_name not in alive_node_list:
                continue
            for resv in node.findall('nres'):
                if resv.attrib['Type'] != 'User':
                    continue
                res_name = resv.attrib['Name']
                if res_name in resv_list:
                    #resv_list
                    pass
                else:
                    pass

    def get_queue_feature(self, queue_info):
        exit_status, stdout, stderr = self.run_cmd("showconfig -v")
        queue_features = {}
        r = re.compile('[ \[\]=]+')
        for line_str in stdout.splitlines():
            if line_str.find('CLASSCFG') == 0:
                (_,q,_,f,_)=r.split(line_str)
                if q in queue_info:
                    queue_features[q] = f
        self.queue_features = queue_features

    def get_queue_info(self):
        exit_status, stdout, stderr = self.run_cmd("qstat -Q -f")
        #TODO handle failure case
        _queue_info = {}
        for line_str in stdout.splitlines():
            if line_str.find('Queue') == 0:
                pos = line_str.find(':')
                queue_name = line_str[pos+1:].strip()
                _queue_info[queue_name] = {'queue_name' : queue_name}
            elif line_str.find('=') != -1:
                queue_attr_k = line_str.lstrip()[:line_str.lstrip().find(' ')]
                pos1 = line_str.find('=')
                queue_attr_v = line_str[pos1+1:].strip()
                if queue_attr_k == 'acl_user_enable':
                    if (queue_attr_v == 'True'):
                        _queue_info[queue_name]['restricted_access'] = True
                elif queue_attr_k == 'resources_max.walltime':
                    if queue_attr_v.count(':') == 2:
                        h, m, s = [int(i) for i in queue_attr_v.split(':')]
                        _max_walltime = 3600*h+60*m+s
                    elif queue_attr_v.count(':') == 3:
                        d, h, m, s = [int(i) for i in queue_attr_v.split(':')]
                        _max_walltime = seconds=24*3600*d+3600*h+60*m+s
                    _queue_info[queue_name]['max_walltime'] = _max_walltime
                    if _max_walltime > self.max_walltime:
                        self.max_walltime = _max_walltime
                elif queue_attr_k == 'started' or queue_attr_k == 'enabled':
                    _queue_info[queue_name][queue_attr_k] = queue_attr_v
        for k,v in _queue_info.items():
            if ('restricted_access' in v) and (v['restricted_access'] == True):
                del _queue_info[k]

        # get 'CLASSCFG'
        if self.h_flag is True:
            self.get_queue_feature(_queue_info)
            for k, v in _queue_info.items():
                _queue_info[k]['pool'] = self.queue_features[k]

        self.queue_info = _queue_info
        self.debug('{} max_walltime = {}'.format(self.hostname, str(datetime.timedelta(seconds=self.max_walltime))))

    def get_attributes(self):
        attributes = {}
        attributes['queue_info'] = self.queue_info
        if self.h_flag is True:
            properties_nodes = self.properties_nodes
            pool_size = {}
            for k, v in properties_nodes.items():
                pool_size[k] = {}
                pool_size[k]['np'] = v['np']
                pool_size[k]['num_procs'] = v['alive_procs']
                pool_size[k]['num_nodes'] = v['alive_nodes']
            attributes['pool'] = pool_size
        attributes['num_procs'] = self.num_procs()
        attributes['num_nodes'] = self.num_nodes()
        attributes['state'] = self.cluster_state()
        return attributes

    def sampling_timer(self):
        self.queue.put("showq")
        #TODO check thread healthy
        self._timer = threading.Timer(self.sampling_interval, self.sampling_timer)
        self._timer.setDaemon(True)
        self._timer.start()

    def run(self):
        self.throt1 = 0
        while True:
            cmd = self.queue.get()
            if cmd is "showq":
                #TODO handle failure case
                #self.debug("run 'showq -c' periodically")
                try:
                    self.exec_showq3()
                except Exception as e:
                    self.throt1+=1
                    if self.throt1 < 10:
                        logging.error('periodically collect complete task trace failed: {} {}'.format(e.__class__, e))
                self.queue.task_done()
                #TODO add lock
            elif cmd is "close":
                self.debug('received "close" command')
                if self._timer:
                    self._timer.cancel()
                #self.debug('timer canceled')
                self.queue.task_done()
                #self.debug('task done')
                break
            else:
                self.error("Unknown command {0}".format(str(cmd)))
                self.queue.task_done()
                continue

    def estimate_qwait(self, p_procs, wall_time):
        if self.use_built_in:
            return self.show_start(p_procs, wall_time)
        else:
            return self.resource_query5(wall_time, p_procs)

    #TODO temporary method
    def show_start(self, p_procs, wall_time):
        #TODO lock protection ssh
        exit_status, stdout, stderr = self.run_cmd("showstart --xml {0}@{1}".format(
                str(p_procs), wall_time))
        #print "exit_status={} stdout={}".format(exit_status, stdout)
        #TODO handle failure case
        if 'job' not in stdout or 'StartTime' not in stdout or 'now' not in stdout:
            raise Exception(stdout)
        else:
            tree = ET.fromstring(stdout)
            return int(tree.find('job').attrib['StartTime']) - int(tree.find('job').attrib['now'])

    #return instantly available resources
    #return results similar to Moab-showbf
    #   factors:
    #       job-features
    #       reservation:
    #           User reservation
    #           Top-priority-job reservation
    #   jobs blocked due to dependency, although at a higher prio, won't affect shadow time
    #   in calculating shadow_time, user-provided estimations should be used instead of system-generated ones
    def resource_query1(self):
        """
        right at this moment, what are the maximum number of nodes I can have,
        and have them for how long? (idle, backfill-able)
        return:
            Tasks/Nodes/bf_window
        """
        #find how many nodes/procs are 'free' right now
        cur_time, cur_alive_nodes, cur_busy_nodes, cur_avail_nodes, running_list, queueing_list = self.exec_showq2()
        #on some clusters, pbsnodes will report more accurate information
        #if self.pbsnodes_flag:
        cur_alive_nodes, cur_busy_nodes, cur_avail_nodes, alive_node_list = self.exec_pbsnodes()
        #identify reservation
        #self.exec_showres(alive_node_list)
        #find shadow time
        return cur_avail_nodes*8, cur_avail_nodes, self.max_walltime

    def resource_query4(self, k_nodes):
        """
        given a cluster, when can I have k nodes available,
        and how long can I use them?
        """
        cur_time, total_nodes, scheduled_list, nodes_tbl = self.run_simulation()
        if k_nodes > total_nodes:
            return -1, -1
        begin_time = end_time = wall_time = -1
        for time_point in sorted(nodes_tbl.keys()):
            avail_nodes = nodes_tbl[time_point]
            if begin_time == -1 and avail_nodes >= k_nodes:
                begin_time = time_point
            elif begin_time != -1 and avail_nodes < k_nodes:
                end_time = time_point
                break
        if begin_time == -1: #This should not happen
            self.error('Never will be enough nodes?')
        elif end_time == -1:
            wall_time = self.max_walltime
        else:
            wall_time = end_time - begin_time
        return begin_time, wall_time

    def resource_query5(self, est_runtime, p_procs=None, n_nodes=None):
        est_queue_time = est_start_time = -1
        #TODO check p_procs, n_nodes within limit (0, max], p_procs*8>=n_nodes
        if p_procs and not n_nodes:
            n_nodes = p_procs/8+(1 if p_procs%8 else 0)
        self.debug('showstart p={}, n={} @ {}'.format(p_procs, n_nodes, est_runtime))

        cur_time, cur_alive_nodes, cur_busy_nodes, cur_avail_nodes, running_list, queueing_list = self.exec_showq2()

        self.debug('current available nodes = {}'.format(cur_avail_nodes))

        #get rid of jobs whose ReqNodes > cur_alive_nodes
        queueing_list = [x for x in queueing_list if x['ReqNodes'] <= cur_alive_nodes]

        #handle the case that currently available nodes enough for top priority job in queue to run
        #but it is not run, this is either because wrong number of cur_avail_nodes (this case should
        #be covered by other logic to guarantee correctness of cur_avail_nodes), or due to these jobs
        #are incorrectly marked as 'eligible'.
        first_real_eligible = len(queueing_list)
        for go_idx in range(len(queueing_list)):
            if queueing_list[go_idx]['ReqNodes'] > cur_avail_nodes:
                first_real_eligible = go_idx
                break
        queueing_list = queueing_list[first_real_eligible:]

        #first check whether it can run now on idle nodes
        if cur_avail_nodes >= n_nodes and len(queueing_list) == 0:
            est_queue_time = 0
            est_start_time = cur_time
            return est_queue_time, est_start_time

        cur_time_save = cur_time

        monalisasmile = ';-)'
        fake_job = { 'JobID':monalisasmile, 'Class':monalisasmile, 'Group':monalisasmile, 'User':monalisasmile, 'JobName':monalisasmile,
                     'ReqNodes':n_nodes, 'ReqProcs':p_procs, 'WallClock':est_runtime, 'Priority':monalisasmile }
        queueing_list.append(fake_job)

        #Step 0: calculate finish time for currently running jobs
        nodes_cur_jobs = 0
        for job in running_list:
            #job['FinishTime'] = job['StartTime'] + self.run_time(job)
            job['FinishTime'] = job['StartTime'] + job['WallClock']
            nodes_cur_jobs+=job['ReqNodes']
        #well, if you find the current in-use number of nodes does
        #not comply with the number that is totally used by running jobs,
        #reservation happens
        if nodes_cur_jobs+cur_avail_nodes != cur_alive_nodes:
            self.error("The # of nodes being used by all running jobs '{}' does not match that reported by system: alive={} inuse={} idle={}".format(nodes_cur_jobs, cur_alive_nodes, cur_busy_nodes, cur_avail_nodes))
            #return -1, -1
        if cur_alive_nodes < n_nodes:
            self.error('n_nodes ({}) > total_alive_nodes ({}), cannot estimate starttime!'.format(n_nodes, cur_alive_nodes))
            return -1, -1

        #Loop until queue job list empty
        while len(queueing_list):
            #Step 1: find shadow time and extra nodes
            print "loop 1 ..."
            node_req1 = queueing_list[0]['ReqNodes']
            #print cur_avail_nodes
            avail_nodes = cur_avail_nodes
            shadow_time = 0
            for job in running_list:
                print "loop 2..."
                avail_nodes += job['ReqNodes']
                if avail_nodes >= node_req1:
                    shadow_time = job['FinishTime']
                    if queueing_list[0]['JobID'] is monalisasmile:
                        est_queue_time = shadow_time - cur_time_save
                        est_start_time = shadow_time
                        return est_queue_time, est_start_time
                    queueing_list[0]['StartTime'] = shadow_time
                    #queueing_list[0]['FinishTime'] = shadow_time+self.run_time(queueing_list[0])
                    #system will still use user provided walltime to determine shadow time
                    queueing_list[0]['FinishTime'] = shadow_time+queueing_list[0]['WallClock']
                    print 'found next shadow time: ' + datetime.datetime.fromtimestamp(shadow_time).strftime('%a %b %d %H:%M:%S')
                    break;
            extra_nodes = avail_nodes - node_req1

            #print 'cur_time={}, shadow_time={}'.format(cur_time, shadow_time)
            while cur_time < shadow_time:
                #Step 2: backfill
                bf_job_idx = []
                print "loop 3..."
                for idx in range(1, len(queueing_list)):
                    #if queueing_list[idx]['ReqNodes'] <= cur_avail_nodes and \
                    #   cur_time + self.run_time(queueing_list[idx]) <= shadow_time:
                    if queueing_list[idx]['ReqNodes'] <= cur_avail_nodes and \
                       cur_time + queueing_list[idx]['WallClock'] <= shadow_time:
                        pass
                    elif queueing_list[idx]['ReqNodes'] <= min(cur_avail_nodes, extra_nodes):
                        extra_nodes -= queueing_list[idx]['ReqNodes']
                    else:
                        continue
                    if queueing_list[idx]['JobID'] is monalisasmile:
                        est_queue_time = cur_time - cur_time_save
                        est_start_time = cur_time
                        return est_queue_time, est_start_time
                    queueing_list[idx]['StartTime'] = cur_time
                    #queueing_list[idx]['FinishTime'] = cur_time + self.run_time(queueing_list[idx])
                    queueing_list[idx]['FinishTime'] = cur_time + queueing_list[idx]['WallClock']
                    cur_avail_nodes -= queueing_list[idx]['ReqNodes']
                    bf_job_idx.append(idx)
                    print '        found job {} which can be backfilled, idx={}'.format(queueing_list[idx]['JobID'], idx)
                #update queueing job list
                idx_offset = 0
                print 'backfill job idx range: {}'.format(bf_job_idx)
                for idx1 in bf_job_idx:
                    bf_job = queueing_list.pop(idx1-idx_offset)
                    #insert the job to the list of running jobs,
                    #according to finish time
                    insert_pos2 = len(running_list)
                    for idx2 in range(len(running_list)):
                        if running_list[idx2]['FinishTime'] > bf_job['FinishTime']:
                            insert_pos2 = idx2
                            break
                    running_list.insert(insert_pos2, bf_job)
                    idx_offset+=1

                #Move on to next time point (next job in queue finish)
                next_finish_job = running_list.pop(0)
                cur_time = next_finish_job['FinishTime']
                cur_avail_nodes += next_finish_job['ReqNodes']
                print '    move to next time point: {} cur_avail_nodes={}'.format(datetime.datetime.fromtimestamp(cur_time).strftime('%a %b %d %H:%M:%S'), cur_avail_nodes)

            #now it's time for the first job in queue to run
            while len(queueing_list) and queueing_list[0]['ReqNodes'] <= cur_avail_nodes:
                print "loop 4..."
                first_in_queue = queueing_list.pop(0)
                print 'first_in_queue: {}'.format(first_in_queue)
                if first_in_queue['JobID'] is monalisasmile:
                    est_queue_time = cur_time - cur_time_save
                    est_start_time = cur_time
                    return est_queue_time, est_start_time
                first_in_queue['StartTime'] = cur_time
                first_in_queue['FinishTime'] = cur_time+self.run_time(first_in_queue)
                insert_pos = len(running_list)
                for idx in range(len(running_list)):
                    print "loop 5..."
                    #print 'running_list {}: {}'.format(idx, running_list[idx])
                    if running_list[idx]['FinishTime'] > first_in_queue['FinishTime']:
                        insert_pos = idx
                        break
                running_list.insert(insert_pos, first_in_queue)
                cur_avail_nodes -= first_in_queue['ReqNodes']
                print 'cur_avail_nodes reduced to {}'.format(cur_avail_nodes)

        self.error("shouldn't reach here! est_queue_time={}, est_start_time={}".format(est_queue_time, est_start_time))
        return est_queue_time, est_start_time

    def load_runtime_history(self, dir_trace='bundle/db'):
        directory = os.path.join(os.getcwd(), dir_trace)
        if not os.path.exists(directory):
            self.info("create new directory for db files")
            os.makedirs(directory)
        self.debug("loading runtime history under '{}' directory".format(directory))
        _counting1 = _counting2 = 0
        for root, _, files in os.walk(os.path.join(os.getcwd(), dir_trace)):
            for f in files:
                fullpath = os.path.join(root, f)
                file_trace = open(fullpath, 'r')
                hostname = file_trace.readline().strip()
                if hostname == self.hostname:
                    self.debug("found runtime history log file '{}'".format(f))
                    for line in file_trace:
                        f_job = {}
                        for field in line.strip().split():
                            k, v = field.split('=')
                            f_job[k] = v
                        if f_job['JobID'] not in self.rtime_tbl:
                            self.rtime_tbl[f_job['JobID']] = [int(f_job['AWDuration']), int(f_job['CompletionTime'])]
                            _counting1 += 1
                            if 'ReqNodes' in f_job:
                                _job_signature = ( f_job['Class'], f_job['Group'], f_job['User'],
                                               int(f_job['ReqNodes']), int(f_job['ReqProcs']), int(f_job['ReqAWDuration']) )
                            else:
                                _job_signature = ( f_job['Class'], f_job['Group'], f_job['User'],
                                               int(f_job['ReqProcs']), int(f_job['ReqAWDuration']) )
                            if _job_signature in self.rtime_lkup_tbl:
                                if int(f_job['CompletionTime']) > self.rtime_tbl[self.rtime_lkup_tbl[_job_signature][0]][1]:
                                    self.rtime_lkup_tbl[_job_signature][1] = self.rtime_lkup_tbl[_job_signature][0]
                                    self.rtime_lkup_tbl[_job_signature][0] = f_job['JobID']
                                elif self.rtime_lkup_tbl[_job_signature][1] != -1 and \
                                    int(f_job['CompletionTime']) > self.rtime_tbl[self.rtime_lkup_tbl[_job_signature][1]][1]:
                                    self.rtime_lkup_tbl[_job_signature][1] = f_job['JobID']
                            else:
                                self.rtime_lkup_tbl[_job_signature] = [ f_job['JobID'], -1 ]
                                _counting2 += 1
        self.debug("loaded {} new records, {} new job signatures".format(_counting1, _counting2))

    def last2_estimate(self, signature):
        if signature in self.rtime_lkup_tbl:
            if self.rtime_lkup_tbl[signature][1] == -1:
                last1_time = self.rtime_tbl[self.rtime_lkup_tbl[signature][0]][0]
                self.debug('found only one record of past job which matches the given one {}, last1 job {} runtime is {} seconds'.format(signature, self.rtime_lkup_tbl[signature][0], last1_time))
                return last1_time
            else:
                last1_time = self.rtime_tbl[self.rtime_lkup_tbl[signature][0]][0]
                last2_time = self.rtime_tbl[self.rtime_lkup_tbl[signature][1]][0]
                self.debug('found two records in past jobs that match the given one {}, last1 job {} runtime is {} seconds, last2 job {} runtime is {} seconds.'.format(signature, self.rtime_lkup_tbl[signature][0], last1_time, self.rtime_lkup_tbl[signature][1], last2_time))
                return (last1_time+last2_time)/2
        else:
            self.debug("didn't find any record in past jobs that match the given one {}, return -1".format(signature))
            return -1

    def run_time(self, job):
        last2_mean = self.last2_estimate((job['Class'],job['Group'],job['User'],job['ReqNodes'],job['ReqProcs'],job['WallClock']))
        if last2_mean == -1:
            return job['WallClock']
        else:
            return min(last2_mean, job['WallClock'])

    def run_simulation(self):
        cur_time, cur_alive_nodes, cur_busy_nodes, cur_avail_nodes, running_list, queueing_list = self.exec_showq2()

        if flag==5:
            queueing_list.append(fake_job)

        cur_time_save = cur_time
        #The dict which maps time to number of free nodes, naturally indexed by timestamp integer as key
        nodes_tbl = {}
        #first mark-up point, assume at this moment there should be no enough resources available for the
        #queue front job to run, nor does any job capable of backfilling
        nodes_tbl[cur_time] = cur_avail_nodes
        print 'cur_avail_nodes = {}'.format(cur_avail_nodes)
        #Step 0: calculate finish time for currently running jobs
        nodes_cur_jobs = 0
        for job in running_list:
            job['FinishTime'] = job['StartTime'] + self.run_time(job)
            job['PredictFlag'] = ''
            nodes_cur_jobs+=job['ReqNodes']
        #well, if you find the current in-use number of nodes does
        #not comply with the number that is totally used by running jobs,
        #reservation happens
        if nodes_cur_jobs+cur_avail_nodes != cur_alive_nodes:
            self.warn("The # of nodes being used by all running jobs '{}' does not match that reported by system: alive{} inuse{} idle{}".format(nodes_cur_jobs, cur_alive_nodes, cur_busy_nodes, cur_avail_nodes))
        scheduled_list = list(running_list)

        #Loop until queue job list empty
        while len(queueing_list):
            #Step 1: find shadow time and extra nodes
            node_req1 = queueing_list[0]['ReqNodes']
            #print cur_avail_nodes
            avail_nodes = cur_avail_nodes
            shadow_time = 0
            for job in running_list:
                avail_nodes += job['ReqNodes']
                if avail_nodes >= node_req1:
                    shadow_time = job['FinishTime']
                    queueing_list[0]['StartTime'] = shadow_time
                    queueing_list[0]['FinishTime'] = shadow_time+self.run_time(queueing_list[0])
                    queueing_list[0]['PredictFlag'] = 'TopQ'
                    print 'found next shadow time: ' + datetime.datetime.fromtimestamp(shadow_time).strftime('%a %b %d %H:%M:%S')
                    break;
            extra_nodes = avail_nodes - node_req1

            #print 'cur_time={}, shadow_time={}'.format(cur_time, shadow_time)
            while cur_time < shadow_time:
                #Step 2: backfill
                bf_job_idx = []
                left_pos = 1
                found_bf_job = True
                print '    start looking for backfill jobs'
                while found_bf_job:
                    found_bf_job = False
                    for idx in range(left_pos , len(queueing_list)):
                        if queueing_list[idx]['ReqNodes'] <= cur_avail_nodes and \
                           cur_time + self.run_time(queueing_list[idx]) <= shadow_time:
                            found_bf_job = True
                        elif queueing_list[idx]['ReqNodes'] <= min(cur_avail_nodes, extra_nodes):
                            found_bf_job = True
                            extra_nodes -= queueing_list[idx]['ReqNodes']
                        if found_bf_job:
                            queueing_list[idx]['StartTime'] = cur_time
                            queueing_list[idx]['FinishTime'] = cur_time + self.run_time(queueing_list[idx])
                            cur_avail_nodes -= queueing_list[idx]['ReqNodes']
                            bf_job_idx.append(idx)
                            left_pos = idx+1
                            print '        found job {} which can be backfilled, idx={}'.format(queueing_list[idx]['JobID'], idx)
                            break
                #update queueing job list
                idx_offset = 0
                print 'backfill job idx range: {}'.format(bf_job_idx)
                for idx1 in bf_job_idx:
                    bf_job = queueing_list.pop(idx1-idx_offset)
                    bf_job['PredictFlag'] = 'Backfill'
                    #insert the job to the list of running jobs,
                    #according to finish time
                    insert_pos2 = len(running_list)
                    for idx2 in range(len(running_list)):
                        if running_list[idx2]['FinishTime'] > bf_job['FinishTime']:
                            insert_pos2 = idx2
                            break
                    running_list.insert(insert_pos2, bf_job)
                    idx_offset+=1
                    insert_pos3 = len(scheduled_list)
                    for idx3 in range(len(scheduled_list)):
                        if scheduled_list[idx3]['FinishTime'] > bf_job['FinishTime']:
                            insert_pos3 = idx3
                            break
                    scheduled_list.insert(insert_pos3, bf_job)

                #mark-up point, this might update previously updated shadow time point
                nodes_tbl[cur_time] = cur_avail_nodes

                #Move on to next time point (next job in queue finish)
                next_finish_job = running_list.pop(0)
                cur_time = next_finish_job['FinishTime']
                cur_avail_nodes += next_finish_job['ReqNodes']
                print '    move to next time point: {} cur_avail_nodes={}'.format(datetime.datetime.fromtimestamp(cur_time).strftime('%a %b %d %H:%M:%S'), cur_avail_nodes)

            #now it's time for the first job in queue to run
            while len(queueing_list) and queueing_list[0]['ReqNodes'] <= cur_avail_nodes:
                first_in_queue = queueing_list.pop(0)
                print 'first_in_queue: {}'.format(first_in_queue)
                insert_pos = len(running_list)
                for idx in range(len(running_list)):
                    print 'running_list {}: {}'.format(idx, running_list[idx])
                    print 'first_in_queue: {}'.format(first_in_queue)
                    if running_list[idx]['FinishTime'] > first_in_queue['FinishTime']:
                        insert_pos = idx
                        break
                running_list.insert(insert_pos, first_in_queue)
                insert_pos = len(scheduled_list)
                for idx in range(len(scheduled_list)):
                    if scheduled_list[idx]['FinishTime'] > first_in_queue['FinishTime']:
                        insert_pos = idx
                        break
                scheduled_list.insert(insert_pos, first_in_jueue)
                cur_avail_nodes -= first_in_queue['ReqNodes']
                print 'cur_avail_nodes reduced to {}'.format(cur_avail_nodes)

            #maybe there are huge amount of jobs that are able to run at this point?
            #mark-up point
            nodes_tbl[cur_time] = cur_avail_nodes

        #get free nodes number after finishing of remainning jobs
        while len(running_list):
            next_finish_job = running_list.pop(0)
            cur_avail_nodes += next_finish_job['ReqNodes']
            nodes_tbl[next_finish_job['FinishTime']] = cur_avail_nodes

        return cur_time_save, cur_alive_nodes, scheduled_list, nodes_tbl

    def set_verbosity(self, verbose):
       if verbose == 0:
           self.logger.setLevel(logging.ERROR)
       elif verbose == 1:
           self.logger.setLevel(logging.INFO)
       elif verbose > 1:
           self.logger.setLevel(logging.DEBUG)

    def close(self):
        #print "close() called"
        self.debug('close')
        if self.queue:
            self.queue.put("close")
            #self.debug('waiting for join return')
            self.queue.join()
            #self.debug('join returned')
            self.queue = None
        if self.ssh:
            self.ssh.close()
            self.ssh = None
        if self.job_trace:
            self.job_trace.close()

supported_cluster_types = {
    "moab" : MoabAgent,
}

def get(cluster_attributes, db_dir=None):
    #TODO: add brief description
    try:
        if cluster_attributes['cluster_type'].lower() == 'moab':
            return MoabAgent(
                cluster_attributes,
                0,
                db_dir,
                use_built_in=True    #temp use system built-in predictor
                )
        else:
            logging.error("Unknown cluster type: {0}".format(str(cluster_attributes['type'])))
    except Exception as e:
        #traceback.print_exception()
        logging.error('bundle agent creation failed: {} {}'.format(e.__class__, e))

def unit_test():
    pass
