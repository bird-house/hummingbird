from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker
from .wps_ioos import IOOSCChecker
from .wps_cdo_op import CDOOperation
from .wps_cdo_sinfo import CDOInfo
from .wps_cdo_bbox import CDOBBox

processes = [
    NCDump(),
    SpotChecker(),
    IOOSCChecker(),
    CDOOperation(),
    CDOInfo(),
    CDOBBox(),
]
