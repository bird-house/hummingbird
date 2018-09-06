import pytest
from pywps import Service
from pywps.tests import assert_response_success

import requests

from .common import TESTDATA, client_for
from hummingbird.processes.wps_compliance_checker import CChecker


def test_wps_cchecker_file():
    client = client_for(Service(processes=[CChecker()]))
    datainputs = "dataset=@xlink:href={0};test=cf;criteria=normal;format=html".format(
        TESTDATA['test_local_nc'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cchecker',
        datainputs=datainputs)
    assert_response_success(resp)


@pytest.mark.skipif(
    requests.head(TESTDATA['test_opendap']).ok is False,
    reason="website unavailable")
@pytest.mark.online
def test_wps_cchecker_opendap():
    client = client_for(Service(processes=[CChecker()]))
    datainputs = "dataset_opendap=@xlink:href={0};test=cf;criteria=normal;format=html".format(
        TESTDATA['test_opendap'])
    resp = client.get(
        service='WPS', request='Execute', version='1.0.0',
        identifier='cchecker',
        datainputs=datainputs)
    assert_response_success(resp)
