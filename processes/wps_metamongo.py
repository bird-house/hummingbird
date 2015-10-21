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
            abstract = 'No description',
            )

        self.variables = self.addLiteralInput(
            identifier = 'variables',
            title = 'Variables',
            abstract = 'Variable(s) to be searched for in the query',
            type=str,
            minOccurs=0,
            maxOccurs=1000,
            )

        self.dimensions = self.addLiteralInput(
            identifier = 'dimensions',
            title = 'Dimensions',
            abstract = 'Necassary dimensions',
            type=str,
            minOccurs=0,
            maxOccurs=1000,
            )

        # If both (start and end) are set, this is interpreted as an interval.
        self.timeBegin = self.addLiteralInput(
            identifier = 'timeBegin',
            title = 'Begin date',
            abstract = 'Begin date (DD.MM.YYYY)',
            type=date,
            minOccurs=0,
            maxOccurs=1,
            )

        self.timeEnd = self.addLiteralInput(
            identifier = 'timeEnd',
            title = 'End date',
            abstract = 'End date (DD.MM.YYYY)',
            type=date,
            minOccurs=0,
            maxOccurs=1,
            )

        # Two values will be interpreted as a bounding box.
        self.latitude = self.addLiteralInput(
            identifier = 'latitude',
            title = 'Latitude',
            abstract = 'Latitude points',
            type=int,
            minOccurs=0,
            maxOccurs=2,
            )

        # Two values will be interpreted as a bounding box.
        self.longitude = self.addLiteralInput(
            identifier = 'longitude',
            title = 'Longitude',
            abstract = 'Longitude points',
            type=int,
            minOccurs=0,
            maxOccurs=2,
            )

        # Two values will be interpreted as a bounding box.
        self.pressure = self.addLiteralInput(
            identifier = 'pressure',
            title = 'Pressure levels',
            abstract = 'Pressure levels',
            type=int,
            minOccurs=0,
            maxOccurs=2,
            )

        # Two values will be interpreted as a bounding box.
        self.intermediate = self.addLiteralInput(
            identifier = 'intermediate',
            title = 'Pressure intermediate levels',
            abstract = 'Pressure intermediate levels',
            type=int,
            minOccurs=0,
            maxOccurs=2,
            )

        self.output = self.addLiteralOutput(
            identifier="output",
            title="Result",
            )

    def execute(self):
        self.show_status("starting metamongo", 10)

        query = dict()

        variables = self.getInputValue(identifier='variables')
        if variables is not None:
            query['variables'] = {'$all': variables}

        dimensions = self.getInputValue(identifier='dimensions')
        if dimensions is not None:
            for dim in dimensions:
                query[dim] = dict('$exists'=True)

        timeBegin = self.getInputValue(identifier='timeBegin')
        timeEnd   = self.getInputValue(identifier='timeEnd')
        # ...

        #nc_files = self.getInputValues(identifier='netcdf_file')
        #operator = self.operator.getValue()

        logger.debug(query)
 
        self.show_status("metamongo done", 90)
        self.output.setValue("Test result!")
