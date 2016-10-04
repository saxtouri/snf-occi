snf-occi
========
snf-occi 0.3 implements the OCCI 1.1 protocol for Synnefo clouds. Since version
0.2, authentication is performed by an external keystone-compatible service,
like "Astavoms". The major change is the abandonment of "snfOCCI" in favor of "OOI".

"OOI" is the Openstack OCCI Interface. It is used in snf-occi, wrapped by the newly introduced "SOI" package (Synnefo OCCI Interface). "SOI" is responsible for patching "OOI" so that it is compatible with Synnefo API.

Installation
-------------
Clone snf-occi:

$ git clone https://github.com/grnet/snf-occi

Create file config.py and edit it with the correct settings:

$ cd snf-occi
$ cp soi/config.py.template soi/config.py
$ <your favorite editor> soi/config.py

**Note** make sure you have a config.py file before installing snf-occi. You don't need to put the correct settings yet, though. They can wait until deployment.

Install the application (dependences are installed automatically) :

$ python setup.py install

Finally you can start the API translation server with paste. We have provided a demonstration server for testing and development at "paste_deploy/test_server.py" but you should not use it for production.

More
----
Read the docs for more documentation, or from here:
https://github.com/grnet/snf-occi/blob/master/docs/index.rst
