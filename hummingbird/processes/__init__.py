from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker

processes = [
    NCDump(),
    SpotChecker(),
]
