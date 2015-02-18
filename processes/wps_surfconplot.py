from malleefowl import config

from hummingbird.process import ESMValToolProcess
from hummingbird import esmvaltool

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class SurfconPlotProcess(ESMValToolProcess):
    def __init__(self):
        ESMValToolProcess.__init__(self,
            identifier = "surfconplot",
            title = "ESMValTool: surface contour plot for precipitation",
            version = "0.1",
            abstract="Tutorial contour plot used in the doc/overview.pdf")

    def execute(self):
        self.show_status("starting", 0)
        
        constraints=esmvaltool.build_constraints(
            project="CMIP5",
            models=self.getInputValues(identifier='model'),
            variable='pr',
            cmor_table=self.cmor_table.getValue(),
            experiment=self.experiment.getValue(),
            ensemble=self.ensemble.getValue())
        
        out, namelist, log_file, reference = esmvaltool.diag(
            name="surfconplot",
            credentials=self.credentials.getValue(),
            constraints=constraints,
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            output_format=self.output_format.getValue(),
            monitor=self.show_status  )
        
        self.show_status("done", 100)

        self.output.setValue(out)
        self.namelist.setValue(namelist)
        self.log.setValue( log_file )
        self.reference.setValue(reference)
        

 
