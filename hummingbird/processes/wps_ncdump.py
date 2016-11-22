import os

from pywps.Process import WPSProcess


class NCDump(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="ncdump",
            title="NCDump",
            version="4.4.1",
            abstract="Run ncdump to retrieve netcdf header metadata",
            statusSupported=True,
            storeSupported=True)

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            abstract="URL to NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=1000,
            formats=[{"mimeType": "application/x-netcdf"}],
        )

        self.output = self.addComplexOutput(
            identifier="output",
            title="NetCDF Metadata",
            abstract="NetCDF Metadata",
            formats=[{"mimeType": "text/plain"}],
            asReference=True,
        )

    def execute(self):
        from hummingbird.processing import ncdump
        datasets = self.getInputValues(identifier='dataset')

        count = 0
        with open("nc_dump.txt", 'w') as fp:
            self.output.setValue(fp.name)
            for dataset in datasets:
                self.status.set("running ncdump", int(count * 100.0 / len(datasets)))
                fp.writelines(ncdump(dataset))
                count = count + 1
        self.status.set("compliance checker finshed.", 100)
