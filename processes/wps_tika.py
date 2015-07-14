import os

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class Tika(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "tika",
            title = "Tika Metadata Parser",
            version = "0.1",
            abstract="Extracts Metadata of Files")

        self.resource = self.addComplexInput(
            identifier="resource",
            title="File",
            minOccurs=1,
            maxOccurs=100,
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
        self.show_status("starting tika", 0)

        resources = self.getInputValues(identifier='resource')

        import tika
        from tika import parser

        metadata = []
        for resource in resources:
            parsed = parser.from_file(resource)
            metadata.append( parsed["metadata"] )

        import json
        out_filename = self.mktempfile(suffix='.json')
        with open(out_filename, 'w') as fp:
            json.dump(obj=metadata, fp=fp, indent=4, sort_keys=True)
        self.output.setValue( out_filename )
        
        self.show_status("tika done", 100)


        
