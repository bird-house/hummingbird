import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cdo_ensembles import CDOEnsembles


def test_wps_ensembles_file():
    client = client_for(Service(processes=[CDOEnsembles()]))
    datainputs = "dataset=@xlink:href={0};operator=ensmean".format(TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ensembles',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.online
def test_wps_ensembles_opendap():
    client = client_for(Service(processes=[CDOEnsembles()]))
    datainputs = "dataset_opendap=@xlink:href={0};operator=ensmean".format(TESTDATA['noaa_dap_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ensembles',
        datainputs=datainputs)
    assert_response_success(resp)
