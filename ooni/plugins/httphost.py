"""
    HTTP Host based filtering
    *************************

    This test detect HTTP Host field
    based filtering.
"""
import os
from datetime import datetime

import urllib2
import httplib
try:
    from BeautifulSoup import BeautifulSoup
except:
    print "Beautiful Soup not installed. HTTPHost may not work"

# XXX reduce boilerplating.
from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin

from ooni.plugoo.assets import Asset
from ooni.plugoo.tests import ITest, OONITest

import logging
logging.basicConfig(level=logging.DEBUG)

class HTTPHostArgs(usage.Options):
    optParameters = [['asset', 'a', None, 'Asset file'],
                     ['controlserver', 'c', 'google.com', 'Specify the control server'],
                     ['resume', 'r', 0, 'Resume at this index'],
                     ['other', 'o', None, 'Other arguments']]
    def control(self, experiment_result, args):
        print "Experiment Result:", experiment_result
        print "Args", args
        return experiment_result

    def experiment(self, args):
        import urllib
        req = urllib.urlopen(args['asset'])
        return {'page': req.readlines()}

class HTTPHostAsset(Asset):
    """
    This is the asset that should be used by the Test. It will
    contain all the code responsible for parsing the asset file
    and should be passed on instantiation to the test.
    """
    def __init__(self, file=None):
        self = Asset.__init__(self, file)

    def parse_line(self, line):
        return line.split(',')[1].replace('\n','')


class HTTPHostTest(OONITest):
    implements(IPlugin, ITest)

    shortName = "httphost"
    description = "HTTP Host plugin"
    requirements = None
    options = HTTPHostArgs
    # Tells this to be blocking.
    blocking = True

    logging.debug("HTTPHostTest")

    def check_response(self, response):
        soup = BeautifulSoup(response)
        if soup.head.title.string == "Blocked":
            # Response indicates censorship
            return True
        else:
            # Response does not indicate censorship
            return False

    def is_censored(self, response):
        if response:
            soup = BeautifulSoup(response)
            censored = self.check_response(response)
        else:
            censored = "unreachable"
        return censored

    def urllib2_test(self, control_server, host):
        req = urllib2.Request(control_server)
        req.add_header('Host', host)
        try:
            r = urllib2.urlopen(req)
            response = r.read()
            censored = self.is_censored(response)
        except Exception, e:
            censored = "Error! %s" % e

        return censored

    def httplib_test(self, control_server, host):
        censored = None
        response = None
        try:
            conn = httplib.HTTPConnection(control_server)
            conn.putrequest("GET", "", skip_host=True, skip_accept_encoding=True)
            conn.putheader("Host", host)
            conn.putheader("User-Agent", "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6")
            conn.endheaders()
            r = conn.getresponse()
            response = r.read()
            censored = self.is_censored(response)
        except Exception, e:
            censored = "Error! %s" % e

        return (censored, response)

    def experiment(self, args):
        control_server = self.local_options['controlserver']
        url = 'http://torproject.org/' if not 'asset' in args else args['asset']
        censored = self.httplib_test(control_server, url)
        return {'control': control_server,
                'host': url,
                'censored': censored}

    def load_assets(self):
        if self.local_options and self.local_options['asset']:
            return {'asset': Asset(self.local_options['asset'])}
        else:
            return {}

httphost = HTTPHostTest(None, None, None)
