"""
Processes with cdo commands
"""

from malleefowl.process import WPSProcess

from cdo import Cdo

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class CDOOperation(WPSProcess):
    """This process calls cdo with operation on netcdf file"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = "cdo_operation",
            title = "CDO Operation",
            version = "0.1",
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO Operation like monmax on NetCDF File.",
            )

        self.cdo = Cdo()

        self.netcdf_file = self.addComplexInput(
            identifier="netcdf_file",
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
            allowedValues=sorted(self.cdo.operators),
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
        self.show_status("starting cdo operator", 10)

        nc_files = self.getInputValues(identifier='netcdf_file')
        operator = self.operator.getValue()

        cdo_op = getattr(self.cdo, operator)

        outfile = self.mktempfile(suffix='.nc')
        cdo_op(input= " ".join(nc_files), output=outfile)
        
        self.show_status("cdo operator done", 90)
        self.output.setValue( outfile )


class CDOInfo(WPSProcess):
    """This process calls cdo sinfo on netcdf file"""

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = "cdo_sinfo",
            title = "CDO sinfo",
            version = "0.1",
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO sinfo on NetCDF File.",
            )

        self.netcdf_file = self.addComplexInput(
            identifier="netcdf_file",
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
        self.show_status("starting cdo sinfo", 0)

        cdo = Cdo()

        nc_files = self.getInputValues(identifier='netcdf_file')

        outfile = self.mktempfile(suffix='.txt')
        with open(outfile, 'w') as fp: 
            for nc_file in nc_files:
                sinfo = cdo.sinfo(input=nc_file, output=outfile)
                for line in sinfo:
                    fp.write(line + '\n')
                fp.write('\n\n')

        self.show_status("cdo sinfo done", 90)

        self.output.setValue( outfile )
