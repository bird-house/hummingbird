from .wps_ncdump import NCDump
from .wps_compliance_checker import CChecker
from .wps_spotchecker import SpotChecker


processes = [
    NCDump(),
    CChecker(),
    SpotChecker(),
]
