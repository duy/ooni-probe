"""
OONI logging facility.
"""
import sys
import logging
import warnings

from twisted.python import log

# Logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

def _get_log_level(level):
    if not level:
        return INFO
    else:
        return level

def start(logfile=None, loglevel=None, logstdout=True):
    if log.defaultObserver:
        print "%s" % logstdout
        loglevel = _get_log_level(loglevel)
        file = open(logfile, 'a') if logfile else sys.stderr
        observer = log.FileLogObserver(file)
        if logstdout:
            log.startLogging(sys.stdout)
        else:
            log.startLogging()
        log.addObserver(observer.emit)
        msg("Started OONI")

def msg(message, level=INFO, **kw):
    log.msg("INFO: " + message, logLevel=level, **kw)

def err(message, **kw):
    log.err("ERROR: " + message, **kw)

def debug(message, **kw):
    log.msg("DEBUG: " + message, logLevel=DEBUG, **kw)
