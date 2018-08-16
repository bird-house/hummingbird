import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cdo_ensembles import CDOEnsembles


@pytest.mark.skip(reason="no way of currently testing this")
@pytest.mark.online
def test_wps_ensembles():
    client = client_for(Service(processes=[CDOEnsembles()]))
    datainputs = "dataset={0};operator=ensmean".format(TESTDATA['noaa_nc_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ensembles',
        datainputs=datainputs)
    assert_response_success(resp)
