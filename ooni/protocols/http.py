import random
from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.internet import protocol, defer
from ooni.plugoo.tests import ITest, OONITest
from ooni.plugoo.assets import Asset
from ooni.utils import log

import logging
logging.basicConfig(level=logging.DEBUG)

useragents = [("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.6) Gecko/20070725 Firefox/2.0.0.6", "Firefox 2.0, Windows XP"),
              ("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)", "Internet Explorer 7, Windows Vista"),
              ("Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)", "Internet Explorer 7, Windows XP"),
              ("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)", "Internet Explorer 6, Windows XP"),
              ("Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 5.1; .NET CLR 1.1.4322)", "Internet Explorer 5, Windows XP"),
              ("Opera/9.20 (Windows NT 6.0; U; en)", "Opera 9.2, Windows Vista"),
              ("Opera/9.00 (Windows NT 5.1; U; en)", "Opera 9.0, Windows XP"),
              ("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.50", "Opera 8.5, Windows XP"),
              ("Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 8.0", "Opera 8.0, Windows XP"),
              ("Mozilla/4.0 (compatible; MSIE 6.0; MSIE 5.5; Windows NT 5.1) Opera 7.02 [en]", "Opera 7.02, Windows XP"),
              ("Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.5) Gecko/20060127 Netscape/8.1", "Netscape 8.1, Windows XP")]

class BodyReceiver(protocol.Protocol):
    def __init__(self, finished):

        log.debug("BodyReceiver.__init__")

        self.finished = finished
        self.data = ""

    def dataReceived(self, bytes):

        log.debug("BodyReceiver.dataReceived")

        self.data += bytes

    def connectionLost(self, reason):

        log.debug("BodyReceiver.connectionLost")

        self.finished.callback(self.data)

from twisted.web.http_headers import Headers
class HTTPTest(OONITest):
    """
    A utility class for dealing with HTTP based testing. It provides methods to
    be overriden for dealing with HTTP based testing.
    The main functions to look at are processResponseBody and
    processResponseHeader that are invoked once the headers have been received
    and once the request body has been received.
    """
    randomize_ua = True
    follow_redirects = False

    def initialize(self):

        logging.debug("HTTPTest.initialize")

        from twisted.web.client import Agent
        import yaml

        self.agent = Agent(self.reactor)
        if self.follow_redirects:
            from twisted.web.client import RedirectAgent
            self.agent = RedirectAgent(self.agent)

        self.request = {}
        self.response = {}

    def _processResponseBody(self, data):

        log.debug("HTTPTest._processResponseBody")

        self.response['body'] = data
        #self.result['response'] = self.response
        self.processResponseBody(data)

    def processResponseBody(self, data):
        """
        This should handle all the response body smushing for getting it ready
        to be passed onto the control.

        @param data: The content of the body returned.
        """

        logging.debug("HTTPTest.processResponseBody")

    def processResponseHeaders(self, headers):
        """
        This should take care of dealing with the returned HTTP headers.

        @param headers: The content of the returned headers.
        """

        log.debug("HTTPTest.processResponseHeaders")

    def processRedirect(self, location):
        """
        Handle a redirection via a 3XX HTTP status code.

        @param location: the url that is being redirected to.
        """

        logging.debug("HTTPTest.processRedirect")


    def experiment(self, args):
        log.msg("HTTPTest.experiment")
        url = self.local_options['url'] if 'url' not in args else args['url']

        d = self.build_request(url)
        def finished(data):
            return data

        d.addCallback(self._cbResponse)
        d.addCallback(finished)
        return d

    def _cbResponse(self, response):

        log.debug("HTTPTest._cbResponse")

        self.response['headers'] = list(response.headers.getAllRawHeaders())
        self.response['code'] = response.code
        self.response['length'] = response.length
        self.response['version'] = response.length

        if str(self.response['code']).startswith('3'):
            self.processRedirect(response.headers.getRawHeaders('Location')[0])
        self.processResponseHeaders(self.response['headers'])
        #self.result['response'] = self.response

        finished = defer.Deferred()
        response.deliverBody(BodyReceiver(finished))
        finished.addCallback(self._processResponseBody)

    def randomize_useragent(self):

        log.debug("HTTPTest.randomize_useragent")

        user_agent = random.choice(useragents)
        self.request['headers']['User-Agent'] = [user_agent]

    def build_request(self, url, method="GET", headers=None, body=None):

        log.debug("HTTPTest.build_request")

        self.request['method'] = method
        self.request['url'] = url
        self.request['headers'] = headers if headers else {}
        self.request['body'] = body
        if self.randomize_ua:
            self.randomize_useragent()

        #self.result['request'] = self.request
        self.result['url'] = url
        return self.agent.request(self.request['method'], self.request['url'],
                                  Headers(self.request['headers']),
                                  self.request['body'])

    def load_assets(self):

        log.debug("HTTPTest.load_assets")

        if self.local_options:
            return {'url': Asset(self.local_options['asset'])}
        else:
            return {}

