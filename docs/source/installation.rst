.. _installation:

Installation
************

Check out code from the Hummingbird github repo and start the installation::

   $ git clone https://github.com/bird-house/hummingbird.git
   $ cd hummingbird
   $ make clean install

For other install options run ``make help`` and read the documention of the `Makefile <http://birdhousebuilderbootstrap.readthedocs.org/en/latest/usage.html#makefile>`_.

After successful installation you need to start the services. Hummingbird is using `Anaconda <https://www.continuum.io/>`_ Python distribution system. All installed files (config etc ...) are below the Anaconda root folder which is by default in your home directory ``~/anaconda``. Now, start the services::

   $ make start    # starts supervisor services
   $ make status   # shows supervisor status

The depolyed WPS service is by default available on http://localhost:8092/wps?service=WPS&version=1.0.0&request=GetCapabilities.


Check the log files for errors:

.. code-block:: sh

   $ tail -f  ~/birdhouse/var/log/pywps/hummingbird.log
   $ tail -f  ~/birdhouse/var/log/supervisor/hummingbird.log


Using docker-compose
====================

Start hummingbird with docker-compose (docker-compose version > 1.7):

.. code-block:: sh

   $ docker-compose up

By default the WPS is available on port 8080: http://localhost:8080/wps?service=WPS&version=1.0.0&request=GetCapabilities.

You can change the ports and hostname with environment variables:

.. code-block:: sh

  $ HOSTNAME=hummingbird HTTP_PORT=8092 SUPERVISOR_PORT=48092 docker-compose up

Now the WPS is available on port 8092: http://hummingbird:8092/wps?service=WPS&version=1.0.0&request=GetCapabilities.
