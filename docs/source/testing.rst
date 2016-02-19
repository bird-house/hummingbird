.. _testing:

Running unit tests
******************

For some tests you need an ESGF proxy certificate. You can generate one with the `Phoenix <http://pyramid-phoenix.readthedocs.org/en/latest/>`_ web client at ``My Account/Update Credentials``::

   $ export TEST_CREDENTIALS=http://localhost:8081/wpsoutputs/malleefowl/output-a41c06ae-a540-11e4-90b4-68a72837e1b8.pem

Run all tests::

   $ make test

or with nosetests::

   $ bin/nosetests unit_tests





