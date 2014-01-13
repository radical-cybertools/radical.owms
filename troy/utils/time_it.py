

import time
import troy


def timeit (method) :

    def timed (*args, **kwargs) :
        start  = time.time ()
        result = method (*args, **kwargs)
        stop   = time.time ()

        troy._logger.info ('%30s : %6.2f sec' \
                        % ("%s (%s, %s) " % (method.__name__, args, kwargs), 
                           stop-start))
        return result

    return timed

