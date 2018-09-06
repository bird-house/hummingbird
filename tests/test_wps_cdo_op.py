import pytest
from pywps import Service
from pywps.tests import assert_response_success

import requests

from .common import TESTDATA, client_for
from hummingbird.processes.wps_cdo_op import CDOOperation


def test_wps_cdo_operation_file():
    client = client_for(Service(processes=[CDOOperation()]))
    datainputs = "dataset=@xlink:href={0};operator=monmax".format(TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_operation',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.skip(reason='opendap support is broken.')
@pytest.mark.online
def test_wps_cdo_operation_opendap():
    client = client_for(Service(processes=[CDOOperation()]))
    datainputs = "dataset_opendap=@xlink:href={0};operator=monmax".format(TESTDATA['test_opendap'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cdo_operation',
        datainputs=datainputs)
    assert_response_success(resp)
