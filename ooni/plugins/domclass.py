# -*- coding: utf-8 -*-
#
#
#    domclass
#    ********
#
#    :copyright: (c) 2012 by Arturo Filastò
#    :license: see LICENSE for more details.
#
#    how this works
#    --------------
#
#    This classifier uses the DOM structure of a website to determine how similar
#    the two sites are.
#    The procedure we use is the following:
#        * First we parse all the DOM tree of the web page and we build a list of
#          TAG parent child relationships (ex. <html><a><b></b></a><c></c></html> =>
#          (html, a), (a, b), (html, c)).
#
#        * We then use this information to build a matrix (M) where m[i][j] = P(of
#          transitioning from tag[i] to tag[j]). If tag[i] does not exists P() = 0.
#          Note: M is a square matrix that is number_of_tags wide.
#
#        * We then calculate the eigenvectors (v_i) and eigenvalues (e) of M.
#
#        * The corelation between page A and B is given via this formula:
#          correlation = dot_product(e_A, e_B), where e_A and e_B are
#          resepectively the eigenvalues for the probability matrix A and the
#          probability matrix B.
#

from zope.interface import implements
from twisted.python import usage
from twisted.plugin import IPlugin
from ooni.plugoo.tests import ITest, OONITest
from ooni.plugoo.assets import Asset
from ooni.utils import log
from ooni.protocols.http import HTTPTest

import logging
logging.basicConfig(level=logging.DEBUG)

class domclassArgs(usage.Options):
    optParameters = [['output', 'o', None, 'Output to write'],
                     ['file', 'f', None, 'Corpus file'],
                     ['fileb', 'b', None, 'Corpus file'],
                     ['asset', 'a', None, 'URL List'],
                     ['resume', 'r', 0, 'Resume at this index'],
                    ]

# All HTML4 tags
# XXX add link to W3C page where these came from
alltags = ['A', 'ABBR', 'ACRONYM', 'ADDRESS', 'APPLET', 'AREA', 'B', 'BASE',
           'BASEFONT', 'BD', 'BIG', 'BLOCKQUOTE', 'BODY', 'BR', 'BUTTON', 'CAPTION',
           'CENTER', 'CITE', 'CODE', 'COL', 'COLGROUP', 'DD', 'DEL', 'DFN', 'DIR', 'DIV',
           'DL', 'DT', 'E M', 'FIELDSET', 'FONT', 'FORM', 'FRAME', 'FRAMESET', 'H1', 'H2',
           'H3', 'H4', 'H5', 'H6', 'HEAD', 'HR', 'HTML', 'I', 'IFRAME ', 'IMG',
           'INPUT', 'INS', 'ISINDEX', 'KBD', 'LABEL', 'LEGEND', 'LI', 'LINK', 'MAP',
           'MENU', 'META', 'NOFRAMES', 'NOSCRIPT', 'OBJECT', 'OL', 'OPTGROUP', 'OPTION',
           'P', 'PARAM', 'PRE', 'Q', 'S', 'SAMP', 'SCRIPT', 'SELECT', 'SMALL', 'SPAN',
           'STRIKE', 'STRONG', 'STYLE', 'SUB', 'SUP', 'TABLE', 'TBODY', 'TD',
           'TEXTAREA', 'TFOOT', 'TH', 'THEAD', 'TITLE', 'TR', 'TT', 'U', 'UL', 'VAR']

# Reduced subset of only the most common tags
commontags = ['A', 'B', 'BLOCKQUOTE', 'BODY', 'BR', 'BUTTON', 'CAPTION',
           'CENTER', 'CITE', 'CODE', 'COL', 'DD', 'DIV',
           'DL', 'DT', 'EM', 'FIELDSET', 'FONT', 'FORM', 'FRAME', 'FRAMESET', 'H1', 'H2',
           'H3', 'H4', 'H5', 'H6', 'HEAD', 'HR', 'HTML', 'IFRAME ', 'IMG',
           'INPUT', 'INS', 'LABEL', 'LEGEND', 'LI', 'LINK', 'MAP',
           'MENU', 'META', 'NOFRAMES', 'NOSCRIPT', 'OBJECT', 'OL', 'OPTION',
           'P', 'PRE', 'SCRIPT', 'SELECT', 'SMALL', 'SPAN',
           'STRIKE', 'STRONG', 'STYLE', 'SUB', 'SUP', 'TABLE', 'TBODY', 'TD',
           'TEXTAREA', 'TFOOT', 'TH', 'THEAD', 'TITLE', 'TR', 'TT', 'U', 'UL']

