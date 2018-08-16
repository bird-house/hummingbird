import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_ncdump import NCDump


@pytest.mark.online
def test_wps_ncdump():
    client = client_for(Service(processes=[NCDump()]))
    datainputs = "dataset_opendap={0}".format(TESTDATA['noaa_dap_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ncdump',
        datainputs=datainputs)
    assert_response_success(resp)
