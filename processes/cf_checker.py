import os

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class CFCheckerProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "cfchecker",
            title = "CF Checker",
            version = "0.1",
            abstract="The cfchecker checks NetCDF files for compliance to the CF standard."
            )

        self.resource = self.addComplexInput(
            identifier="resource",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.cf_version = self.addLiteralInput(
            identifier="cf_version",
            title="CF version",
            abstract="CF version to check against, use auto to auto-detect the file version.",
            default="auto",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=["auto", "1.6", "1.5", "1.4", "1.3", "1.2", "1.1"]
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting cfchecker ...", 0)

        # TODO: iterate input files ... run parallel 
        # TODO: generate html report with links to cfchecker output ...
        nc_file = self.getInputValues(identifier='resource')[0]
        # TODO: maybe use local file path
        if not nc_file.endswith(".nc"):
            new_name = nc_file + ".nc"
            from os import rename
            rename(nc_file, new_name)
            nc_file = new_name
        from subprocess import check_output, CalledProcessError
        cmd = ["cfchecks"]
        cmd.extend( ["--cf_standard_names", "http://cfconventions.org/Data/cf-standard-names/28/src/cf-standard-name-table.xml"] )
        cmd.extend( ["--area_types", "http://cfconventions.org/Data/area-type-table/2/src/area-type-table.xml"] )
        #cmd.extend( ["--udunits", "/home/pingu/anaconda/share/udunits/udunits2.xml"])
        cmd.extend( ["--version", self.cf_version.getValue()] ) 
        cmd.append(nc_file)
        try:
            cf_report = check_output(cmd)
        except CalledProcessError as e:
            logger.exception("cfchecker failed! output=%s", e.output)
            cf_report = e.output
        
        self.show_status("writing report ...", 80)

        outfile = self.mktempfile(suffix='.txt')
        with open(outfile, 'w') as fp:
            fp.write(cf_report)
        self.output.setValue( outfile )
        
        self.show_status("cfchecker: done", 100)


        
