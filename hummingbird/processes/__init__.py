from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker
from .wps_ioos import IOOSCChecker
from .wps_cdo_op import CDOOperation
from .wps_cdo_sinfo import CDOInfo

processes = [
    NCDump(),
    SpotChecker(),
    IOOSCChecker(),
    CDOOperation(),
    CDOInfo(),
]
