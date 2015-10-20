"""
Processes for metamongo
"""

from malleefowl.process import WPSProcess

from pymongo import MongoClient as mc

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class MetaMongo(WPSProcess):
    """This process ..."""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = 'metamongo',
            title = 'MetaMongo',
            version = '0.1',
            #abstract = '...',
            )

        self.variables = self.addLiteralInput(
            identifier = 'variables',
            title = 'Variables',
            abstract = 'Variable(s) to be searched for in the query',
            type=str,
            minOccurs=0,
            maxOccurs=1000,
            )

        self.output = self.addLiteralOutput(
            identifier="output",
            title="Result",
            )

    def execute(self):
        self.show_status("starting metamongo", 10)

        #nc_files = self.getInputValues(identifier='netcdf_file')
        #operator = self.operator.getValue()
 
        self.show_status("metamongo done", 90)
        self.output.setValue("Test result!")
