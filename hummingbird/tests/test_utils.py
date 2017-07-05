from hummingbird.utils import output_filename


def test_output_filename():
    assert output_filename("tas.nc") == 'tas_.nc'
    assert output_filename("tas.nc", addition="copy") == 'tas_copy.nc'
    assert output_filename("tas_eur.nc", addition="copy") == 'tas_eur_copy.nc'
    assert output_filename("out.html", addition="test", extension='html') == 'out_test.html'
