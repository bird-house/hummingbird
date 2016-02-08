from unittest import TestCase

SERVICE = "http://localhost:8092/wps"


class WpsTestCase(TestCase):
    """
    Base TestCase class, sets up a wps
    """

    @classmethod
    def setUpClass(cls):
        from owslib.wps import WebProcessingService
        cls.wps = WebProcessingService(SERVICE, verbose=False, skip_caps=False)
