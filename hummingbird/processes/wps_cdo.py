"""
Processes with cdo commands
"""
from cdo import Cdo
cdo_version = Cdo().version()

from pywps.Process import WPSProcess

import logging

class CDOOperation(WPSProcess):
    """This process calls cdo with operation on netcdf file"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_operation",
            title="CDO Operation",
            version=cdo_version,
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO Operation like monmax on NetCDF File.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.operator = self.addLiteralInput(
            identifier="operator",
            title="CDO Operator",
            abstract="Choose a CDO Operator",
            default="monmax",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            allowedValues=['merge', 'dayavg', 'daymax', 'daymean', 'daymin','daysum', 'dayvar',    'daystd', 'monmax', 'monmin', 'monmean', 'monavg', 'monsum', 'monvar', 'monstd', 'ymonmin', 'ymonmax', 'ymonsum', 'ymonmean', 'ymonavg', 'ymonvar', 'ymonstd', 'yearavg', 'yearmax', 'yearmean', 'yearmin', 'yearsum', 'yearvar', 'yearstd', 'yseasvar']
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="NetCDF Output",
            abstract="NetCDF Output",
            formats=[{"mimeType":"application/x-netcdf"}],
            asReference=True,
            )

    def execute(self):
        datasets = self.getInputValues(identifier='dataset')
        operator = self.operator.getValue()

        cdo = Cdo()
        cdo_op = getattr(cdo, operator)
        
        outfile = 'out.nc'
        cdo_op(input=datasets, output=outfile)

        self.output.setValue( outfile )
        
        self.status.set("cdo operator done", 100)


class CDOInfo(WPSProcess):
    """This process calls cdo sinfo on netcdf file"""

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_sinfo",
            title="CDO sinfo",
            version=cdo_version,
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO sinfo on NetCDF File.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CDO sinfo result",
            abstract="CDO sinfo result",
            metadata=[],
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        cdo = Cdo()

        datasets = self.getInputValues(identifier='dataset')

        outfile = 'out.txt'
        with open(outfile, 'w') as fp: 
            for ds in datasets:
                sinfo = cdo.sinfo(input=[ds], output=outfile)
                for line in sinfo:
                    fp.write(line + '\n')
                fp.write('\n\n')
            self.output.setValue( fp.name )
            self.status.set("cdo sinfo done", 100)

class CDOLonLatBox(WPSProcess):
    """This process calls cdo sellonlatbox on netcdf file"""

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="cdo_lonlatbox",
            title="CDO select lon/lat box",
            version=cdo_version,
            metadata=[
                {"title":"CDO","href":"https://code.zmaw.de/projects/cdo"},
                ],
            abstract="Apply CDO sellonlatbox on NetCDF File.",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.bbox = self.addBBoxInput(
            identifier="bbox",
            title="Bounding Box",
            minOccurs=1,
            maxOccurs=1,
            crss=["EPSG:4326", "EPSG:3035"],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="CDO result",
            abstract="CDO sellonlatbox result",
            metadata=[],
            formats=[{"mimeType":"application/x-netcdf"}],
            asReference=True,
            )

    def execute(self):
        cdo = Cdo()

        # TODO handle mutliple input files
        datasets = self.getInputValues(identifier='dataset')
        bbox = self.bbox.getValue()

        logging.debug("bbox: %s", bbox.coords)
        outfile = "out.nc"
        op_bbox="%d,%d,%d,%d" % (bbox.coords[0][0], bbox.coords[1][0], bbox.coords[0][1], bbox.coords[1][1])
        cdo.sellonlatbox(op_bbox, input=datasets[0], output=outfile)
        self.output.setValue( outfile )
        
        self.status.set("cdo sellonlatbox done", 100)

        
