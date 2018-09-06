import pytest
from pywps import Service
from pywps.tests import assert_response_success

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cdo_copy import CDOCopy


def test_wps_cdo_copy_file():
    client = client_for(Service(processes=[CDOCopy()]))
    datainputs = "dataset=@xlink:href={0};".format(TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_copy',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.online
def test_wps_cdo_copy_opendap():
    client = client_for(Service(processes=[CDOCopy()]))
    datainputs = "dataset_opendap=@xlink:href={0};".format(TESTDATA['noaa_dap_1'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_copy',
        datainputs=datainputs)
    assert_response_success(resp)
