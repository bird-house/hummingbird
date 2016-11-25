import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_hdh_cfchecker import HDHCFChecker


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.online
def test_wps_qa_cfchecker():
    client = client_for(Service(processes=[HDHCFChecker()]))
    datainputs = "dataset@xlink:href={0};cf_version=auto".format(TESTDATA['noaa_nc_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='qa_cfchecker',
        datainputs=datainputs)
    assert_response_success(resp)
