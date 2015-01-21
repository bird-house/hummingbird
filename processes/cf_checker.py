import os

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

def cf_check(nc_file, version):
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
    cmd.extend( ["--version", version] ) 
    cmd.append(nc_file)
    try:
        cf_report = check_output(cmd)
    except CalledProcessError as e:
        logger.exception("cfchecker failed! output=%s", e.output)
        cf_report = e.output
    return cf_report

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
            maxOccurs=1000,
            maxmegabites=10000,
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
        outfile = self.mktempfile(suffix='.txt')
        self.output.setValue( outfile )
        nc_files = self.getInputValues(identifier='resource')
        count = 0
        max_count = len(nc_files)
        step = 100.0 / max_count
        for nc_file in nc_files:
            cf_report = cf_check(nc_file, version=self.cf_version.getValue())
            with open(outfile, 'a') as fp:
                fp.write(cf_report)
                count = count + 1
                self.show_status("cfchecker: %d/%d" % (count, max_count), int(count*step))
        self.show_status("cfchecker: done", 100)


        
