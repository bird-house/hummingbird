"""
Processes with cdo commands
"""

from malleefowl.process import WPSProcess

from cdo import Cdo

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class CdoVertIntML(WPSProcess):
    """Vertical interpolation"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = 'cdo_vertintml',
            title = 'CDO 2.12.11 VERTINTML - Vertical interpolation',
            abstract = 'Interpolate 3D variables on hybrid model levels to pressure or height levels.',
            metadata = [{'title': 'CDO', 'href': 'https://code.zmaw.de/projects/cdo'}],
            version = '1.0', # Can this be ommited?
            )

        self.netcdfFile = self.addComplexInput(
            identifier = 'netcdfFile',
            title = 'NetCDF File',
            abstract = 'NetCDF File',
            formats = [{'mimeType': 'application/x-netcdf'}],
            )

        self.operator = self.addLiteralInput(
            identifier = 'operator',
            title = 'CDO Operator',
            abstract = 'Choose a CDO Operator',
            type = type(''),
            allowedValues = ['ml2pl', 'ml2hl'],
            )

        self.levels = self.addLiteralInput(
            identifier = 'levels',
            title = 'p/h levels',
            abstract = 'Float; Pressure levels in pascal / Height levels in meter',
            type = float,
            maxOccurs = 100,
            )

        self.output = self.addComplexOutput(
            identifier = 'output',
            title = 'NetCDF Output',
            abstract = 'NetCDF Output',
            formats = [{'mimeType': 'application/x-netcdf'}],
            asReference = True,
            )

    def execute(self):
        self.show_status('starting cdo operation', 10)

        operator = self.getInputValue('operator')
        netcdfFile = self.getInputValue('netcdfFile')
        levels = self.getInputValue('levels')

        cdo = Cdo()
        cdoOperator = getattr(cdo, operator)

        outfile = self.mktempfile(suffix='.nc')
        cdoOperator(*levels, input=netcdfFile, output=outfile)

        self.show_status('cdo operation done', 90)
        self.output.setValue(outfile)


class CdoZonStat(WPSProcess):
    """Zonal statistical values"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = 'cdo_zonstat',
            title = 'CDO 2.8.6  ZONSTAT - Zonal statistical values',
            abstract = 'This module computes zonal statistical values of the input fields.',
            metadata = [{'title': 'CDO', 'href': 'https://code.zmaw.de/projects/cdo'}],
            version = '1.0', # Can this be ommited?
            )

        self.netcdfFile = self.addComplexInput(
            identifier = 'netcdfFile',
            title = 'NetCDF File',
            abstract = 'NetCDF File',
            formats = [{'mimeType': 'application/x-netcdf'}],
            )

        self.operator = self.addLiteralInput(
            identifier = 'operator',
            title = 'CDO Operator',
            abstract = 'Choose a CDO Operator',
            type = type(''),
            allowedValues = ['zonmin', 'zonmax', 'zonsum', 'zonmean', 'zonavg', 'zonstd', 'zonstd1', 'zonvar', 'zonvar1', 'zonpctl'],
            )

        self.percentile = self.addLiteralInput(
            identifier = 'percentile',
            title = 'Percentile (zonpctl only)',
            abstract = 'FLOAT Percentile number in 0, ..., 100',
            type = float,
            minOccurs = 0,
            maxOccurs = 1,
            )

        self.output = self.addComplexOutput(
            identifier = 'output',
            title = 'NetCDF Output',
            abstract = 'NetCDF Output',
            formats = [{'mimeType': 'application/x-netcdf'}],
            asReference = True,
            )

    def execute(self):
        self.show_status('starting cdo operattion', 10)

        operator = self.getInputValue('operator')
        netcdfFile = self.getInputValue('netcdfFile')
        percentile = self.getInputValue('percentile')

        if operator == 'zonpctl' and percentile is None:
            raise RuntimeError('Missing input for parameter "percentile".')
        elif operator != 'zonpctl' and percentile is not None:
            logger.warning('Unused input for paramter "percentile".')

        cdo = Cdo()
        cdoOperator = getattr(cdo, operator)

        outfile = self.mktempfile(suffix='.nc')
        if operator == 'zonpctl':
            cdoOperator(percentile, input=netcdfFile, output=outfile)
        else:
            cdoOperator(input=netcdfFile, output=outfile)

        self.show_status('cdo operation done', 90)
        self.output.setValue(outfile)