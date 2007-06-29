############################################################################
#
#   DSAGE: Distributed SAGE
#
#       Copyright (C) 2006, 2007 Yi Qiang <yqiang@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
############################################################################

import ConfigParser
import os
import random
from glob import glob
import cPickle
import zlib
import uuid
import base64

from twisted.trial import unittest
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred import portal, credentials
from twisted.conch.ssh import keys
from twisted.python import log

from sage.dsage.twisted.pb import Realm
from sage.dsage.server.server import DSageServer
from sage.dsage.twisted.pb import _SSHKeyPortalRoot
from sage.dsage.twisted.pb import PBClientFactory
from sage.dsage.twisted.pubkeyauth import PublicKeyCredentialsCheckerDB
from sage.dsage.database.jobdb import JobDatabaseSQLite
from sage.dsage.database.monitordb import MonitorDatabase
from sage.dsage.database.clientdb import ClientDatabase
from sage.dsage.database.job import Job
from sage.dsage.errors.exceptions import BadJobError
from sage.dsage.misc.hostinfo import ClassicHostInfo
from sage.dsage.twisted.tests.test_pubkeyauth import TEST_PUB_KEY
from sage.dsage.twisted.tests.test_pubkeyauth import TEST_PRIV_KEY

DSAGE_DIR = os.path.join(os.getenv('DOT_SAGE'), 'dsage')
hf = ClassicHostInfo().host_info
hf['uuid'] = ''
hf['workers'] = 2

RANDOM_DATA =  ''.join([chr(i) for i in [random.randint(65, 123) for n in
                       range(500)]])

class ClientRemoteCallsTest(unittest.TestCase):
    """
    Tests of remote procedure calls go here.

    """

    def unpickle(self, pickled_job):
        return cPickle.loads(zlib.decompress(pickled_job))

    def setUp(self):
        self.jobdb = JobDatabaseSQLite(test=True)
        self.monitordb = MonitorDatabase(test=True)
        self.clientdb = ClientDatabase(test=True)
        self.dsage_server = DSageServer(self.jobdb,
                                        self.monitordb,
                                        self.clientdb,
                                        log_level=5)
        self.realm = Realm(self.dsage_server)
        self.p = _SSHKeyPortalRoot(portal.Portal(self.realm))
        self.clientdb = ClientDatabase(test=True)
        self.p.portal.registerChecker(
                            PublicKeyCredentialsCheckerDB(self.clientdb))
        self.client_factory = pb.PBServerFactory(self.p)
        self.hostname = 'localhost'
        self.server = reactor.listenTCP(0, self.client_factory)
        self.port = self.server.getHost().port

        # public key authentication information
        self.username = 'unit_test'
        self.pubkey_file = TEST_PUB_KEY
        self.privkey_file = TEST_PRIV_KEY
        self.data = RANDOM_DATA
        self.public_key_str = keys.getPublicKeyString(data=TEST_PUB_KEY)
        self.private_key = keys.getPrivateKeyObject(
                            data=TEST_PRIV_KEY)
        self.public_key = keys.getPublicKeyObject(self.public_key_str)
        self.algorithm = 'rsa'
        self.blob = keys.makePublicKeyBlob(self.public_key)
        self.signature = keys.signData(self.private_key, self.data)
        self.creds = credentials.SSHPrivateKey(self.username,
                                               self.algorithm,
                                               self.blob,
                                               self.data,
                                               self.signature)
        pubkey = base64.encodestring(self.public_key_str).strip()
        try:
            self.clientdb.del_user(self.username)
            self.clientdb.add_user(self.username, pubkey)
        except:
            self.clientdb.add_user(self.username, pubkey)

    def tearDown(self):
        self.connection.disconnect()
        self.jobdb._shutdown()
        files = glob('*.db*')
        for file in files:
            os.remove(file)
        return self.server.stopListening()

    def _catch_failure(self, failure, *args):
        log.msg("Error: ", failure.getErrorMessage())
        log.msg("Traceback: ", failure.printTraceback())

    def testremoteSubmitJob(self):
        """tests perspective_submit_job"""
        jobs = self.create_jobs(1)

        factory = PBClientFactory()
        self.connection = reactor.connectTCP(self.hostname,
                                             self.port,
                                             factory)

        d = factory.login(self.creds, None)
        d.addCallback(self._LoginConnected2, jobs)
        return d

    def _LoginConnected2(self, remoteobj, jobs):
        job = jobs[0]
        job.code = "2+2"
        d = remoteobj.callRemote('submit_job', job.reduce())
        d.addCallback(self._got_job_id)
        return d

    def _got_job_id(self, job_id):
        self.assertEquals(type(job_id), str)

    def testremoteSubmitBadJob(self):
        """tests perspective_submit_job"""

        factory = PBClientFactory()
        self.connection = reactor.connectTCP(self.hostname,
                                             self.port,
                                             factory)

        d = factory.login(self.creds, None)
        d.addCallback(self._LoginConnected3)
        return d

    def _LoginConnected3(self, remoteobj):
        d = remoteobj.callRemote('submit_job', None)
        d.addErrback(self._gotNoJobID)
        return d

    def _gotNoJobID(self, failure):
        self.assertEquals(BadJobError, failure.check(BadJobError))

    def create_jobs(self, n):
        """This method creates n jobs. """

        jobs = []
        for i in range(n):
            jobs.append(Job(name='unittest', username=self.username))

        return jobs

