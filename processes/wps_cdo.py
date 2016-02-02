"""
Processes with cdo commands
"""
from cdo import Cdo

from pywps.Process import WPSProcess

import logging

class CDOOperation(WPSProcess):
    """This process calls cdo with operation on netcdf file"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_operation",
            title="CDO Operation",
            version="0.4",
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO Operation like monmax on NetCDF File.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.operator = self.addLiteralInput(
            identifier="operator",
            title="CDO Operator",
            abstract="Choose a CDO Operator",
            default="monmax",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['merge', 'dayavg', 'daymax', 'daymean', 'daymin','daysum', 'dayvar',    'daystd', 'monmax', 'monmin', 'monmean', 'monavg', 'monsum', 'monvar', 'monstd', 'ymonmin', 'ymonmax', 'ymonsum', 'ymonmean', 'ymonavg', 'ymonvar', 'ymonstd', 'yearavg', 'yearmax', 'yearmean', 'yearmin', 'yearsum', 'yearvar', 'yearstd', 'yseasvar']
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="NetCDF Output",
            abstract="NetCDF Output",
            formats=[{"mimeType":"application/x-netcdf"}],
            asReference=True,
            )

    def execute(self):
        datasets = self.getInputValues(identifier='dataset')
        logging.debug("datasets %s", datasets)
        operator = self.operator.getValue()

        cdo = Cdo()
        cdo_op = getattr(cdo, operator)
        
        outfile = 'out.nc'
        input_files = " ".join(datasets)
        logging.debug("inputs = %s", input_files)
        cdo_op(input=input_files, output=outfile)

        self.output.setValue( outfile )
        
        self.status.set("cdo operator done", 100)


class CDOInfo(WPSProcess):
    """This process calls cdo sinfo on netcdf file"""

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_sinfo",
            title="CDO sinfo",
            version="0.4",
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO sinfo on NetCDF File.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CDO sinfo result",
            abstract="CDO sinfo result",
            metadata=[],
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        cdo = Cdo()

        datasets = self.getInputValues(identifier='dataset')

        with open('out.txt', 'w') as fp: 
            for ds in datasets:
                sinfo = cdo.sinfo(input=ds, output=outfile)
                for line in sinfo:
                    fp.write(line + '\n')
                fp.write('\n\n')
            self.output.setValue( fp.name )
            self.status.set("cdo sinfo done", 100)

        
