import nose.tools
from unittest import TestCase
from nose import SkipTest
from nose.plugins.attrib import attr

from owslib.wps import monitorExecution

from __init__ import TESTDATA, SERVICE, CREDENTIALS

class WpsTestCase(TestCase):
    """
    Base TestCase class, sets up a wps
    """

    @classmethod
    def setUpClass(cls):
        from owslib.wps import WebProcessingService
        cls.wps = WebProcessingService(SERVICE, verbose=False, skip_caps=False)

class EsgValToolTestCase(WpsTestCase):

    @attr('online')
    def test_mydiag(self):
        inputs = []
        inputs.append(('credentials', CREDENTIALS))
        inputs.append(('distrib', 'False'))
        inputs.append(('replica', 'False'))
        inputs.append(('limit', '10'))
        inputs.append(('model', 'MPI-ESM-LR'))
        inputs.append(('variable', 'ta'))
        inputs.append(('cmor_table', 'Amon'))
        inputs.append(('experiment', 'historical'))
        inputs.append(('ensemble', 'r1i1p1'))
        inputs.append(('start_year', '2001'))
        inputs.append(('end_year', '2005'))
        
        #output=[('output', True), ('namelist', True), ('summary', True)]
        output=[('namelist', True), ('summary', True)]
        execution = self.wps.execute(identifier="esmvaltool", inputs=inputs, output=output)
        monitorExecution(execution, sleepSecs=1)

        nose.tools.ok_(execution.status == 'ProcessSucceeded', execution.status)

    @attr('online')
    def test_mydiag_with_replica(self):
        # TODO: fix replica search ... did not return results
        raise SkipTest
        inputs = []
        inputs.append(('credentials', CREDENTIALS))
        inputs.append(('distrib', 'False'))
        inputs.append(('replica', 'True'))
        inputs.append(('limit', '10'))
        inputs.append(('model', 'MPI-ESM-LR'))
        inputs.append(('variable', 'ta'))
        inputs.append(('cmor_table', 'Amon'))
        inputs.append(('experiment', 'historical'))
        inputs.append(('ensemble', 'r1i1p1'))
        inputs.append(('start_year', '2001'))
        inputs.append(('end_year', '2005'))
        
        output=[('output', True), ('summary', True)]
        execution = self.wps.execute(identifier="esmvaltool", inputs=inputs, output=output)
        monitorExecution(execution, sleepSecs=1)

        nose.tools.ok_(execution.status == 'ProcessSucceeded', execution.status)

    



