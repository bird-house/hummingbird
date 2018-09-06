import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cdo_indices import CDOClimateIndices


def test_wps_indices_file():
    client = client_for(Service(processes=[CDOClimateIndices()]))
    datainputs = "dataset=@xlink:href={0};operator=eca_su".format(TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_indices',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.skip(reason='opendap support is broken.')
@pytest.mark.online
def test_wps_indices_opendap():
    client = client_for(Service(processes=[CDOClimateIndices()]))
    datainputs = "dataset_opendap=@xlink:href={0};operator=eca_su".format(TESTDATA['noaa_dap_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_indices',
        datainputs=datainputs)
    assert_response_success(resp)
