"""
Processes for plotting netcdf files with matplotlib/basemap
"""

from netCDF4 import Dataset
import numpy as np

from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class SimplePlot(WPSProcess):
    """Plots a simple 2D map of netcdf file"""
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier = "simple_plot",
            title = "Simple NetCDF Plotter",
            version = "0.1",
            abstract="Simple NetCDF Plotter",
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="NetCDF File",
            minOccurs=1,
            maxOccurs=1,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.variable = self.addLiteralInput(
            identifier="variable",
            title="Variable",
            abstract="Variable to plot",
            type=type(''),
            minOccurs=1,
            maxOccurs=1,
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Plot",
            formats=[{"mimeType":"image/png"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting simple plot", 0)

        fh = Dataset(self.dataset.getValue(), mode='r')
        if 'rlon' in fh.variables:
            lons = fh.variables['rlon'][:]
            lats = fh.variables['rlat'][:]
        else:
            lons = fh.variables['lon'][:]
            lats = fh.variables['lat'][:]
        plotvar = fh.variables[self.variable.getValue()][0][:]
        plotvar_units = fh.variables[self.variable.getValue()].units
        fh.close()

        # Get some parameters for the Stereographic Projection
        lon_0 = lons.mean()
        lat_0 = lats.mean()

        m = Basemap(width=5000000,height=3500000,
                resolution='l',projection='stere',\
                lat_ts=40,lat_0=lat_0,lon_0=lon_0)

        # Because our lon and lat variables are 1D, 
        # use meshgrid to create 2D arrays 
        # Not necessary if coordinates are already in 2D arrays.
        lon, lat = np.meshgrid(lons, lats)
        xi, yi = m(lon, lat)

        # Plot Data
        cs = m.pcolor(xi,yi,np.squeeze(plotvar))

        # Add Grid Lines
        m.drawparallels(np.arange(-80., 81., 10.), labels=[1,0,0,0], fontsize=10)
        m.drawmeridians(np.arange(-180., 181., 10.), labels=[0,0,0,1], fontsize=10)

        # Add Coastlines, States, and Country Boundaries
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()

        # Add Colorbar
        cbar = m.colorbar(cs, location='bottom', pad="10%")
        cbar.set_label(plotvar_units)

        # Add Title
        plt.title('Simple Plot')
        plt.savefig('output.png')

        self.output.setValue( 'output.png' )
        
        self.show_status("simple plot done", 100)
       


