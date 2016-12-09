import pytest

from pywps import Service
from pywps.tests import assert_response_success

from .common import client_for
from hummingbird.processes import processes


def test_wps_caps():
    client = client_for(Service(processes=processes))
    resp = client.get(service='wps', request='getcapabilities', version='1.0.0')
    names = resp.xpath_text('/wps:Capabilities'
                            '/wps:ProcessOfferings'
                            '/wps:Process'
                            '/ows:Identifier')
    assert sorted(names.split()) == [
        'cdo_bbox',
        'cdo_operation',
        'cdo_sinfo',
        'cfchecker',
        'ensembles',
        'ioos_cchecker',
        'ncdump',
        'qa_cfchecker',
        'qa_checker',
        'spotchecker']
