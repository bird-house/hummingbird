.. _processes:

WPS Processes
*************

We describe here the WPS processes available in Hummingbird.

.. _caps:

WPS Capabilities
================

Using the default Hummingbird installation the ``GetCapabilities`` request is as follows:

http://localhost:8092/wps?service=WPS&version=1.0.0&request=GetCapabilities

The XML response of the WPS service is the following document:

.. literalinclude:: processes/wps_caps.xml
    :language: xml
    :emphasize-lines: 52,58,64
    :linenos:

.. _cfchecker:

CFChecker
=========

The `cfchecker <https://pypi.python.org/pypi/cfchecker>`_ checks NetCDF files for compliance to the Climate Forcast Conventions (CF) standard.

The process expects one or more NetCDF files which should be checked and an optional parameter for the CF version.

.. _cfchecker_description:

WPS process description
-----------------------

Using the default Hummingbird installation the ``DescribeProcess`` request is as follows:

http://localhost:8092/wps?service=WPS&version=1.0.0&request=DescribeProcess&identifier=cfchecker

The XML response of the WPS service is the following document:

.. literalinclude:: processes/wps_cfchecker.xml
    :language: xml
    :emphasize-lines: 9,26,46
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

WPS process execution
---------------------

An example execution of the cfchecker process with public available data:

http://localhost:8092/wps?service=WPS&version=1.0.0&request=Execute&identifier=cfchecker&DataInputs=resource=http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep/vwnd.sfc.2015.nc&RawDataOutput=output

The process is called with key/value parameters, synchronously and with direct output (``RawDataOutput``).

The resulting text document of the cfchecker report looks like the following:

.. literalinclude:: cf_output.txt
    :linenos:

CDO
===

to be continued ...












