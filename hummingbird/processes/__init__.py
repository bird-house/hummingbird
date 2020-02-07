from .wps_ncdump import NCDump
from .wps_compliance_checker import CChecker


processes = [
    NCDump(),
    CChecker(),
]
