"""
Processes with cdo ensemble opertions
"""
import tempfile
from pywps.Process import WPSProcess

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
        nc_files = self.getInputValues(identifier='dataset')

        _,out_filename = tempfile.mkstemp(suffix='.nc')
        try:
            cmd = ["cdo", self.operator.getValue()]
            cmd.extend(nc_files)
            cmd.append(out_filename)
            self.cmd(cmd=cmd, stdout=True)
        except:
            logging.exception('cdo failed')
            raise
        self.output.setValue( out_filename )
