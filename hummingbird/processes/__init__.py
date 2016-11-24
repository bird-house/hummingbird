from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker
from .wps_ioos import IOOSCChecker
from .wps_cdo_op import CDOOperation

processes = [
    NCDump(),
    SpotChecker(),
    IOOSCChecker(),
    CDOOperation(),
]
