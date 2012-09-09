from __future__ import with_statement

import os
import yaml

import itertools
from ooni.utils import log, date, net

import logging
logging.basicConfig(level=logging.DEBUG)

class Report:
    """This is the ooni-probe reporting mechanism. It allows
    reporting to multiple destinations and file formats.

    :scp the string of <host>:<port> of an ssh server

    :yaml the filename of a the yaml file to write

    :file the filename of a simple txt file to write

    :tcp the <host>:<port> of a TCP server that will just listen for
         inbound connection and accept a stream of data (think of it
         as a `nc -l -p <port> > filename.txt`)
    """
    def __init__(self, testname=None, file="report.log",
                 scp=None,
                 tcp=None):


        logging.debug("Report.__init__")

        self.testname = testname
        self.file = file
        self.tcp = tcp
        self.scp = scp
        #self.config = ooni.config.report

        #if self.config.timestamp:
        #    tmp = self.file.split('.')
        #    self.file = '.'.join(tmp[:-1]) + "-" + \
        #                datetime.now().isoformat('-') + '.' + \
        #                tmp[-1]
        #    print self.file

        self.scp = None
        self.write_header()

    def write_header(self):

        logging.debug("Report.write_header")

        pretty_date = date.pretty_date()
        header = "# OONI Probe Report for Test %s\n" % self.testname
        header += "# %s\n\n" % pretty_date
        self._write_to_report(header)
        # XXX replace this with something proper
        address = net.getClientAddress()
        test_details = {'start_time': str(date.now()),
                        'asn': address['asn'],
                        'test_name': self.testname,
                        'addr': address['ip']}
        self(test_details)

    def _write_to_report(self, dump):

        logging.debug("Report._write_to_report")

        reports = []

        if self.file:
            reports.append("file")

        if self.tcp:
            reports.append("tcp")

        if self.scp:
            reports.append("scp")

        #XXX make this non blocking
        for report in reports:
            self.send_report(dump, report)

    def __call__(self, data):
        """
        This should be invoked every time you wish to write some
        data to the reporting system
        """

        logging.debug("Report.__call__")

        dump = yaml.dump([data])
        self._write_to_report(dump)

    def file_report(self, data):
        """
        This reports to a file in YAML format
        """

        logging.debug("Report.file_report")

        with open(self.file, 'a+') as f:
            f.write(data)

    def send_report(self, data, type):
        """
        This sends the report using the
        specified type.
        """

        logging.debug("Report.send_report")

        #print "Reporting %s to %s" % (data, type)
        log.msg("Reporting to %s" % type)
        getattr(self, type+"_report").__call__(data)


