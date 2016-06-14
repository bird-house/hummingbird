"""
Processes for plotting netcdf files with matplotlib/basemap
"""

from netCDF4 import Dataset
import numpy as np

from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from pywps.Process import WPSProcess

class SimplePlot(WPSProcess):
    """Plots a simple 2D map of netcdf file"""

    SPATIAL_VARIABLES = [
        'longitude', 'lon', 'rlon',
        'latitude', 'lat', 'rlat',
        'altitude', 'alt', 'level', 'height',
        'rotated_pole',
        'time']
    
    def __init__(self):
        WPSProcess.__init__(
            self,
            identifier="simple_plot",
            title="Simple NetCDF Plotter",
            version="0.2",
            abstract="Simple NetCDF Plotter",
            statusSupported=True,
            storeSupported=True
            )

        self.dataset = self.addComplexInput(
            identifier="dataset",
            title="Dataset (NetCDF)",
            minOccurs=1,
            maxOccurs=1,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        ## self.variable = self.addLiteralInput(
        ##     identifier="variable",
        ##     title="Variable",
        ##     abstract="Variable to plot",
        ##     type=type(''),
        ##     minOccurs=1,
        ##     maxOccurs=1,
        ##     )

        self.output = self.addComplexOutput(
            identifier="output",
            title="Plot",
            formats=[{"mimeType":"image/png"}],
            asReference=True,
            )

    def execute(self):
        ds = Dataset(self.dataset.getValue(), mode='r')
        if 'rlon' in ds.variables:
            lons = ds.variables['rlon'][:]
            lats = ds.variables['rlat'][:]
        else:
            lons = ds.variables['lon'][:]
            lats = ds.variables['lat'][:]

        # Guess variable
        name = longname = None
        for key, variable in ds.variables.items():
            if key.lower() in ds.dimensions:
                # skip dimension variables
                continue
            if '_bnds' in key.lower():
                continue
            if key.lower() in self.SPATIAL_VARIABLES:
                continue
            name = key
            longname = getattr(variable, 'long_name', key)
            break

            
        var = ds.variables[name][0][:]
        units = ds.variables[name].units
        ds.close()

        # Get some parameters for the Stereographic Projection
        lon_0 = lons.mean()
        lat_0 = lats.mean()

        m = Basemap(llcrnrlon=lons[0],llcrnrlat=lats[0],urcrnrlon=lons[-1],urcrnrlat=lats[-1],
                    resolution='l', projection='cyl', lat_0 = lat_0, lon_0 = lon_0)

        # Because our lon and lat variables are 1D, 
        # use meshgrid to create 2D arrays 
        # Not necessary if coordinates are already in 2D arrays.
        lon, lat = np.meshgrid(lons, lats)
        xi, yi = m(lon, lat)

        # Plot Data
        cs = m.pcolor(xi,yi,np.squeeze(var))

        # Add Grid Lines
        #m.drawparallels(np.arange(-80., 81., 10.), labels=[1,0,0,0], fontsize=10)
        #m.drawmeridians(np.arange(-180., 181., 10.), labels=[0,0,0,1], fontsize=10)

        # Add Coastlines, States, and Country Boundaries
        m.drawcoastlines()
        m.drawstates()
        m.drawcountries()

        # Add Colorbar
        cbar = m.colorbar(cs, location='bottom', pad="10%")
        cbar.set_label(units)

        # Add Title
        plt.title(longname)
        plt.savefig('output.png')

        self.output.setValue( 'output.png' )
        
       


