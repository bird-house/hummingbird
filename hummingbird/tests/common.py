from pywps.tests import WpsClient, WpsTestResponse

TESTDATA = {
    'noaa_dap_1': "http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis2.dailyavgs/surface/mslp.2016.nc",  # NOPEP8
    'noaa_nc_1': "http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep.reanalysis.dailyavgs/surface/slp.1955.nc",  # NOPEP8
    'noaa_catalog_1': "http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/ncep.reanalysis.dailyavgs/surface/catalog.xml?dataset=Datasets/ncep.reanalysis.dailyavgs/surface/air.sig995.1948.nc"  # NOPEP8
}


class WpsTestClient(WpsClient):

    def get(self, *args, **kwargs):
        query = "?"
        for key, value in kwargs.iteritems():
            query += "{0}={1}&".format(key, value)
        return super(WpsTestClient, self).get(query)


def client_for(service):
    return WpsTestClient(service, WpsTestResponse)
