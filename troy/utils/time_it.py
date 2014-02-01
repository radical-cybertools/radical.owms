
import time
import troy

def timeit (method) :

    def timed (*args, **kwargs) :

        start  = time.time ()
        result = method (*args, **kwargs)
        stop   = time.time ()

        signature = "TIMER %s (%s, %s, %s) " % (method.__name__, args[0].__name__, args[1:], kwargs)

        troy._logger.info ('%30s : %6.2f sec' % (signature, stop-start))

        return result

    return timed
