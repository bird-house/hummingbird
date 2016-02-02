import nose.tools
from nose.plugins.attrib import attr

from tests.common import WpsTestClient, TESTDATA, assert_response_success

@attr('online')
def test_wps_ensembles():
    wps = WpsTestClient()
    datainputs = "[dataset={0};operator=ensmean]".format(TESTDATA['noaa_nc_1'])
    resp = wps.get(service='wps', request='execute', version='1.0.0', identifier='ensembles',
                   datainputs=datainputs)
    assert_response_success(resp)

