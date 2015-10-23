"""
Processes for metamongo
"""

from malleefowl.process import WPSProcess

from datetime import date, datetime
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
            type = str,
            minOccurs = 0,
            maxOccurs = 1000,
            )

        self.dimensions = self.addLiteralInput(
            identifier = 'dimensions',
            title = 'Dimensions',
            abstract = 'Necassary dimensions',
            type = str,
            minOccurs = 0,
            maxOccurs = 1000,
            )

        self.timeBegin = self.addLiteralInput(
            identifier = 'timeBegin',
            title = 'Begin date',
            abstract = 'Begin date (DD.MM.YYYY)',
            type = date, # TODO: This doesn't seem to be enough to prevent illegal dates.
            minOccurs = 0,
            maxOccurs = 1,
            )

        self.timeEnd = self.addLiteralInput(
            identifier = 'timeEnd',
            title = 'End date',
            abstract = 'End date (DD.MM.YYYY)',
            type = date,
            minOccurs = 0,
            maxOccurs = 1,
            )

        self.latitude = self.addLiteralInput(
            identifier = 'latitude',
            title = 'Latitude',
            abstract = 'Latitude points',
            type = int,
            minOccurs = 0,
            maxOccurs = 2, # This seems to be ignored by the phoenix web interface. See issue https://github.com/bird-house/pyramid-phoenix/issues/52
            )

        self.longitude = self.addLiteralInput(
            identifier = 'longitude',
            title = 'Longitude',
            abstract = 'Longitude points',
            type = int,
            minOccurs = 0,
            maxOccurs = 2,
            )

        self.pressure = self.addLiteralInput(
            identifier = 'pressure',
            title = 'Pressure levels',
            abstract = 'Pressure levels',
            type = int,
            minOccurs = 0,
            maxOccurs = 2,
            )

        self.intermediate = self.addLiteralInput(
            identifier = 'intermediate',
            title = 'Pressure intermediate levels',
            abstract = 'Pressure intermediate levels',
            type = int,
            minOccurs = 0,
            maxOccurs = 2,
            )

        self.output = self.addLiteralOutput(
            identifier = 'output',
            title = 'Result',
            )

    def execute(self):
        self.show_status('starting metamongo', 10)
        query = dict()

        variables = self.getInputValue('variables')
        if variables is not None:
            query['variables'] = {'$all': variables}

        dimensions = self.getInputValue('dimensions')
        if dimensions is not None:
            for dim in dimensions:
                query[dim] = {'$exists': True}

        # TODO: Maybe this can be ommited, if PyWPS input support such checks.
        def checkDate(d):
            return datetime.strptime(d, '%d.%m.%Y')

        timeBegin = self.getInputValue('timeBegin')
        timeEnd   = self.getInputValue('timeEnd')
        if timeBegin is not None:
            query['time.maximum'] = {'$gte': checkDate(timeBegin)}
        if timeEnd is not None:
            query['time.minimum'] = {'$lte': checkDate(timeEnd)}

        latitude = self.getInputValue('latitude')
        if latitude is not None:
            query['lat.maximum'] = {'$gte': max(latitude)}
            query['lat.minimum'] = {'$lte': min(latitude)}

        longitude = self.getInputValue('longitude')
        if longitude is not None:
            query['lon.maximum'] = {'$gte': max(longitude)}
            query['lon.minimum'] = {'$lte': min(longitude)}

        pressure = self.getInputValue('pressure')
        if pressure is not None:
            query['plev.maximum'] = {'$gte': max(pressure)}
            query['plev.minimal'] = {'$lte': min(pressure)}

        intermediate = self.getInputValue('intermediate')
        if intermediate is not None:
            query['ilev.maximum'] = {'$gte': max(intermediate)}
            query['ilev.minimum'] = {'$lte': min(intermediate)}

        logger.debug('Database query: {}'.format(query))

        # TODO: MongoDB connection and query.
        #cursor = mc('localhost',27017)['netcdf']['test']
        #result = cursor.find(query,{'path':1,'_id':0})
 
        self.show_status('metamongo done', 90)
        # TODO: Set query result as output.
        self.output.setValue('Database query: {}'.format(query)) 
