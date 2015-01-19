import os

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class ESMValTool(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "esmvaltool",
            title = "ESMValTool",
            version = "0.1",
            abstract="Test Process for ESMValTool")

        self.model = self.addLiteralInput(
            identifier="model",
            title="Model",
            abstract="",
            default="IPSL-CM5B-LR",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['IPSL-CM5B-LR']
            )

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="",
            default="tas",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['tas']
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

        self.output = self.addComplexOutput(
            identifier="output",
            title="output",
            abstract="output",
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting netcdf metadata retrieval", 0)
        result = self.search()

        import json
        outfile = self.mktempfile(suffix='.json')
        with open(outfile, 'w') as fp:
            json.dump(obj=result, fp=fp, indent=4, sort_keys=True)
            self.output.setValue( outfile )


    def search(self):
        from malleefowl.esgf.search import ESGSearch
        esgsearch = ESGSearch(
            url = "http://localhost:8081/esg-search",
            distrib = True,
            replica = False,
            latest = True,
            monitor = self.show_status,
        )

        constraints = []
        constraints.append( ("project", "CMIP5" ) )
        constraints.append( ("model", self.model.getValue() ) )
        constraints.append( ("variable", self.variable.getValue() ) )
        constraints.append( ("cmor_table", self.cmor_table.getValue() ) )
        constraints.append( ("experiment", self.experiment.getValue() ) )
        constraints.append( ("ensemble", self.ensemble.getValue() ) )

        (result, summary, facet_counts) = esgsearch.search(
            constraints = constraints,
            query = "*:*",
            start = "%d-01-01" % self.start_year.getValue(),
            end = "%d-12-31" % self.end_year.getValue(),
            search_type = "File",
            limit = 1,
            offset = 0,
            temporal = False)
        return result


