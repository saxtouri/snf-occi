.. snf-occi documentation master file, created by
   sphinx-quickstart on Mon Mar 26 13:45:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

snf-occi's documentation!
====================================

**snf-occi** snf-occi implements the OCCI specification on top of synnefo’s API in order to achieve greater interoperability in common tasks referring cyclades management. This module is a translation bridge between OCCI and the Openstack API and is designed to be as independent as possible from the rest IaaS, providing an OCCI compatibility layer to other services using Openstack API. 

**snf-occi** is based in modules provided by kamaki cli-tool when dealing with REST API calls to Openstack.

.. toctree::
   :maxdepth: 2

About Open Cloud Computing Interface (OCCI)
----------
The current OCCI specification consists of the following three documents:

* `OCCI Core <http://ogf.org/documents/GFD.183.pdf>`_
* `OCCI Infrastructure <http://ogf.org/documents/GFD.184.pdf>`_
* `OCCI HTTP rendering <http://ogf.org/documents/GFD.185.pdf>`_

The master document for the OCCI specification is at `OCCI Specification <http://occi-wg.org/about/specification/>`_

OCCI and Cyclades
-----------------
The OCCI implementation in Cyclades is going to be based in the OCCI Infrastructure specification, in which common Cloud IaaS components are described. The correspondence between OCCI and Cyclades is as follows:

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


 
**Note:** Metadata info in synnefo's servers cannot be represented (clearly) using OCCI's components.


OCCI requirements
------------------
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
By now we have considered implementing only the **Compute** backend of the OCCI to Cyclades/Openstack API bridge and we are planning to extend it for **networking** and **storage** capabilities.

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

