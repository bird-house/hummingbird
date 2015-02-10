.. _processes:
WPS Processes
*************

We describe here the WPS processes available in Hummingbird.

CFChecker
=========

The `cfchecker <https://pypi.python.org/pypi/cfchecker>`_ checks NetCDF files for compliance to the Climate Forcast Conventions (CF) standard.

The process expects one or more NetCDF files which should be checked and an optional parameter for the CF version.

WPS process description
-----------------------

Using the default Hummingbird installation the ``DescribeProcess`` request is as follows:

http://localhost:8092/wps?service=WPS&version=1.0.0&request=DescribeProcess&identifier=cfchecker

The XML response of the WPS service is the following document:

.. literalinclude:: wps_cfchecker.xml
    :language: xml
    :linenos:

The WPS Parameters are:

*resource*
     Is the input parameter to provide one or more URLs (``http://``, ``file://``) to NetCDF files. 
     It is a WPS `ComplexData <http://pywps.wald.intevation.org/documentation/course/ogc-wps/index.html#complexdata>`_ type with MIME-type ``application/x-netcdf``.

*cf_version*
     Is an optional input parameter to provide the CF version to check against. It is a WPS `LiteralData <http://pywps.wald.intevation.org/documentation/course/ogc-wps/index.html#literaldata>`_ type with a set of allowed values (1.1, 1.2, ..., auto).

*output*
     Is the output parameter to provide the report of the CF check as text document. 
     It is a WPS ComplexData type with MIME-type ``text/plain``.