class MonitorRemoteCallsTest(unittest.TestCase):
    """
    Tests remote calls for monitors.

    """

    def setUp(self):
        self.jobdb = JobDatabaseSQLite(test=True)
        self.monitordb = MonitorDatabase(test=True)
        self.clientdb = ClientDatabase(test=True)
        self.dsage_server = DSageServer(self.jobdb,
                                        self.monitordb,
                                        self.clientdb,
                                        log_level=5)
        self.realm = Realm(self.dsage_server)
        self.p = _SSHKeyPortalRoot(portal.Portal(self.realm))
        self.p.portal.registerChecker(
        PublicKeyCredentialsCheckerDB(self.clientdb))
        self.client_factory = pb.PBServerFactory(self.p)
        self.hostname = 'localhost'
        self.server = reactor.listenTCP(0, self.client_factory)
        self.port = self.server.getHost().port

        # public key authentication information
        self.username = 'unit_test'
        self.pubkey_file = TEST_PUB_KEY
        self.privkey_file = TEST_PRIV_KEY
        self.data = RANDOM_DATA
        self.public_key_str = keys.getPublicKeyString(data=TEST_PUB_KEY)
        self.private_key = keys.getPrivateKeyObject(
                            data=TEST_PRIV_KEY)
        self.public_key = keys.getPublicKeyObject(self.public_key_str)
        self.algorithm = 'rsa'
        self.blob = keys.makePublicKeyBlob(self.public_key)
        self.signature = keys.signData(self.private_key, self.data)
        self.creds = credentials.SSHPrivateKey(self.username,
                                               self.algorithm,
                                               self.blob,
                                               self.data,
                                               self.signature)
        pubkey = base64.encodestring(self.public_key_str).strip()
        try:
            self.clientdb.del_user(self.username)
            self.clientdb.add_user(self.username, pubkey)
        except:
            self.clientdb.add_user(self.username, pubkey)

    def tearDown(self):
        self.connection.disconnect()
        self.jobdb._shutdown()
        files = glob('*.db*')
        for file in files:
            os.remove(file)
        return self.server.stopListening()

    def testremote_get_job(self):
        job = Job()
        job.code = "2+2"
        self.dsage_server.submit_job(job.reduce())
        factory = PBClientFactory()
        self.connection = reactor.connectTCP(self.hostname,
                                             self.port,
                                             factory)
        d = factory.login(self.creds, (pb.Referenceable(), hf))
        d.addCallback(self._logged_in)
        d.addCallback(self._get_job)

        return d

    def _logged_in(self, remoteobj):
        self.assert_(remoteobj is not None)

        return remoteobj

    def _get_job(self, remoteobj):
        d = remoteobj.callRemote('get_job')
        d.addCallback(self._got_job)

        return d

    def _got_job(self, jdict):
        self.assertEquals(type(jdict), dict)

    def testremote_job_done(self):
        factory = PBClientFactory()
        self.connection = reactor.connectTCP(self.hostname, self.port,
                                             factory)
        d = factory.login(self.creds, (pb.Referenceable(), hf))
        job = Job()
        job.code = "2+2"
        job_id = self.dsage_server.submit_job(job.reduce())
        jdict = self.dsage_server.get_job_by_id(job_id)
        d.addCallback(self._logged_in)
        d.addCallback(self._job_done, jdict)

        return d

    def _job_done(self, remoteobj, jdict):
        import time
        job_id = jdict['job_id']
        result = jdict['result']
        d = remoteobj.callRemote('job_done', job_id,
                                 'Nothing.', result, False,
                                 time.time() - time.time())
        d.addCallback(self._done_job)

        return d

    def _done_job(self, job_id):
        self.assertEquals(type(job_id), str)
        jdict = self.dsage_server.get_job_by_id(job_id)
        self.assertEquals(jdict['status'], 'new')
        self.assertEquals(jdict['output'], 'Nothing.')

    def testremote_job_failed(self):
        factory = PBClientFactory()
        self.connection = reactor.connectTCP(self.hostname,
                                             self.port,
                                             factory)
        job = Job()
        job.code = "2+2"
        job_id = self.dsage_server.submit_job(job.reduce())
        jdict = self.dsage_server.get_job_by_id(job_id)
        d = factory.login(self.creds, (pb.Referenceable(), hf))
        d.addCallback(self._logged_in)
        d.addCallback(self._job_failed, jdict)

        return d

    def _job_failed(self, remoteobj, jdict):
        d = remoteobj.callRemote('job_failed', jdict['job_id'], 'Failure')
        d.addCallback(self._failed_job)

        return d

    def _failed_job(self, job_id):
        self.assertEquals(type(job_id), str)
        jdict = self.dsage_server.get_job_by_id(job_id)
        self.assertEquals(jdict['failures'], 1)
        self.assertEquals(jdict['output'], 'Failure')

    def testget_killed_jobs_list(self):
        factory = PBClientFactory()
        self.connection = reactor.connectTCP(self.hostname,
                                             self.port,
                                             factory)

        job = Job()
        job.code = "2+2"
        job.killed = True
        job_id = self.dsage_server.submit_job(job.reduce())
        jdict = self.dsage_server.get_job_by_id(job_id)
        d = factory.login(self.creds, (pb.Referenceable(), hf))
        d.addCallback(self._logged_in)
        d.addCallback(self._get_killed_jobs_list)
        d.addCallback(self._got_killed_jobs_list, jdict)

        return d

    def _get_killed_jobs_list(self, remoteobj):
        d = remoteobj.callRemote('get_killed_jobs_list')

        return d

    def _got_killed_jobs_list(self, killed_jobs_list, jdict):
        self.assertEquals(len(killed_jobs_list), 1)
        self.assertEquals(killed_jobs_list[0]['job_id'], jdict['job_id'])


if __name__ == 'main':
    unittest.main()
