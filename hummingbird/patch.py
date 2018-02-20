import requests

import logging
LOGGER = logging.getLogger("PYWPS")


def patch_compliance_checker():
    """
    Patch compliance_checker for ESGF OpenDAP with ``.dodsrc``.
    """
    def patched_is_opendap(url):
        '''
        Returns True if the URL is a valid OPeNDAP URL
        :param str url: URL for a remote OPeNDAP endpoint
        '''
        # If the server replies to a Data Attribute Structure request
        das_url = url + '.das'
        response = requests.get(das_url, allow_redirects=True)
        if 'xdods-server' in response.headers:
            return True
        # Check if it is an access restricted ESGF thredds service
        if response.status_code == 401 and \
            'text/html' in response.headers['content-type'] and \
                'The following URL requires authentication:' in response.text:
            return True
        return False
    from compliance_checker.protocols import opendap
    opendap.is_opendap = patched_is_opendap
