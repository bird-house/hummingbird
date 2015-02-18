import nose.tools
from nose import SkipTest
from nose.plugins.attrib import attr

from owslib.wps import monitorExecution

from __init__ import TESTDATA, SERVICE, CREDENTIALS, WpsTestCase

class SurfConPlotProcessTestCase(WpsTestCase):

    @attr('online')
    def test_surfconplot_pr(self):
        #raise SkipTest
        inputs = []
        inputs.append(('credentials', CREDENTIALS))
        inputs.append(('model', 'MPI-ESM-LR'))
        inputs.append(('cmor_table', 'Amon'))
        inputs.append(('experiment', 'historical'))
        inputs.append(('ensemble', 'r1i1p1'))
        inputs.append(('start_year', '2001'))
        inputs.append(('end_year', '2005'))
        
        output=[('output', True), ('namelist', True), ('log', True), ('reference', True)]
        execution = self.wps.execute(identifier="surfconplot", inputs=inputs, output=output)
        monitorExecution(execution, sleepSecs=1)

        nose.tools.ok_(execution.status == 'ProcessSucceeded', execution.status)
        #nose.tools.ok_(False, execution.processOutputs[0].reference)



    




