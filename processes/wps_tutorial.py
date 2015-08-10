from malleefowl.process import WPSProcess
from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class Tutorial(WPSProcess):

    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = "tutorial",
            title = "Tutorial Process",
            version = "0.1",
            abstract="Do something useful",
            )

        self.netcdf_file = self.addComplexInput(
            identifier="netcdf_file",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=1,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        # complex output
        # -------------

        self.output = self.addComplexOutput(
            identifier="output",
            title="Result",
            formats=[{"mimeType":"text/plain"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting ...", 0)

        nc_files = self.getInputValues(identifier='netcdf_file')
        out_filename = self.mktempfile(suffix='.txt')

        from netCDF4 import Dataset
        from numpy import arange, dtype # array module from http://numpy.scipy.org
        from numpy.testing import assert_array_equal, assert_array_almost_equal

        nlats = 6; nlons = 12
        # open netCDF file for reading
        ncfile = Dataset(nc_files[0], 'r') 
        # expected latitudes and longitudes of grid
        lats_check = 25.0 + 5.0*arange(nlats,dtype='float32')
        lons_check = -125.0 + 5.0*arange(nlons,dtype='float32')
        # expected data.
        #press_check = 900. + 6.0*arange(0.,nlats*nlons,dtype='float32') # 1d array
        #press_check.shape = (nlats,nlons) # reshape to 2d array
        #temp_check = 9. + 0.25*arange(nlats*nlons,dtype='float32') # 1d array
        #temp_check.shape = (nlats,nlons) # reshape to 2d array
        # get pressure and temperature variables.
        try:
            temp = ncfile.variables['temperature']
            press = ncfile.variables['pressure']
        except:
            raise Exception("variable not found")
        # check units attributes.
        assert temp.units == 'celsius', 'temperature units attribute not what was expected'
        assert press.units == 'hPa', 'pressure units attribute not what was expected'
        # get coordinate variables.
        lats = ncfile.variables['latitude']
        lons = ncfile.variables['longitude']
        # check units attributes.
        assert lats.units == 'degrees_north', 'latitude units attribute not what was expected'
        assert lons.units == 'degrees_east', 'longitude units attribute not what was expected'
        # check data
        try:
            assert_array_almost_equal(lats[:],lats_check)
        except:
            raise ValueError('latitude data not what was expected')
        try:
            assert_array_almost_equal(lons[:],lons_check)
        except:
            raise ValueError('longitude data not what was expected')

        with open(out_filename, 'w') as fp:
            fp.write( '*** SUCCESS reading example file testfile.nc!\n' )
            fp.write( "mittlerer zonaler Druck %s hPa" % ( sum(press[:])/6. ) )
        # close the file.
        ncfile.close()
        
        
        self.output.setValue( out_filename )
        self.show_status("done", 100)
