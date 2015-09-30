"""
Provide all CDO Operations
"""

from malleefowl.process import WPSProcess

from cdo import Cdo

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)


cdo = Cdo()
wps = dict()

# Sort all operations into groups.
for op in cdo.operators:
    key = getattr(cdo, op).__doc__
    if key not in wps:
        wps[key] = [op]
    else:
        wps[key].append(op)

# TODO...
debugfile = open('debugoutput.txt', 'a')
for k, v in wps:
    print >> debugfile, sorted(v)
    print >> debugfile, k, '\n\n'
debugfile.close()
