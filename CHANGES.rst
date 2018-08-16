Changes
*******

0.6.0 (2018-08-16)
==================

* Using new deployment without Buildout.
* Regenerated from Cookiecutter template.
* Updated docs.
* Travis tests on Python 2.7/3.x.
* Disabled processes due to dependency conflicts:
  * cfchecker
  * QA checker
  * cmor checker

0.5.8 (2018-08-13)
==================

* Fix wsgi app init (#13).
* Updated versions.cfg.
* Updated setuptools 2.12.0.
* Added cython to environment.yml.

0.5.7 (2018-04-04)
==================

* updated compliance checker 3.1.1.
* cleaned up code.
* allow multiple input files for cdo_bbox and cdo_indices.
* updated cdo 1.9.0
* updated python-cdo 1.3.4
* updated cfchecker 3.0.5
* added cdo_copy process.
* update cmor checker 3.2.8
* display version number in service title.
* using compliance checker patch for ESGF OpenDAP access.
* using pytest skikif.
* added process cdo_inter_mpi for CDO Remapping of NetCDF File(s) with multiprocessing.

0.5.6 (2017-05-18)
==================

* updated ceda cfchecker 3.0.4.
* added opendap input parameter to cfchecker.
* added wsgi application.
* update pywps recipe 0.9.0.

0.5.5 (2017-05-08)
==================

* updated compliance-checker 3.0.3.
* pinned pygeoif=0.6 for compliance checker.
* updated cdo 1.8.1
* added cmor checker process.
* added cdo indices process.
* updated pywps recipe 0.8.8.
* update conda recipe 0.3.6.

0.5.4 (2017-03-27)
==================

* update compliance-checker 3.0.1
* added opendap input parameter and using metadata to indicate opendap mime-type.


0.5.3 (2017-01-27)
==================

* update qa-dkrz 0.6.3.
* fixed multiline abstracts.

0.5.2 (2017-01-04)
==================

* update qa-dkrz 0.6.2.
* using __version__ constant.
* fixed install on ubuntu 16.04: update conda environment (lxml, icu, libxslt).
* update cdo=1.7.2.

0.5.1 (2016-12-23)
==================

* added CORDEX and CMIP5 tests to spotchecker.
* updated pywps recipe 0.8.2.
* fixed wps caps test.
* updated qa-dkrz 0.6.1.

0.5.0 (2016-12-01)
==================

* converted all processes to pywps-4.
* updated qa-dkrz 0.6.0.

0.4.4 (2016-11-24)
==================

* updated qa-dkrz 0.5.17.
* updated ioos compliance checker 3.0.0
* added spotchecker process.
* replaced ncmeta process by ncdump.
* added opendap url parameter add ncdump, compliance-checker and spotchecker.
* updated conda env.

0.4.3 (2016-10-19)
==================

* updated dockerfile.
* updated setuptools and buildout version.

0.4.2 (2016-10-04)
==================

* update ioos compliance-checker 2.3.0.
* added output_format option to compliance-checker.

0.4.1 (2016-09-26)
==================

* updated ioos compliance-checker 2.2.1 and qa-dkrz 0.5.14.


0.4.0 (2016-07-30)
==================

* update buildout
* update pywps 3.2.6

0.3.1 (2016-06-14)
==================

* using pytest.
* moved processes and tests to hummingbird package.
* updated pywps recipe.
* update dkrz checker, cfchecker and ioos checker

0.3.0 (2016-01-21)
==================

* removed malleefowl dependency.

0.2.3 (2016-01-20)
==================

* replaced malleefowl.process.WPSProcess with pywps.Process.WPSProcess.
* updated dockerfile and docker recipe.
* using ioos conda channel.
* updated compliance checker (ioos).
* ncplot process added.
* stormtrack process added.


0.2.2 (2015-08-14)
==================

* IOOS compliance checker added.
* qa-dkrz cf checker added.
* cdo ensembles operation added.

0.2.1 (2015-08-04)
==================

* update cfchecker 2.0.8 ... using numpy 1.9.
* tika metadata parser process added.
* updated supervisor/pywps recipe.
* logging to stderr/supervisor.

0.2.0 (2015-02-24)
==================

* Now possible to use shared anaconda installation.

0.1.3 (2015-02-23)
==================

* cfchecker added
* using anaconda environment
* esmvaltools processes added
* added werkzeug python dependency

0.1.2 (2014-11-24)
==================

* Using Buildout 2.x.

0.1.1 (2014-11-11)
==================

* Using Makefile from birdhousebuilder.bootstrap to install and start application.


0.1.0 (2014-09-04)
==================

Initial Paris Release
