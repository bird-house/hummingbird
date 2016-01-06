"""
Processes with cdo commands
"""

from pywps.Process import WPSProcess
from malleefowl.process import show_status, getInputValues, mktempfile
from cdo import Cdo

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class CDOOperation(WPSProcess):
    """This process calls cdo with operation on netcdf file"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_operation",
            title="CDO Operation",
            version="0.2",
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
            metadata=[],
            formats=[{"mimeType":"application/x-netcdf"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting cdo operator", 10)

        datasets = getInputValues(self, identifier='dataset')
        operator = self.operator.getValue()

        cdo = Cdo()
        cdo_op = getattr(cdo, operator)

        outfile = mktempfile(suffix='.nc')
        cdo_op(input= " ".join(datasets), output=outfile)
        
        show_status(self, "cdo operator done", 90)
        self.output.setValue( outfile )


class CDOInfo(WPSProcess):
    """This process calls cdo sinfo on netcdf file"""

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_sinfo",
            title="CDO sinfo",
            version="0.2",
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
        show_status(self, "starting cdo sinfo", 0)

        cdo = Cdo()

        datasets = getInputValues(self, identifier='dataset')

        outfile = mktempfile(suffix='.txt')
        with open(outfile, 'w') as fp: 
            for ds in datasets:
                sinfo = cdo.sinfo(input=ds, output=outfile)
                for line in sinfo:
                    fp.write(line + '\n')
                fp.write('\n\n')

        show_status(self, "cdo sinfo done", 90)

        self.output.setValue( outfile )
