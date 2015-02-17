from malleefowl import config

from hummingbird.process import ESMValToolProcess
from hummingbird import esmvaltool

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class ESMValToolPerfmetricsProcess(ESMValToolProcess):
    def __init__(self):
        ESMValToolProcess.__init__(self,
            identifier = "perfmetrics",
            title = "ESMValTool: Perfmetrics",
            version = "0.1",
            abstract="""Plotting the performance metrics for the CMIP5 models.

            Calculation of performance metrics to quantify the ability of the models to reproduce the
            climatological mean annual cycle for some selected EVCs  plus some additional
            corresponding diagnostics and plots to better understand and interpret the results. 
            
            https://teamsites-extranet.dlr.de/pa/ESMValTool/Wiki/Performance%20Metrics%20for%20Essential%20Climate%20Parameters.aspx
            """)

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['ta', 'ua', 'va', 'zg', 'tas', 'rsut', 'rlut']
            )

    def execute(self):
        self.show_status("starting", 0)

        # TODO: configure distrib, replica, limit
        
        out, namelist_file, log_file, ack_file = esmvaltool.diag_perfmetrics(
            credentials=self.credentials.getValue(),
            project="CMIP5",
            models=self.getInputValues(identifier='model'),
            variable=self.variable.getValue(),
            cmor_table=self.cmor_table.getValue(),
            experiment=self.experiment.getValue(),
            ensemble=self.ensemble.getValue(),
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            output_format=self.output_format.getValue(),
            monitor=self.show_status )
        
        self.show_status("done", 100)

        self.namelist.setValue(namelist_file)
        self.log.setValue( log_file )
        self.output.setValue(out)
        self.ack.setValue(ack_file)
        

 
