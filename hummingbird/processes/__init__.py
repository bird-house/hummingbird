from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker
from .wps_ioos import IOOSCChecker
from .wps_cdo_op import CDOOperation
from .wps_cdo_sinfo import CDOInfo
from .wps_cdo_bbox import CDOBBox
from .wps_ensembles import Ensembles
from .wps_cfchecker import CFChecker
from .wps_hdh_cfchecker import HDHCFChecker
from .wps_hdh_qachecker import QualityChecker

processes = [
    NCDump(),
    SpotChecker(),
    IOOSCChecker(),
    CFChecker(),
    HDHCFChecker(),
    QualityChecker(),
    CDOOperation(),
    CDOInfo(),
    CDOBBox(),
    Ensembles(),
]
