DCE Python SDK (Developing. Not Ready!)
=======================================

Python library for DaoCloud Enterprise API

Install
-------

::

    $ python setup.py install

    or

    $ pip install git+https://github.com/dceplugins/dce-client.git

Usage
-----

::

    >> from dce import DCEAPIClient
    >> client = DCEAPIClient('http://192.168.100.30', username='admin', password='admin')
    >> print('DCE Version: ' + client.dce_version)
