import nose.tools
from unittest import TestCase
from nose import SkipTest
from nose.plugins.attrib import attr

from hummingbird import esmvaltool

class EsmValToolTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_generate_namelist(self):
        result = esmvaltool.generate_namelist(
            name="MyDiag",
            workspace="/tmp",
            model="MPI-ESM-LR",
            experiment="historical",
            cmor_table="Amon",
            ensemble="r1i1p1",
            start_year=2001,
            end_year=2005)
        nose.tools.ok_(result == "namelist_MyDiag.xml", result)
