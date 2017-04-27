from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker
from .wps_compliance_checker import CChecker
from .wps_cdo_op import CDOOperation
from .wps_cdo_sinfo import CDOInfo
from .wps_cdo_bbox import CDOBBox
from .wps_cdo_indices import CDOClimateIndices
from .wps_cdo_ensembles import CDOEnsembles
from .wps_cfchecker import CFChecker
from .wps_hdh_cfchecker import HDHCFChecker
from .wps_hdh_qachecker import QualityChecker
from .wps_cmor_checker import CMORChecker

processes = [
    NCDump(),
    SpotChecker(),
    CChecker(),
    CFChecker(),
    CMORChecker(),
    HDHCFChecker(),
    QualityChecker(),
    CDOOperation(),
    CDOInfo(),
    CDOBBox(),
    CDOClimateIndices(),
    CDOEnsembles(),
]
