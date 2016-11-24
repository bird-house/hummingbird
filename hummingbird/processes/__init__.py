from .wps_ncdump import NCDump
from .wps_spotchecker import SpotChecker
from .wps_ioos import IOOSCChecker

processes = [
    NCDump(),
    SpotChecker(),
    IOOSCChecker(),
]
