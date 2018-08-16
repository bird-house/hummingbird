import pytest
from pywps import Service
from pywps.tests import assert_response_success

import requests

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cdo_op import CDOOperation


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.skipif(
    requests.head(TESTDATA['noaa_nc_1']).ok is False,
    reason="website unavailable")
@pytest.mark.online
def test_wps_cdo_operation():
    client = client_for(Service(processes=[CDOOperation()]))
    datainputs = "dataset@xlink:href={0};operator=monmax".format(TESTDATA['noaa_nc_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_operation',
        datainputs=datainputs)
    assert_response_success(resp)
