.. snf-occi documentation master file, created by
   sphinx-quickstart on Mon Mar 26 13:45:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About snf-occi
==============

**snf-occi** snf-occi implements the OCCI specification on top of Synnefo’s API in order to achieve greater interoperability in common tasks referring cyclades management. This module is a translation bridge between OCCI and the Openstack API and is designed to be as independent as possible from the rest IaaS, providing an OCCI compatibility layer to other services using Openstack API. 

**snf-occi** is based in modules provided by kamaki library-tool when dealing with REST API calls to Openstack.

.. toctree::
   :maxdepth: 2

About Open Cloud Computing Interface (OCCI)
-------------------------------------------
The current OCCI specification consists of the following three documents:

* `OCCI Core <http://ogf.org/documents/GFD.183.pdf>`_
* `OCCI Infrastructure <http://ogf.org/documents/GFD.184.pdf>`_
* `OCCI HTTP rendering <http://ogf.org/documents/GFD.185.pdf>`_

The master document for the OCCI specification is at `OCCI Specification <http://occi-wg.org/about/specification/>`_

OCCI and Cyclades
-----------------
The OCCI implementation for Cyclades is going to be based in the OCCI 1.1 Infrastructure specification, in which common Cloud IaaS components are described. The correspondence between OCCI and Cyclades is as follows:

+-------------------------+-------------------------+
|OCCI                     |Cyclades                 |
+=========================+=========================+
|Compute                  |Synnefo servers          |
+-------------------------+-------------------------+
|OS Template              |Synnefo images           |
+-------------------------+-------------------------+
|Resource Template        |Synnefo flavors          |
+-------------------------+-------------------------+
|Networking               |NA                       |
+-------------------------+-------------------------+
|Storage                  |NA                       |
+-------------------------+-------------------------+


 
**Note:** Metadata info in Synnefo's servers cannot be represented (clearly) using OCCI's components.


OCCI requirements
-----------------
Due to OCCI's structure there cannot be straightforward mapping to Cyclades/OpenStack API. The missing elements are networking and storage capabilities using current Cyclades API.

OCCI operations
****************

Below you can see the required procedures/operations for OCCI compatibility.
   
* Handling the query interface
   * Query interface must be found under path /-/
   * Retrieve all registered Kinds, Actions and Mixins
   * Add a mixin definition
   * Remove a mixin definition

* Operation on paths in the name-space 
   * Retrieving the state of the name-space hierarchy
   * Retrieving all Resource instances below a path
   * Deletion of all Resource instances below a path

* Operations on Mixins and Kinds
   * Retrieving all Resource instances belonging to Mixin or Kind
   * Triggering actions to all instances of a Mixin or a Kind
   * Associate resource instances with a Mixin or a Kind
   * Full update of a Mixin collection
   * Dissociate resource instances from a Mixin

* Operations on Resource instances
   * Creating a resource instance
   * Retrieving a resource instance
   * Partial update of a resource instance
   * Full update of a resource instance
   * Delete a resource instance
   * Triggering an action on a resource instance

* Handling Link instances
   * Inline creation of a Link instance
   * Retrieving Resource instances with defined Links
   * Creating of Link Resource instance


OCCI client/server library
==========================

pyssf is a collection of OCCI python modules. It aims to provide a high-level interface for the integration of OCCI to other new or existing applications. 

Features:
---------

* It includes a REST API service with the OCCI specifications already implemented
* It only requires a custom backend and registry to interact with Cyclades

Current progress
=================
By now we have considered implementing only the **Compute** backend of the OCCI to Cyclades/Openstack API bridge and we are planning to extend it for **networking** and **storage** capabilities. It is possible to implement the remaining capabilities directly for OCCI 1.2, though.

Installation
-------------
Install **snf-occi** API translation server by cloning our latest source code:

::

  git clone https://github.com/grnet/snf-occi
  cd snf-occi
  cp snfOCCI/config.py.template snfOCCI/config.py
  python setup.py install

**NOTE**: edit the **config.py** before running the service

snf-occi is a simple WSGI python application with basic paste support. A full scale deployment is out of the scope of this document, but it is expected to use standard tools like apache and gunicorn to setup the service.

Examples:
---------
For the examples below we assume server is running on localhost (port 8888) and authentication token is $AUTH. For the HTTP requests we are using **curl**.

* Retrieve all registered Kinds, Actions and Mixins:

  ::

    curl -v -X GET localhost:8888/-/ -H 'Auth-Token: $AUTH'

* Create a new VM described by the flavor 'C2R2048D20' and using the image 'Debian'

  ::
 
    curl -v -X POST localhost:8888/compute/ 
    -H 'Category: compute; scheme=http://schemas.ogf.org/occi/infrastructure#;  class="kind";' 
    -H 'X-OCCI-Attribute: occi.core.title = newVM' -H 'Category: C2R2048D20; scheme=http://schemas.ogf.org/occi/infrastructure#; ' 
    -H 'Category: Debian; scheme=http://schemas.ogf.org/occi/infrastructure#;' -H 'Auth-Token: $AUTH' 
    -H 'Content-type: text/occi'

* Retrieve all the details of th VM with identifier $ID

  ::

    curl -v -X GET localhost:8888/compute/$ID -H 'Auth-Token: $AUTH'

* Delete the VM with identifier $ID

  ::
  
    curl -v -X DELETE localhost:8888/compute/$ID -H 'Auth-Token: $AUTH'

Testing
-------
Here is how to run a local paste server. This is useful only for experimenting
and development and should not be used in production.

::

  sudo apt-get install python-pastedeploy
  cp snfOCCI/paste_deploy/test-server.py .
  python test-server.py
    server is running on 127.0.0.1:8080

Follow the test/README.md instructions to setup a client e.g., with docker, and
test the application with the prepared queries or the examples bellow.

A smart way to test the application is by using the `egifedcloud/fedcloud-userinterface`. Make sure you have valid and authorized proxy certificates in your ${HOME}/.globus directory, and then start a cointainer shell loaded with all necessary client tools. E.g., to perform a "list servers" operation:

  ::

    $ docker run -v /home/saxtouri/.globus:/root/.globus -it egifedcloud/fedcloud-userinterface /bin/bash
    # fetch-crl -p 20
    # voms-proxy-init --voms fedcloud.egi.eu -rfc
      Your proxy is stored at /tmp/x509up_u0
    # occi --endpoint https://snf-occi.example.com --action list --resource compute -n x509 -x /tmp/x509up_u0 -X


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

