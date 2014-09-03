import os

from malleefowl.process import WPSProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class NetcdfMetadata(WPSProcess):
    def __init__(self):
        WPSProcess.__init__(self,
            identifier = "ncmeta",
            title = "NetCDF Metadata",
            version = "0.1",
            abstract="Retrieve Metadata of NetCDF File")

        self.netcdf_file = self.addComplexInput(
            identifier="netcdf_file",
            title="NetCDF File",
            abstract="NetCDF File",
            minOccurs=1,
            maxOccurs=100,
            maxmegabites=5000,
            formats=[{"mimeType":"application/x-netcdf"}],
            )

        self.output = self.addComplexOutput(
            identifier="output",
            title="NetCDF Metadata",
            abstract="NetCDF Metadata",
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting netcdf metadata retrieval", 5)

        nc_file = self.getInputValues(identifier='netcdf_file')[0]

        from netCDF4 import Dataset
        ds = Dataset(nc_file)
        metadata = {}
        metadata['global_attributes'] = {}
        for att_name in ["contact", "experiment", "institute_id", "title"]:
            if hasattr(ds, att_name):
                metadata['global_attributes'][att_name] = getattr(ds, att_name)
        metadata['dimensions'] = ds.dimensions.keys()
        metadata['variables'] = {}
        for var_name in ds.variables.keys():
            metadata['variables'][var_name] = {}
            for att_name in ["axis", "bounds", "calendar", "long_name", "standard_name", "units", "shape"]:
                if hasattr(ds.variables[var_name], att_name):
                    metadata['variables'][var_name][att_name] = getattr(ds.variables[var_name], att_name)
        
        self.show_status("retrieved netcdf metadata", 80)

        import json
        out_filename = self.mktempfile(suffix='.json')
        with open(out_filename, 'w') as fp:
            json.dump(obj=metadata, fp=fp, indent=4, sort_keys=True)
        self.output.setValue( out_filename )
        
        self.show_status("netcdf metadata written", 90)


        
