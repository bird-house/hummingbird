import os
from mako.template import Template

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

templ_cfchecks = Template(
"""
#!/bin/bash
source activate hummingbird
cfchecks \
    --cf_standard_names http://cfconventions.org/Data/cf-standard-names/28/src/cf-standard-name-table.xml \
    --area_types http://cfconventions.org/Data/area-type-table/2/src/area-type-table.xml \
    --version ${version} \
    ${input_file} &> ${output_file}
source deactivate
"""
)

def cf_check(nc_file, version):
    logger.debug("start cf_check: nc_file=%s, version=%s", nc_file, version)
    # TODO: maybe use local file path
    if not nc_file.endswith(".nc"):
        new_name = nc_file + ".nc"
        from os import rename
        rename(nc_file, new_name)
        nc_file = new_name
    from subprocess import check_call, CalledProcessError
    # TODO: using anaconda env ... should be configured in pywps/gunicorn!
    #from os.path import realpath
    cfchecks_script = templ_cfchecks.render(
        version=version,
        input_file=nc_file,
        output_file="output.txt")
    with open("cfchecks.sh", 'w') as fp:
        fp.write(cfchecks_script)
    cmd = ["bash", "cfchecks.sh"]
    try:
        check_call(cmd)
        with open("output.txt", 'r') as fp:
            cf_report = fp.read()
    except Exception as e:
        logger.exception("cfchecker failed!")
        cf_report = "cfchecker failed, error=%s" % e.message
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


        
