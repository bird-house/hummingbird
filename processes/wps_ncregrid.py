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

        self.namelist = self.addComplexInput(
            identifier="namelist",
            title="Namelist",
            abstract="Namelist",
            formats=[{"mimeType":"text/nml"}],
            )

        self.infile = self.addComplexInput(
            identifier="infile",
            title="Input File",
            abstract="Input File",
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.gridfile = self.addComplexInput(
            identifier="gridfile",
            title="Grid File",
            abstract="Grid File",
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Output File",
            abstract="Output File",
            metadata=[],
            formats=[{"mimeType":"application/x-netcdf"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting ncregrid operation", 10)

        namelist = self.getInputValue('namelist')
        infile   = self.getInputValue('infile')
        gridfile = self.getInputValue('gridfile')
        outfile  = self.mktempfile(suffix='.nc')
        alt_nml  = self.mktempfile(suffix='.nml')

        # Manipulate namelist to match actual file names.
        f = open(namelist, 'r')
        config = f.readlines()
        f.close()

        from os import path
        for i in range(len(config)):
            if config[i].startswith('infile'):
                config[i] = "infile = '" + path.abspath(infile) + "',\n"
            if config[i].startswith('grdfile'):
                config[i] = "grdfile = '" + path.abspath(gridfile) + "',\n"
            if config[i].startswith('outfile'):
                config[i] = "outfile = '" + path.abspath(outfile) + "',\n"

        f = open(alt_nml, 'w')
        f.writelines(config)
        f.close()

        # Delete empty outfile, otherwise ncregrid will fail.
        from os import remove
        remove(outfile)

        import subprocess
        ncregrid = 'ncregrid' # This seem to be okay, if ncregrid is copied to envs/birdhouse/bin/.
        proc = subprocess.Popen([ncregrid, alt_nml], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        ret = proc.communicate()

        self.show_status(ret[0].decode('utf-8'), 90)
        self.output.setValue(outfile)

        if proc.returncode != 0:
            return proc.returncode
