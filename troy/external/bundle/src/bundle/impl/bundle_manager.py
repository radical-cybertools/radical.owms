#!/usr/bin/env python

import sys
import getopt
import logging
import Queue
import threading
import argparse
import pickle

try:
    import bundle_agent
except ImportError:
    logging.critical("Can't find module: bundle_agent")
    sys.exit(1)

#from bundle.impl.bundle_agent import AgentState as ClusterState

cluster_list = {}
default_credential_file = "bundle_credentials.txt"
cluster_credentials = []

class BundleManager(object):
    def __init__(self):
        pass

    def add_cluster(self, cluster_credential, finished_job_trace):
        #TODO check duplicated hostname
        cluster = bundle_agent.get(cluster_credential, finished_job_trace)
        if cluster:
            cluster_list[cluster_credential['hostname']] = cluster
            cluster_credentials.append(dict(cluster_credential))
            return cluster_credential['hostname']
        return None

    def remove_cluster(self, cluster_id):
        if cluster_id in cluster_list:
            #print 'closing bundle_agent of {}'.format(cluster_id)
            cluster_list[cluster_id].close()
            #print 'bundle_agent {} closed'.format(cluster_id)
            cluster_list.pop(cluster_id, None)
        else:
            print "ERROR - cluster {} not in cluster list {}".format(cluster_id, cluster_list.keys())

    def get_cluster_list(self):
        return cluster_list.keys()
        #_list = {}
        #for k, v in cluster_list.items():
        #    cluster_attributes = {}
        #    cluster_attributes['state'] = v.cluster_state()
        #    cluster_attributes['num_procs'] = v.num_procs()
        #    cluster_attributes['type'] = v.cluster_type()
        #    _list[k] = cluster_attributes
        #return _list

    def get_cluster_configuration(self, cluster_id):
        if cluster_id in cluster_list:
            return cluster_list[cluster_id].get_attributes()
        else:
            print "ERROR - cluster {} not in cluster list {}".format(cluster_id, cluster_list.keys())

    def get_cluster_workload(self, cluster_id):
        if cluster_id in cluster_list:
            return cluster_list[cluster_id].workload()
        else:
            print "ERROR - cluster {} not in cluster list {}".format(cluster_id, cluster_list.keys())

    def resource_predict(self, cluster_id, resource):
        """
        fields in resource:
            p_procs, how many processors does the caller request
            est_runtime, how long does the caller estimate the application could run, or walltime

        valid combination of fields:
            (1) INPUT - <p_procs> + <est_runtime>
                OUTPUT - qtime, estimated queue wait time based on input

        """
        if cluster_id in cluster_list:
            cluster = cluster_list[cluster_id]
            if 'p_procs' in resource and 'est_runtime' in resource:
                try:
                    #due to unstable of our own oversion of queue time prediction, temporarily use system built-in version.
                    #return cluster.resource_query5(resource['est_runtime'], resource.get('p_procs'), resource.get('n_nodes'))
                    return cluster.estimate_qwait(resource.get('p_procs'), resource['est_runtime'])
                except Exception as e:
                    logging.error('Caught exception: ' + str(e.__class__) + ': ' + str(e))
                    return -1
            else:
                print "ERROR - need both 'p_procs' and 'est_runtime' in resource"
        #else:
        #    return cluster.resource_query1()
        #return cluster.show_start(resource['p_procs'], resource['wall_time'])
        else:
            print "ERROR - cluster {} not in cluster list {}".format(cluster_id, cluster_list.keys())

    def show_supported_cluster_types():
        print bundle_agent.supported_cluster_types.keys()

    #def save_cluster_credentials(self, file_name = default_credential_file):
    #    try:
    #        pickle.dump(cluster_credentials, open(file_name, "wb"))
    #    except Exception as e:
    #        logging.error('Caught exception: ' + str(e.__class__) + ': ' + str(e))

    #def load_cluster_credentials(self, file_name = default_credential_file):
    #    try:
    #        _cluster_credentials = pickle.load(open(file_name, "rb"))
    #        for cc in _cluster_credentials:
    #            add_cluster(cc)
    #    except Exception as e:
    #        logging.error('Caught exception: ' + str(e.__class__) + ': ' + str(e))

    def load_cluster_credentials(self, file_name = default_credential_file):
        try:
            c_file = open(file_name, 'r')
            for line in c_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    if line.startswith('finished_job_trace'):
                        _, finished_job_trace = line.split('=')
                        finished_job_trace = finished_job_trace.strip()
                    else:
                        cc = {}
                        for param in line.split():
                            k, v = param.split('=')
                            cc[k.strip()] = v.strip()
                        self.add_cluster(cc, finished_job_trace)
        except Exception as e:
            logging.error('Caught exception: ' + str(e.__class__) + ': ' + str(e))

    def unit_test(self, case):
        pass

    def __del__(self):
        for cluster_id in cluster_list:
            cluster_list[cluster_id].close()
        #cluster_list = {} <- strange if you keep this: "local variable 'cluster_list' referenced before assignment"

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False,
        help="Turn on debug information printing")
    parser.add_argument('-D', '--daemon', action='store_true', default=False,
        help="Launch as a service daemon")
    parser.add_argument('-t', '--test', dest='n', default=False,
        help="Run test case #N")
    parser.add_argument('-c', '--config_file', dest='bundle_config_file', default=False,
        help="Location of the bundle configuration file")
    return parser.parse_args()

def main(argv=None):

    arguments = parse_arguments()

    if arguments.debug:
        print "debug mode"
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(filename)s:%(lineno)s:%(message)s',
            level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s:%(filename)s:%(lineno)s:%(message)s',
            level=logging.WARNING)

    if arguments.daemon:
        print "daemon mode"
        try:
            import Pyro4
        except ImportError:
            logging.critical("Bundle Manager depends on Pyro4 package installation")
            sys.exit(1)
        bm = BundleManager()
        bm.load_cluster_credentials(arguments.bundle_config_file)
        Pyro4.Daemon.serveSimple(
        {
            bm: "BundleManager"
        },
        ns = True)

    #if arguments.n:
    #    print "run test case #", arguments.n
    #    return unit_test(arguments.n)

if __name__ == "__main__":
    sys.exit(main())
