import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from owslib.wps import monitorExecution

from __init__ import TESTDATA, SERVICE, CREDENTIALS, WpsTestCase

class TaylorProcessTestCase(WpsTestCase):

    @attr('online')
    @attr('slow')
    def test_taylor_ta(self):
        #raise SkipTest
        inputs = []
        inputs.append(('credentials', CREDENTIALS))
        inputs.append(('model', 'MPI-ESM-LR'))
        inputs.append(('model', 'MPI-ESM-MR'))
        inputs.append(('variable', 'ta'))
        inputs.append(('cmor_table', 'Amon'))
        inputs.append(('experiment', 'historical'))
        inputs.append(('ensemble', 'r1i1p1'))
        inputs.append(('start_year', '2000'))
        inputs.append(('end_year', '2001'))
        
        output=[('output', True), ('namelist', True), ('log', True)]
        execution = self.wps.execute(identifier="taylor", inputs=inputs, output=output)
        monitorExecution(execution, sleepSecs=1)

        nose.tools.ok_(execution.status == 'ProcessSucceeded', execution.status)


    




