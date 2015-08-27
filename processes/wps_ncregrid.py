"""
Processes with ncregrid commands
"""

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)


class Ncregrid(WPSProcess):
    """Ncregrid"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = "ncregrid",
            title = "ncregrid",
            abstract = "A tool for rediscretisation of geo-data",
            metadata = [{"title":"ncregrid","href":"http://www.pa.op.dlr.de/~PatrickJoeckel/ncregrid/"}],
            version = '1.0', # Can this be ommited?
            )

        self.netcdf_file = self.addComplexInput(
            identifier="infile",
            title="NetCDF Input",
            abstract="NetCDF Input",
            formats=[{"mimeType":"application/x-netcdf"}],
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
        self.show_status("starting ncregrid operation", 10)

        infile = self.getInputValues('infile')

        import subprocess
        ncregrid = '/home/fklemme/bin/ncregrid' # TODO!
        proc = subprocess.Popen([ncregrid] + infile, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        ret = proc.communicate()

        self.show_status(ret[0].decode('utf-8'), 90)
        self.output.setValue(*infile) # is this correct?
