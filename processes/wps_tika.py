import os

from pywps.Process import WPSProcess
from malleefowl.process import show_status, getInputValues, mktempfile

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class Tika(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier="tika",
            title="Tika Metadata Parser",
            version="1.9.7-2",
            abstract="Extracts Metadata of Files",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="Dataset (NetCDF)",
            minOccurs=1,
            maxOccurs=1000,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Tika Result",
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting ...", 0)

        resources = getInputValues(self, identifier='resource')

        import tika
        from tika import parser

        metadata = []
        for counter, resource in enumerate(resources):
            parsed = parser.from_file(resource)
            metadata.append( parsed["metadata"] )
            progress = int( counter * 100.0 / len(resources) )
            show_status(self, "parsing {0}/{1}".format(counter, len(resources)), progress)

        import json
        out_filename = mktempfile(suffix='.json')
        with open(out_filename, 'w') as fp:
            json.dump(obj=metadata, fp=fp, indent=4, sort_keys=True)
        self.output.setValue( out_filename )
        
        show_status(self, "done", 100)


        
