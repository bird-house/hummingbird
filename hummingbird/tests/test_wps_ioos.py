import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_compliance_checker import CChecker


# @pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.online
def test_wps_ioos_cchecker():
    client = client_for(Service(processes=[CChecker()]))
    datainputs = "dataset_opendap={0};test=cf;criteria=normal;format=html".format(TESTDATA['noaa_dap_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ioos_cchecker',
        datainputs=datainputs)
    assert_response_success(resp)
