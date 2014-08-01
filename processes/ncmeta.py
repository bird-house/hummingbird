import os

from malleefowl.process import WorkerProcess

from malleefowl import wpslogging as logging
logger = logging.getLogger(__name__)

class NetcdfMetadata(WorkerProcess):
    def __init__(self):
        WorkerProcess.__init__(self,
            identifier = "org.malleefowl.ncmeta",
            title = "NetCDF Metadata",
            version = "0.1",
            metadata=[
                ],
            abstract="Retrieve Metadata of NetCDF File")

        self.output = self.addComplexOutput(
            identifier="output",
            title="NetCDF Metadata",
            abstract="NetCDF Metadata",
            metadata=[],
            formats=[{"mimeType":"application/json"}],
            asReference=True,
            )

    def execute(self):
        self.show_status("starting netcdf metadata retrieval", 5)

        nc_file = self.get_nc_files()[0]

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


        
