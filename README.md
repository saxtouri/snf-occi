snf-occi
========
snf-occi 0.2 implements the OCCI 1.1 procotol for Synnefo clouds. Since version
0.2, authentication is performed by an external keystone-compatible service,
like Astavoms.

Installation
-------------
First, you need to install the required dependencies which can be found here:

* `pyssf <https://code.grnet.gr/attachments/download/1182/pyssf-0.4.5.tar>`_
* `kamaki <https://code.grnet.gr/projects/kamaki>`_  

Then you can install **snf-occi** API translation server by cloning our latest source code:

* `snf-occi <https://code.grnet.gr/projects/snf-occi>`_ 

**NOTE**: Before running setup.py you have to edit the **config.py** setting up:

* API Server port
* VM hostname naming pattern (FQDN providing the id of each compute resource)
* VM core architecture

Finally you can start the API translation server by running **snf-occi**

More
----
Read the docs for more documentation, or from here:
https://github.com/grnet/snf-occi/blob/master/docs/index.rst
