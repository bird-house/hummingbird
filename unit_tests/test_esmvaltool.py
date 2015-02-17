import nose.tools
from unittest import TestCase
from nose import SkipTest
from nose.plugins.attrib import attr

from hummingbird import esmvaltool

class EsmValToolTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_build_constraints(self):
        constraints = esmvaltool.build_constraints(
            project="CMIP5",
            experiment="historical",
            models=["MPI-ESM-LR", "MPI-ESM-MR"])
        nose.tools.ok_(constraints.get("project") == "CMIP5", constraints)
        nose.tools.ok_(constraints.getlist("model") == ["MPI-ESM-LR", "MPI-ESM-MR"], constraints)

    def test_generate_namelist(self):
        constraints = esmvaltool.build_constraints(
            project="CMIP5",
            experiment="historical",
            cmor_table="Amon",
            ensemble="r1i1p1",
            variable="ta",
            models=["MPI-ESM-LR", "MPI-ESM-MR"])

        result = esmvaltool.generate_namelist(
            diag="mydiag",
            workspace="/tmp",
            constraints=constraints,
            start_year=2001,
            end_year=2005,
            output_format='ps')
        nose.tools.ok_("CMIP5 MPI-ESM-LR Amon historical r1i1p1 2001 2005 /tmp/input-data/" in result, result)
        nose.tools.ok_("CMIP5 MPI-ESM-MR Amon historical r1i1p1 2001 2005 /tmp/input-data/" in result, result)

