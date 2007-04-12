"""nodoctests
Distributed SAGE

AUTHORS:
    Yi Qiang (yqiang@gmail.com)
"""

import os

import sage.interfaces.cleaner
from sage.misc.all import DOT_SAGE
import pexpect

## def spawn(cmd, logfile=None, verbose=True):
##     pid = os.fork()
##     if pid != 0:
##         sage.interfaces.cleaner.cleaner(pid)
##         if verbose:
##             print "Started %s (pid = %s, logfile = '%s')"%(cmd, pid, logfile)
##         return pid
##     if pid == 0:
##         if not logfile is None:
##             cmd += ' 2>&1 > ' + logfile
##         os.system(cmd)

def start_process(typ, hostname, address, port):
    cmd = 'dsage_%s.py &'%typ
    os.system(cmd)
    dir = '%s/dsage/'%os.environ['DOT_SAGE']
    pid_file = '%s/server-hostname-address-port.pid'%dir
    while True:
        try:
            if os.path.exists(pid_file):
                return int(open(pid_file).read())
        except Exception, msg:
            print msg


class DistributedSage(object):
    r"""
    DistributedSage allows you to do distributed computing using SAGE.

    To get up and running quickly, run dsage.setup() to run the
    configuration utility.

    Note that configuration files will be stored in the
    directory \code{$DOT_SAGE/dsage}.

    There are three distinct parts of Distributed SAGE:
        Server
            Launch the server with dsage.server()

        Worker
            Launch the worker with dsage.worker()

        Client
            Create the DSage object like this:
                d = DSage()

    EXAMPLES:
    This starts a server instance on localhost:

        sage: dsage.server()

    The dsage server is currently blocking by default.

    Open another sage instance and type:

        sage: dsage.worker()

    This starts a worker connecting the localhost.

    Open yet another terminal and type:
        sage: D = DSage()

    This creates a connection to the remote server.  To do a simple
    evaluation, type:
        sage: job1 = D('2+2')

    This sends the job '2+2' to a worker and you can view the
    result by typing:

        sage: print job1

    This is the most basic way of interacting with dsage. To do more
    complicated tasks, you should look at the DistributedFunction
    class.  For example, to do distributed integer factorization with
    ECM, type this:

        sage: f = DistributedFactor(P, number, name='my_factor')
        sage: f.start()

    To check the result, do

        sage: print f.result

    To check if it is done, do

        sage: print f.done

    Customization:

        To customize how the worker, server, or client behaves, you
        can look for their respective conf files in DOT_SAGE/dsage.
        The configuration file should be self explanatory.
    """
    def __init__(self):
        pass

    def start_all(self):
        self.server(blocking=False)
        self.worker(blocking=False)
        from sage.dsage.interface.dsage_interface import BlockingDSage as DSage

        return DSage()

    def server(self, blocking=True, logfile=None):
        r"""
        Run the Distributed SAGE server.

        Doing \code{dsage.server()} will spawn a server process which
        listens by default on port 8081.

        INPUT:
            blocking -- boolean (default: True) -- if False the dsage
                        server will run and you'll still be able to
                        enter commands at the command prompt (though
                        logging will make this hard).
            logfile  -- only used if blocking=True; the default is
                        to log to $DOT_SAGE/dsage/server.log
        """
        cmd = 'dsage_server.py'
        if not blocking:
            if logfile is None:
                logfile = '%s/dsage/server.log'%DOT_SAGE
            spawn(cmd, logfile)
        else:
            os.system(cmd)

##     def server(self):
##         r"""
##         Run the Distributed SAGE server.

##         Doing \code{dsage.server()} will spawn a server process which
##         listens by default on port 8081.
##         """
##         cmd = 'dsage_server.py'
##         os.system(cmd)


##     def worker(self, server=None, port=None, blocking=True, logfile=None):
##         r"""
##         Run the Distributed SAGE worker.

##         Typing \code{sage.worker()} will launch a worker which by
##         default connects to localhost on port 8081 to fetch jobs.

##         INPUT:

##             server -- (string, default: None) the server you want to
##                       connect to if None, connects to the server
##                       specified in .sage/dsage/worker.conf
##             port -- (integer, default: None) the port that the server
##                       listens on for workers.
##             blocking -- (bool, default: True) whether or not to make a
##                         blocking connection.
##             logfile -- only used if blocking=True; the default is
##                        to log to $DOT_SAGE/dsage/worker.log
##         """
##         cmd = 'dsage_worker.py'
##         if blocking:
##             cmd += ' %s' % server
##             cmd += ' %s' % port
##             os.system(cmd)
##         else:
##             if not server is None or not port is None:
##                 args = [str(server), str(port)]
##             else:
##                 args = []
##             if logfile is None:
##                 logfile = '%s/dsage/worker.log'%DOT_SAGE
##             spawn(cmd + ' '.join(args), logfile)

    def worker(self, server=None, port=None):
        r"""
        Run the Distributed SAGE worker.

        Typing \code{sage.worker()} will launch a worker which by
        default connects to localhost on port 8081 to fetch jobs.

        INPUT:

            server -- (string, default: None) the server you want to
                      connect to if None, connects to the server
                      specified in .sage/dsage/worker.conf
            port -- (integer, default: None) the port that the server
                      listens on for workers.
        """
        cmd = 'dsage_worker.py'
        cmd += ' %s' % server
        cmd += ' %s' % port
        os.system(cmd)

    def setup(self):
        r"""
        This is the setup utility which helps you configure dsage.

        Type \code{dsage.setup()} to run the configuration for the server,
        worker and client.  Alternatively, if you want to run the
        configuration for just one parts, you can launch
        \code{dsage.setup_server()}, \code{dsage.setup_worker()}
        or \code{dsage.setup()}.
        """
        cmd = 'dsage_setup.py'
        os.system(cmd)

    def setup_server(self):
        """
        This method runs the configuration utility for the server.
        """
        cmd = 'dsage_setup.py server'
        os.system(cmd)

    def setup_worker(self):
        """
        This method runs the configuration utility for the worker.
        """
        cmd = 'dsage_setup.py worker'
        os.system(cmd)

    def setup_client(self):
        """
        This method runs the configuration utility for the client.
        """
        cmd = 'dsage_setup.py client'
        os.system(cmd)

dsage = DistributedSage()
