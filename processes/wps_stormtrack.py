import os
from c3stormtrack.processing import Stormtrack

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class StormtrackProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "stormtrack",
            title = "C3 Stormtrack",
            version = "2.3.0-0",
            abstract="Stormtrack calculates the standard deviation of bandpassfiltered geopotential height anomalies or air pressure at sea level anomalies."
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            minOccurs=1,
            maxOccurs=1000,
            maxmegabites=10000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.accu = self.addLiteralInput(
            identifier="accu",
            title="Accumulation Type",
            abstract="Choose accu type for Stormtrack. Default: complete.",
            default="complete",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["complete", "monthly", "seasonal"]
            )

        self.level = self.addLiteralInput(
            identifier="level",
            title="Level",
            abstract="Choose level [in Pa]. Default: 50000 hPA.",
            default=50000,
            type=type(50000),
            minOccurs=1,
            maxOccurs=1
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting stormtrack ...", 0)

        # TODO: run stormtracks in parallel
        stormtrack = Stormtrack(cache_dir='cache', output_dir='outputs')
        result = stormtrack.run(datasets=self.getInputValues(identifier='dataset'),
                       accu=self.accu.getValue(),
                       level=self.level.getValue())

        self.output.setValue( result )
        
        self.show_status("stormtrack: done", 100)


        
