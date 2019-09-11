.. _configuration:

Configuration
=============

.. warning::

  Please read the PyWPS documentation_ to find details about possible configuration options.


Command-line options
--------------------

You can overwrite the default `PyWPS`_ configuration by using command-line options.
See the Hummingbird help which options are available::

    $ hummingbird start --help
    --hostname HOSTNAME        hostname in PyWPS configuration.
    --port PORT                port in PyWPS configuration.

Start service with different hostname and port::

    $ hummingbird start --hostname localhost --port 5001

Use a custom configuration file
-------------------------------

You can overwrite the default `PyWPS`_ configuration by providing your own
PyWPS configuration file (just modifiy the options you want to change).
Use one of the existing ``sample-*.cfg`` files as example and copy them to ``etc/custom.cfg``.

For example change the hostname (*demo.org*) and logging level:

.. code-block:: console

   $ cd hummingbird
   $ vim etc/custom.cfg
   $ cat etc/custom.cfg
   [server]
   url = http://demo.org:5000/wps
   outputurl = http://demo.org:5000/outputs

   [logging]
   level = DEBUG

Start the service with your custom configuration:

.. code-block:: console

   # start the service with this configuration
   $ hummingbird start -c etc/custom.cfg

Example
~~~~~~~

Here is an example of a customized configuration.
Please read the PyWPS documentation_ for a detailed description of the options, like `outputpath` and `workdir`.

.. code-block:: ini

  [server]
  url = http://demo.org:5000/wps
  outputurl = http://demo.org:5000/outputs
  outputpath = /var/lib/pywps/outputs
  workdir = /var/lib/pywps/tmp

  [logging]
  level = DEBUG

Find more examples in `etc/`.


.. _PyWPS: http://pywps.org/
.. _documentation: https://pywps.readthedocs.io/en/master/configuration.html
