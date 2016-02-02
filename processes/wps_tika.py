import os
import json
import tika
from tika import parser

from pywps.Process import WPSProcess

class Tika(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier="tika",
            title="Tika Metadata Parser",
            version="1.9.7-4",
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
        resources = self.getInputValues(identifier='resource')

        metadata = []
        for counter, resource in enumerate(resources):
            parsed = parser.from_file(resource)
            metadata.append( parsed["metadata"] )
            progress = int( counter * 100.0 / len(resources) )
            self.status.set("parsing {0}/{1}".format(counter, len(resources)), progress)

        with open('out.json', 'w') as fp:
            json.dump(obj=metadata, fp=fp, indent=4, sort_keys=True)
            self.output.setValue( fp.name )
        


        
