"""
Processes with cdo ensemble opertions
"""

from pywps.Process import WPSProcess
from malleefowl.process import show_status, getInputValues, mktempfile

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class Ensembles(WPSProcess):

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="ensembles",
            title="Ensembles Operations",
            version="0.2",
            metadata=[
                {"title":"CDO ens","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Calling cdo to calculate ensembles operations.",
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

        # operators
        self.operator = self.addLiteralInput(
            identifier="operator",
            title="Ensemble command",
            abstract="Choose a CDO Operator",
            default="ensmean",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['ensmin', 'ensmax', 'enssum', 'ensmean', 'ensavg', 'ensvar', 'ensstd', 'enspctl']
            )

        # complex output
        # -------------

        self.output = self.addComplexOutput(
            identifier="output",
            title="NetCDF Output",
            abstract="NetCDF Output",
            metadata=[],
            formats=[{"mimeType":"application/x-netcdf"}],
            asReference=True,
            )

    def execute(self):
        show_status(self, "starting cdo operator", 0)

        nc_files = getInputValues(self, identifier='dataset')

        out_filename = mktempfile(suffix='.nc')
        try:
            cmd = ["cdo", self.operator.getValue()]
            cmd.extend(nc_files)
            cmd.append(out_filename)
            self.cmd(cmd=cmd, stdout=True)
        except:
            logger.exception('cdo failed')
            raise
        show_status(self, "ensembles calculation done", 100)
        self.output.setValue( out_filename )
