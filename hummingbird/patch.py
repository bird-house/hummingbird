import logging
LOGGER = logging.getLogger("PYWPS")


def patch_compliance_checker():
    """
    Patch compliance_checker for ESGF OpenDAP with ``.dodsrc``.
    """
    def patched_load_dataset(self, ds_str):
        LOGGER.warning("!!! running patched compliance_checker !!!")
        from netCDF4 import Dataset
        LOGGER.debug("dataset url: %s", ds_str)
        return Dataset(ds_str)
    from compliance_checker import suite
    suite.CheckSuite.load_dataset = patched_load_dataset
