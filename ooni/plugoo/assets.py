from ooni.utils import log

import logging
logging.basicConfig(level=logging.DEBUG)

class Asset:
    """
    This is an ooni-probe asset. It is a python
    iterator object, allowing it to be efficiently looped.
    To create your own custom asset your should subclass this
    and override the next_asset method and the len method for
    computing the length of the asset.
    """
    def __init__(self, file=None, *args, **argv):

        log.debug("Asset.__init__")

        self.fh = None
        if file:
            self.name = file
            self.fh = open(file, 'r')
        self.eof = False

    def __iter__(self):

        log.debug("Asset.__iter__")

        return self

    def len(self):
        """
        Returns the length of the asset
        """

        log.debug("Asset.len")

        for i, l in enumerate(self.fh):
            pass
        # rewind the file
        self.fh.seek(0)
        return i + 1

    def parse_line(self, line):
        """
        Override this method if you need line
        by line parsing of an Asset.
        """

        log.debug("Asset.parse_line")

        return line.replace('\n','')

    def next_asset(self):
        """
        Return the next asset.
        """

        log.debug("Asset.next_asset")

        # XXX this is really written with my feet.
        #     clean me up please...
        line = self.fh.readline()
        if line:
            parsed_line = self.parse_line(line)
            if parsed_line:
                return parsed_line
        else:
            self.fh.seek(0)
            raise StopIteration

    def next(self):

        log.debug("Asset.next")

        try:
            return self.next_asset()
        except:
            raise StopIteration

