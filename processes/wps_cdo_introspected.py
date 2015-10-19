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

# Print some debug information to a local file.
import codecs
debugfile = codecs.open('debug_cdo_introspection.txt', 'w+', 'utf-8')
for k, v in wps.items():
    print >> debugfile, sorted(v)
    print >> debugfile, k, '\n\n'
debugfile.close()