# The tags we are interested in using for our analysis
thetags = ['A', 'DIV', 'FRAME', 'H1', 'H2',
           'H3', 'H4', 'IFRAME ', 'INPUT',
           'LABEL','LI', 'P', 'SCRIPT', 'SPAN',
           'STYLE', 'TR']

def compute_probability_matrix(dataset):
    """
    Compute the probability matrix based on the input dataset.

    :dataset: an array of pairs representing the parent child relationships.
    """
    import itertools
    import numpy
    ret = {}
    # create a matrix of 0s of size the number of interested tags +1 = 17x17
    matrix = numpy.zeros((len(thetags) + 1, len(thetags) + 1))

    # put 1s in the matrix in the row x, column y, being x,y the position of the
    # tags in thetags
    # if the tag is not in the tag, then use row or column 16 (the len of 
    # thetags)
    # for instance, (html, div) => (16,1),(div,a) => (1,0),(html,h1)=> (16,3)

    for data in dataset:
        x = data[0].upper()
        y = data[1].upper()
        try:
            x = thetags.index(x)
        except:
            x = len(thetags)

        try:
            y = thetags.index(y)
        except:
            y = len(thetags)

        matrix[x,y] += 1

    # walk through every row
    # xrange is 17
    for x in xrange(len(thetags) + 1):
        # sum all the elements in the row => number of 1s in the row
        possibilities = 0
        # matrix[x] have 17 elements
        for y in matrix[x]:
            possibilities += y

        # xrange is 17
        # replace 1s by  1 / the sum of the 1s of that row 
        for i in xrange(len(matrix[x])):
            if possibilities != 0:
                matrix[x][i] = matrix[x][i]/possibilities


    return matrix

def compute_eigenvalues(matrix):
    """
    Returns the eigenvalues of the supplied square matrix.

    :matrix: must be a square matrix and diagonalizable.
    """
    import numpy
    return numpy.linalg.eigvals(matrix)

def readDOM(content=None, filename=None):
    """
    Parses the DOM of the HTML page and returns an array of parent, child
    pairs.

    :content: the content of the HTML page to be read.

    :filename: the filename to be read from for getting the content of the
               page.
    """
    from bs4 import BeautifulSoup

    if filename:
        f = open(filename)
        content = ''.join(f.readlines())
        f.close()

    dom = BeautifulSoup(content)
    couples = []
    for x in dom.findAll():
        couples.append((str(x.parent.name), str(x.name)))

    return couples

class domclassTest(HTTPTest):

    logging.debug("domclassTest")

    implements(IPlugin, ITest)

    shortName = "domclass"
    description = "domclass"
    requirements = None
    options = domclassArgs
    blocking = False
    follow_redirects = True
    #FIXME: it's needed to run runTool, but then it's not threaded
    #tool = True

    def runTool(self):
    
        log.debug("domclassTest.runTool")
        self.a = {}
        self.b = {}

        #import yaml, numpy
        import numpy
        site_a = readDOM(filename=self.local_options['file'])
        site_b = readDOM(filename=self.local_options['fileb'])
        self.a['matrix'] = compute_probability_matrix(site_a)
        self.a['eigen'] = compute_eigenvalues(self.a['matrix'])

        self.result['eigenvalues'] = self.a['eigen']
        self.b['matrix'] = compute_probability_matrix(site_b)
        self.b['eigen'] = compute_eigenvalues(self.b['matrix'])

        #print "A: %s" % a
        #print "B: %s" % b
        correlation = numpy.vdot(self.a['eigen'],self.b['eigen'])
        correlation /= numpy.linalg.norm(self.a['eigen'])*numpy.linalg.norm(self.b['eigen'])
        correlation = (correlation + 1)/2
        print "Corelation: %s" % correlation

        #self.finished({})

    def processResponseBody(self, data):
    
        log.debug("domclassTest.processResponseBody")
        self.a = {}
        self.b = {}

        #import yaml, numpy
        site_a = readDOM(data)
        #site_b = readDOM(self.local_options['fileb'])
        self.a['matrix'] = compute_probability_matrix(site_a)
        self.a['eigen'] = compute_eigenvalues(self.a['matrix'])


        if len(data) == 0:
            self.result['eigenvalues'] = None
            self.result['matrix'] = None
        else:
            self.result['eigenvalues'] = self.a['eigen']
            #self.result['matrix'] = self.a['matrix']
        #self.result['content'] = data[:200]
        #self.b = compute_matrix(site_b)
        print "A: %s" % self.a
        return self.a['eigen']

domclass = domclassTest(None, None, None)
