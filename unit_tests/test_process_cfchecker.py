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

class CFCheckerProcessTestCase(WpsTestCase):

    @attr('online')
    def test_cfcheck(self):
        #raise SkipTest
        inputs = []
        inputs.append((
            'resource',
            TESTDATA['tasmax_WAS-44_MPI-M-MPI-ESM-LR_historical_r1i1p1_MPI-CSC-REMO2009_v1_day_20010101-20051231.nc']))
        inputs.append(('cf_version', 'auto'))
        
        output=[('output', True)]
        execution = self.wps.execute(identifier="cfchecker", inputs=inputs, output=output)
        monitorExecution(execution, sleepSecs=1)

        nose.tools.ok_(execution.status == 'ProcessSucceeded', execution.status)
        nose.tools.ok_('output' in execution.processOutputs[0].reference)
