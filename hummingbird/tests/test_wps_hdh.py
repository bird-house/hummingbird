import pytest

from hummingbird.tests.common import WpsTestClient, TESTDATA, assert_response_success

@pytest.mark.online
def test_wps_qa_cfchecker():
    wps = WpsTestClient()
    datainputs = "[dataset={0}]".format(TESTDATA['noaa_nc_1'])
    resp = wps.get(service='wps', request='execute', version='1.0.0', identifier='qa_cfchecker',
                   datainputs=datainputs)
    assert_response_success(resp)

