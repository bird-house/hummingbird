Hummingbird
===========

Hummingbird (the bird)
  *Hummingbirds are among the smallest of birds. They hover in mid-air at rapid wing flapping rates, typically around 50 times per second, but possibly as high as 200 times per second, allowing them also to fly at speeds exceeding 15 m/s (54 km/h; 34 mph), backwards or upside down. [..].* (`Wikipedia https://en.wikipedia.org/wiki/Hummingbird`_).

Hummingbird is a collection of WPS processes for general tools like cdo used in the climate science community.


Installation
------------

Check out code from the Hummingbird github repo and start the installation::

   $ git clone https://github.com/bird-house/hummingbird.git
   $ cd hummingbird
   $ ./requirements.sh
   $ ./install.sh


After successful installation you need to start the services. Hummingbird is using `Anaconda http://www.continuum.io/`_ Python distribution system. All installed files (config etc ...) are below the Anaconda root folder which is by default in your home directory ``~/anaconda``. Now, start the services::

   $ cd ~/anaconda
   $ etc/init.d/supervisor start
   $ etc/init.d/nginx start

The depolyed WPS service is by default available on http://localhost:8092/wps?service=WPS&version=1.0.0&request=GetCapabilities.

Check the log files for errors::

   $ tail -f  ~/anaconda/var/log/pywps/hummingbird.log
   $ tail -f  ~/anaconda/var/log/pywps/hummingbird_trace.log

Configuration
-------------

If you want to run on a different hostname or port then change the default values in ``custom.cfg``::

   $ cd hummingbird
   $ vim custom.cfg
   $ cat custom.cfg
   [settings]
   hostname = localhost
   http-port = 8092

After any change to your ``custom.cfg`` you **need** to run ``install.sh`` again and restart the ``supervisor`` service::

  $ ./install.sh
  $  ~/anaconda/etc/init.d/supervisor restart


Update
------

When updating your installation you may run ``clean.sh`` to remove outdated Python dependencies::

   $ cd hummingbird
   $ git pull
   $ ./clean.sh
   $ ./requirement.sh
   $ ./install.sh

And then restart the ``supervisor`` and ``nginx`` service.


Authors
-------

* `DKRZ http://www.dkrz.de`_
* `Climate Service Center http://www.climate-service-center.de/`_
* `IPSL http://www.ipsl.fr/`_


