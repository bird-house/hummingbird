import pytest

from hummingbird.tests.common import WpsTestClient, TESTDATA, assert_response_success

@pytest.mark.online
def test_wps_cdo_operation():
    wps = WpsTestClient()
    datainputs = "[dataset={0};operator=monmax]".format(TESTDATA['noaa_nc_1'])
    resp = wps.get(service='wps', request='execute', version='1.0.0', identifier='cdo_operation',
                   datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.online
def test_wps_cdo_sinfo():
    wps = WpsTestClient()
    datainputs = "[dataset={0}]".format(TESTDATA['noaa_nc_1'])
    resp = wps.get(service='wps', request='execute', version='1.0.0', identifier='cdo_sinfo',
                   datainputs=datainputs)
    assert_response_success(resp)

