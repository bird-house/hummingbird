from hummingbird.tests.common import WpsTestClient


def test_wps_caps():
    wps = WpsTestClient()
    resp = wps.get(service='wps', request='getcapabilities')
    names = resp.xpath_text('/wps:Capabilities'
                            '/wps:ProcessOfferings'
                            '/wps:Process'
                            '/ows:Identifier')
    sorted_names = sorted(names.split())
    expected_names = [
        'cdo_lonlatbox',
        'cdo_operation',
        'cdo_sinfo',
        'cfchecker',
        'ensembles',
        'ioos_cchecker',
        'ncdump',
        'qa_cfchecker',
        'qa_checker',
        'spotchecker']
    assert sorted_names == expected_names
