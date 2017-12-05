import pytest
from pywps import Service
from pywps.tests import assert_response_success

import requests

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cfchecker import CFChecker


@pytest.mark.skipif(
    requests.head(TESTDATA['noaa_nc_1']).ok is False,
    reason="website unavailable")
@pytest.mark.online
def test_wps_cfchecker():
    client = client_for(Service(processes=[CFChecker()]))
    datainputs = "dataset={0};cf_version=auto".format(TESTDATA['noaa_nc_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cfchecker',
        datainputs=datainputs)
    assert_response_success(resp)
