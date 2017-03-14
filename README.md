snf-occi
========
snf-occi 0.3 implements the OCCI 1.1 protocol for Synnefo clouds. Since version
0.2, authentication is performed by an external keystone-compatible service,
like "Astavoms". The major change is the abandonment of "snfOCCI" in favor of "OOI".

"OOI" is the Openstack OCCI Interface. It is used in snf-occi, wrapped by the newly introduced "SOI" package (Synnefo OCCI Interface). "SOI" is responsible for patching "OOI" so that it is compatible with Synnefo API.

More
----
Read the docs for more documentation, or from here:
https://github.com/grnet/snf-occi/blob/master/docs/index.rst
