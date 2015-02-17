from malleefowl import config

from hummingbird.process import ESMValToolProcess
from hummingbird import esmvaltool

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class ESMValToolMyDiagProcess(ESMValToolProcess):
    def __init__(self):
        ESMValToolProcess.__init__(self,
            identifier = "mydiag",
            title = "ESMValTool MyDiag",
            version = "0.1",
            abstract="Tutorial diagnostic used in the doc/toy-diagnostic-tutorial.pdf")

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="",
            default="ta",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['ta']
            )

    def execute(self):
        self.show_status("starting", 0)

        # TODO: configure distrib, replica, limit
        
        out, namelist_file, log_file, ack_file = esmvaltool.diag_mydiag(
            credentials=self.credentials.getValue(),
            constraints=esmvaltool.build_constraints(
                project="CMIP5",
                models=self.getInputValues(identifier='model'),
                variable=self.variable.getValue(),
                cmor_table=self.cmor_table.getValue(),
                experiment=self.experiment.getValue(),
                ensemble=self.ensemble.getValue()),
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            output_format=self.output_format.getValue(),
            monitor=self.show_status  )
        
        self.show_status("done", 100)

        self.namelist.setValue(namelist_file)
        self.log.setValue( log_file )
        self.output.setValue(out)
        self.ack.setValue(ack_file)
        

 
