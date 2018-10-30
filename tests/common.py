import os
import requests
from pywps.tests import WpsClient, WpsTestResponse

TESTS_HOME = os.path.abspath(os.path.dirname(__file__))


def resource_file(filepath):
    return os.path.join(TESTS_HOME, 'testdata', filepath)


TESTDATA = {
    'test_local_nc':
    'file:///{}'.format(resource_file('test.nc')),
    'test_opendap':
    'http://test.opendap.org:80/opendap/netcdf/examples/sresa1b_ncar_ccsm3_0_run1_200001.nc',  # noqa
    'noaa_dap_1':
    "http://www.esrl.noaa.gov/psd/thredds/dodsC/Datasets/ncep.reanalysis.derived/surface/air.mon.ltm.nc",  # noqa
    'noaa_nc_1':
    "http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep.reanalysis.dailyavgs/surface/slp.1955.nc",  # noqa
    'noaa_catalog_1':
    "http://www.esrl.noaa.gov/psd/thredds/catalog/Datasets/ncep.reanalysis.dailyavgs/surface/catalog.xml?dataset=Datasets/ncep.reanalysis.dailyavgs/surface/air.sig995.1948.nc"  # noqa
}


def service_ok(url, timeout=5):
    try:
        ok = requests.get(url, timeout=timeout).ok
    except requests.exceptions.ReadTimeout:
        print('Read Timeout')
        ok = False
    except requests.exceptions.ConnectTimeout:
        print('Connect Timeout')
        ok = False
    except Exception:
        ok = False
    return ok


class WpsTestClient(WpsClient):

    def get(self, *args, **kwargs):
        query = "?"
        for key, value in kwargs.items():
            query += "{0}={1}&".format(key, value)
        return super(WpsTestClient, self).get(query)


def client_for(service):
    return WpsTestClient(service, WpsTestResponse)
