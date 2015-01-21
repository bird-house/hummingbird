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
            abstract="""
            The NetCDF Climate Forcast Conventions compliance checker
            
            http://cf-pcmdi.llnl.gov/conformance/compliance-checker/
            """
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

        self.output = self.addComplexOutput(
            identifier="output",
            title="CF Checker Report",
            abstract="",
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting cfchecker ...", 0)

        nc_file = self.getInputValues(identifier='resource')[0]
        from subprocess import check_output, CalledProcessError
        cmd = ["cfchecks"]
        cmd.extend( ["--cf_standard_names", "http://cfconventions.org/Data/cf-standard-names/28/src/cf-standard-name-table.xml"] )
        cmd.extend( ["--area_types", "http://cfconventions.org/Data/area-type-table/2/src/area-type-table.xml"] )
        #cmd.extend( ["--udunits", "/home/pingu/anaconda/share/udunits/udunits2.xml"]) 
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


        
