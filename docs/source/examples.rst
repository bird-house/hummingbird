.. _example_docker:

Example: Using Docker
=====================

If you just want to try the Hummingbird Web Processing Service you can also use the `Docker <https://hub.docker.com/r/birdhouse/hummingbird/>`_ image::

  $ docker run -i -d -p 9001:9001 -p 8000:8000 -p 8080:8080 birdhouse/hummingbird

Open your browser and enter the url of the supervisor service:

  http://localhost:9001/

Run a GetCapabilites WPS request:

  http://localhost:8080/wps?service=WPS&version=1.0.0&request=getcapabilities

Run DescribeProcess WPS request for *CFChecker*:

  http://localhost:8080/wps?service=WPS&version=1.0.0&request=describeprocess&identifier=cfchecker

Execute *CFChecker* process with public available data:

  http://localhost:8080/wps?service=WPS&version=1.0.0&request=Execute&identifier=cfchecker&DataInputs=dataset=http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep/vwnd.sfc.2015.nc&RawDataOutput=output

Install *Birdy* WPS command line tool from Anaconda (Anaconda needs to be installed and in your ``PATH``)::

  $ conda install -c birdhouse birdhouse-birdy

Use Birdy to access Hummingbird WPS service::

  $ export WPS_SERVICE=http://localhost:8080/wps
  $ birdy -h
  $ birdy cfchecker -h
  $ birdy cfchecker --dataset http://www.esrl.noaa.gov/psd/thredds/fileServer/Datasets/ncep/vwnd.sfc.2015.nc
