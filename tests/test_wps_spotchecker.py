import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_spotchecker import SpotChecker


def test_wps_spotchecker_file():
    client = client_for(Service(processes=[SpotChecker()]))
    datainputs = "dataset=@xlink:href={0};test=CF-1.6".format(TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='spotchecker',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.online
def test_wps_spotchecker_opendap():
    client = client_for(Service(processes=[SpotChecker()]))
    datainputs = "dataset_opendap=@xlink:href={0};test=CF-1.6".format(TESTDATA['test_opendap'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='spotchecker',
        datainputs=datainputs)
    assert_response_success(resp)
