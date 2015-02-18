from malleefowl import config

from hummingbird.process import ESMValToolProcess
from hummingbird import esmvaltool

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class AnnualCycleProcess(ESMValToolProcess):
    def __init__(self):
        ESMValToolProcess.__init__(self,
            identifier = "anncycle",
            title = "ESMValTool: Perfmetrics Annual Cycle Line Plot",
            version = "0.1",
            abstract="Plotting an annual cycle line diagram of the performance metrics for the CMIP5 models."
            )

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

        constraints= esmvaltool.build_constraints(
            project="CMIP5",
            models=self.getInputValues(identifier='model'),
            variable=self.variable.getValue(),
            cmor_table=self.cmor_table.getValue(),
            experiment=self.experiment.getValue(),
            ensemble=self.ensemble.getValue())
        
        out, namelist, log_file, reference = esmvaltool.diag(
            name="anncycle",
            credentials=self.credentials.getValue(),
            constraints=constraints,
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            output_format=self.output_format.getValue(),
            monitor=self.show_status)
        
        self.show_status("done", 100)

        self.output.setValue(out)
        self.namelist.setValue(namelist)
        self.log.setValue( log_file )
        self.reference.setValue(reference)
        

 
