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
for doc, ops in wps.items():
    print >> debugfile, sorted(ops)
    print >> debugfile, doc, '\n\n'
debugfile.close()

# Generate WPSs from operation documentation.
for doc, ops, in wps.items():
    # Get NAME from documentation.
    import re
    match = re.search('NAME(.*?)SYNOPSIS', doc, re.MULTILINE | re.DOTALL)
    if match is not None:
        name = match.group(1)
        # Remove redundant whitespace.
        name = re.sub('\s+', ' ', name).strip()

        #print 'CDO:', name # just testing

        # Add WPS for these operations.
        # TODO: This class is being overridden all the time. Maybe fix it with 'type'?
        class TempClassName(WPSProcess):
            def __init__(self):
                WPSProcess.__init__(
                        self,
                        identifier = 'cdo_%s' % ''.join(ops),
                        title = 'CDO: %s' % name,
                        version = "0.1"
                        )

                self.operator = self.addLiteralInput(
                        identifier = 'operatior',
                        title = 'CDO operator',
                        type = type(''),
                        allowedValues = sorted(ops)
                        )

                # TODO: Inputs / Outputs

            def execute(self):
                self.show_status("starting cdo operator", 10)

                # TODO...

                self.show_status("cdo operator done", 90)
