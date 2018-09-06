import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_ncdump import NCDump


def test_wps_ncdump_file():
    client = client_for(Service(processes=[NCDump()]))
    datainputs = "dataset=@xlink:href={0};".format(TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ncdump',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.online
def test_wps_ncdump_opendap():
    client = client_for(Service(processes=[NCDump()]))
    datainputs = "dataset_opendap=@xlink:href={0};".format(TESTDATA['test_opendap'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='ncdump',
        datainputs=datainputs)
    assert_response_success(resp)
