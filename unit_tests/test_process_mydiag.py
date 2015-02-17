import nose.tools
from unittest import TestCase
from nose import SkipTest
from nose.plugins.attrib import attr

from owslib.wps import monitorExecution

from __init__ import TESTDATA, SERVICE, CREDENTIALS, WpsTestCase

class MyDiagProcessTestCase(WpsTestCase):

    @attr('online')
    def test_mydiag_ta(self):
        #raise SkipTest
        inputs = []
        inputs.append(('output_format', 'ps'))
        inputs.append(('credentials', CREDENTIALS))
        inputs.append(('model', 'MPI-ESM-LR'))
        inputs.append(('variable', 'ta'))
        inputs.append(('cmor_table', 'Amon'))
        inputs.append(('experiment', 'historical'))
        inputs.append(('ensemble', 'r1i1p1'))
        inputs.append(('start_year', '2000'))
        inputs.append(('end_year', '2004'))
        
        output=[('output', True), ('namelist', True), ('log', True), ('ack', True)]
        execution = self.wps.execute(identifier="mydiag", inputs=inputs, output=output)
        monitorExecution(execution, sleepSecs=1)

        nose.tools.ok_(execution.status == 'ProcessSucceeded', execution.status)
        #nose.tools.ok_(False, execution.processOutputs[0].reference)




    



