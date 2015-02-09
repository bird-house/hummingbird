from malleefowl.process import WPSProcess
from malleefowl import config

from hummingbird import esmvaltool

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class ESMValToolOverviewProcess(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "overview",
            title = "ESMValTool Overview",
            version = "0.1",
            abstract="Overview Diag of ESMValTool")

        self.credentials = self.addComplexInput(
            identifier = "credentials",
            title = "X509 Certificate",
            abstract = "X509 proxy certificate to access ESGF data.",
            minOccurs=0,
            maxOccurs=1,
            maxmegabites=1,
            formats=[{"mimeType":"application/x-pkcs7-mime"}],
            )

        self.model = self.addLiteralInput(
            identifier="model",
            title="Model",
            abstract="",
            default="MPI-ESM-LR",
            type=type(''),
            minOccurs=1,
            maxOccurs=10,
            allowedValues=["IPSL-CM5A-LR", "MPI-ESM-LR", "MPI-ESM-MR", "MPI-ESM-P"]
            )

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="",
            default="pr",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['pr']
            )

        self.cmor_table = self.addLiteralInput(
            identifier="cmor_table",
            title="CMOR Table",
            abstract="",
            default="Amon",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['Amon']
            )

        self.experiment = self.addLiteralInput(
            identifier="experiment",
            title="Experiment",
            abstract="",
            default="historical",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['historical']
            )

        self.ensemble = self.addLiteralInput(
            identifier="ensemble",
            title="Ensemble",
            abstract="",
            default="r1i1p1",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['r1i1p1']
            )

        self.start_year = self.addLiteralInput(
            identifier="start_year",
            title="Start Year",
            abstract="",
            default="2001",
            type=type(2001),
            minOccurs=1,
            maxOccurs=1
            )

        self.end_year = self.addLiteralInput(
            identifier="end_year",
            title="End Year",
            abstract="",
            default="2005",
            type=type(2005),
            minOccurs=1,
            maxOccurs=1
            )

        self.output_format = self.addLiteralInput(
            identifier="output_format",
            title="Output Format",
            abstract="",
            default="ps",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['ps', 'eps', 'pdf', 'png']
            )

        # outputs
        # -------

        self.output = self.addComplexOutput(
            identifier="output",
            title="output",
            abstract="",
            formats=[
                {"mimeType":"application/postscript"},
                {"mimeType":"application/pdf"},
                {"mimeType":"image/png"},
                {"mimeType":"application/eps"}
                ],
            asReference=True,
            )

        self.namelist = self.addComplexOutput(
            identifier="namelist",
            title="namelist",
            abstract="",
            formats=[{"mimeType":"application/xml"}],
            asReference=True,
            )

        self.log = self.addComplexOutput(
            identifier="log",
            title="log",
            abstract="",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting", 0)

        # TODO: configure distrib, replica, limit
        
        out, namelist_file, log_file = esmvaltool.run_on_esgf(
            diag='overview',
            credentials=self.credentials.getValue(),
            project="CMIP5",
            models=self.getInputValues(identifier='model'),
            variable=self.variable.getValue(),
            cmor_table=self.cmor_table.getValue(),
            experiment=self.experiment.getValue(),
            ensemble=self.ensemble.getValue(),
            distrib=True,
            replica=False,
            limit=100,
            start_year=self.start_year.getValue(),
            end_year=self.end_year.getValue(),
            output_format=self.output_format.getValue(),
            monitor=self.show_status  )
        
        self.show_status("done", 100)

        self.namelist.setValue(namelist_file)
        self.log.setValue( log_file )
        self.output.setValue(out)
        

 
