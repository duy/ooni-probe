# ooni-probe - Open Observatory of Network Interference

"The Net interprets censorship as damage and routes around it."
                - John Gilmore; TIME magazine (6 December 1993)

OONI, the Open Observatory of Network Interference, is a global observation
network which aims is to collect high quality data using open methodologies,
using Free and Open Source Software (FL/OSS) to share observations and data
about the various types, methods, and amounts of network tampering in the world.

# Let's get started with this already!

To run OONI-probe without having to install it you must tell python that it can
import modules from the root of ooni-probe.

You must therefore run from the root of the repo:

    export PYTHONPATH=$PYTHONPATH:`pwd`

Then to see what tests are available:

    cd ooni
    python ooniprobe.py

If you see some errors see INSTALL to install the missing dependencies.

To list the help for a specific test:

    python ooniprobe.py httpt --help


# More details

With the belief that unfettered access to information is a intrinsic human right,
OONI seeks to observe levels of surveillance, censorship, and network discrimination
in order for people worldwide to have a clearer understanding of the ways in
which their access to information is filtered.

The end goal of OONI is to collect data which can show an accurate
topology of network interference and censorship. Through this topology, it will be
possible to see what the internet looks like from nearly any location, including
what sites are censored, or have been tampered with, and by whom. We're calling
it filternet.

OONI uses open methodologies and the data will be provided in raw
format to allow any researcher to indipendently draw their conclusions
from the results OONI tests.

There are currently projects aimed at measuring censorship in one
way or another but they either use non open methodologies or their
tools are not open sources. OONI aims at filling up this gap by
creating the first open source framework for developing network
tests and collecting data on censorship.

OONI revolves around three major concepts: Assets, Tests and
Reports.

## Assets

Assets are the inputs used inside Tests to detect censorship events.
These can be URL lists, keywords, ip addresses, packets or any kind
of set of data.
In the python specific implementation this is represented as a python
iterable object. This means that the Testing framework will be able
to iterate through every element in the Asset.

## Tests

This is the core of OONI. These are the actual tests that will be run
using as input (if an input is required) the Assets.
Tests can be summarized as an experiment and a control. The control
represents the expected result and the experiment is the network operation
being performed on the live network. If the experiment does not match up
with the control then a censorship event had occured.

OONI probe provides some useful functionality to the application developer
that may be useful when developing censorship detection tests. For example
it is possible to make a request over the Tor network easily or use a fast
and flexible non-blocking HTTP client implementation.

## Reports

This is the data that is collected from the test. OONI probe provides a
flexible means of storing results and uploading this data to a remote
server or a flat file.

The Test developer should include in the report as much data as possible
and can contain raw packet dumps as well as structured synthetic results.

In future on top of ooni-probe Reports it will be possible to develop
flexible post-processing tools to allow data-visualization guru's to
properly visualize and contextualize the resulting data.

