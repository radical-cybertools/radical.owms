from bundle import BundleManager

def cmd_line_loop(bm):
    done=0
    while not done:
        cmd = raw_input("Enter command: ")
        if cmd == 'quit':
            for cid in bm.get_cluster_list():
                bm.remove_cluster(cid)
            done=1
        elif cmd.startswith('loadc'):
            c, p = cmd.split()
            bm.load_cluster_credentials(p)
        #elif cmd == 'loadr':
        #    bm.load_cluster_credentials()
        elif cmd == 'list':
            print bm.get_cluster_list()
        elif cmd.startswith('showc'):
            c, p = cmd.split()
            print bm.get_cluster_configuration(p)
        elif cmd.startswith('showw'):
            c, p = cmd.split()
            print bm.get_cluster_workload(p)
        elif cmd.startswith('qtime'):
            c, cl, n, w = cmd.split()
            resource={}
            resource['n_nodes']=int(n)
            resource['est_runtime']=int(w)
            print bm.resource_predict(cl, resource)
        #elif cmd.startswith('estimate1'):
        #    c, cl = cmd.split()
        #    resource={}
        #    print bm.resource_predict(cl, resource)

if __name__ == "__main__":

    bm = BundleManager()

    cmd_line_loop(bm)

    print "cmd_line_loop finish"
