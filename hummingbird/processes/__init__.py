from .wps_ncdump import NCDump
from .wps_compliance_checker import CChecker
from .wps_cfchecker import CFChecker


processes = [
    NCDump(),
    CChecker(),
    CFChecker(),
]
