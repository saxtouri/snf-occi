.. snf-occi documentation master file, created by
   sphinx-quickstart on Mon Mar 26 13:45:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About snf-occi
==============

**snf-occi** snf-occi is an OCCI API proxy for the Synnefo IaaS cloud. The
purpose of snf-occi is to provide and OCCI REST API for Synnefo's Cyclades API,
which provides compute, networking and volume services.

The implementation of snf-occi is based on Openstack OCCI Interface (OOI)
project, since version 0.3. OOI is a WSGI proxy for OpenStack. Synnefo API is
(almost) compatible with OpenStack, so snf-occi patches OOI wherever needer to
ensure the desired API compatibility. Clients running on OOI should be able to
run on snf-occi as well.

**snf-occi** is depends on kamaki library for communicating with Synnefo, and 
OOI for receiving and understanding OCCI calls.

.. toctree::
   :maxdepth: 2

About Open Cloud Computing Interface (OCCI)
-------------------------------------------
OCCI unifies various cloud compute services in a common API and a product of
the EGI initiative. For more information on OCCI: www.ogf.org

OCCI and Cyclades
-----------------
The OCCI implementation for Cyclades currently implements OCCI 1.1
Infrastructure specification. The correspondence between OCCI and Cyclades is
as follows:

+-------------------------+-------------------------+
|OCCI                     |Cyclades                 |
+=========================+=========================+
|Compute                  |Synnefo servers          |
+-------------------------+-------------------------+
|OS Template              |Synnefo images           |
+-------------------------+-------------------------+
|Resource Template        |Synnefo flavors          |
+-------------------------+-------------------------+
|Networking               |Synnefo Networking       |
+-------------------------+-------------------------+
|Storage                  |Synnefo Volumes          |
+-------------------------+-------------------------+


.. Note: Metadata info in Synnefo's servers cannot be represented (clearly) using OCCI's components.


Current progress
=================
We currently have an adequate implementation of the **compute** API and we are
planning to extend it for **networking** and **volumes** as soon as possible.
We will also provide the corresponding implementations for OCCI 1.2, as soon as
they are implemented in OOI.

Installation
-------------

The following instructions have been tested on Debian Jessy with pythoh-pip
installed. It is suggested to install Paste and PasteScript for deployment.

::

  $ git clone https://github.com/grnet/snf-occi
  $ cd snf-occi
  $ cp soi/config.py.template snfOCCI/config.py
  $ vim soi/confg.py
  ...
  $ python setup.py install

**NOTE**: edit the **config.py** before running the service. In the following
example, we replicate the settings of the hellasgrid service, but you can set
your own cloud and astavoms settings in your own deployment

::

  #  Copy this file as config.py and fill in the appropriate values
  
  AUTH_URL = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
  CA_CERTS = '/etc/ssl/certs/ca-certificates.crt'
  KEYSTONE_URL = 'https://okeanos-astavoms.hellasgrid.gr'

  HOST = '127.0.0.1'
  PORT = '8080'
  PASTE_INI = '/path/to/snf-occi/ci/soi.ini''

snf-occi is a simple WSGI python application with basic paste support. A full
scale deployment is out of the scope of this document, but deployments with
apache and gunicorn have been tested and work well.

Running with docker
===================

To test snf-occi, you can build and use a docker image, as described in the
"ci/README.md" file, or just follow these steps:

::

    $ docker build -t snf-occi-ci https://github.com/grnet/snf-occi#master:ci
    $ docker run -ti --name occi-ci --net host -p 127.0.0.1:8080:8080 \
        -e AUTH_URL='https://accounts.okeanos.grnet.gr/identity/v2.0' \
        -e KEYSTONE_URL='https://okeanos-astavoms.hellasgrid.gr' -d \
        snf-occi-ci


Testing
=======

Functional tests
----------------

The current snf-occi has good test coverage. Two equivalent sets of functional
tests (curl and rOCCI) in the form of bash scripts can be found in
"soi/tests/functional/". To run the script, make sure you have setup following
environment variables:

::

  $ export OCCI_ENDPOINT="http:127.0.0.1:8080"
  $ export TOKEN="Your-Synnefo-User-Token"
  $ export USER_PROXY="/path/to/your/VOMS/proxy"
  $ export OS_TPL="13"
  $ export RESOURCE_TPL="6f1f7205-cf4c-4b8c-ae77-7c419747bcbd"

The USER_PROXY is only needed if you run the rOCCI-based "run_function_tests.sh",
while TOKEN is only needed if you run the "run_curl_tests.sh" script.

You can setup a docker client for testing. Follow the
"soi/tests/functional/README.md" instructions and test the application with the
prepared queries or the examples of the current document. The instructions will
guide you to build a docker image based on the
`egifedcloud/fedcloud-userinterface` with all the functional tests loaded in
the container.

Examples
--------
For the examples below we assume server is running on localhost (port 8080) and authentication token is $TOKEN. For the HTTP requests we are using **curl**. All
these tests are also programmed in "soi/tests/functional/run_curl_tests.sh"

* Retrieve all registered Kinds, Actions and Mixins:

  ::

    curl -X GET localhost:8080/-/ -H 'X-Auth-Token: $TOKEN'

* List all VMs:

  ::

    curl -X GET localhost:8080/compute -H 'X-Auth-Token: $TOKEN'

* Create a new VM described by the flavor 13 and using the image
  6f1f7205-cf4c-4b8c-ae77-7c419747bcbd:

  ::
 
    curl -X POST localhost:8080/compute/ \
    -H 'Category: compute; scheme=http://schemas.ogf.org/occi/infrastructure#; class="kind";' \
    -H 'X-OCCI-Attribute: occi.core.title = newVM' -H 'Category: 13; scheme=http://schemas.ogf.org/occi/infrastructure#;' \
    -H 'Category: 6f1f7205-cf4c-4b8c-ae77-7c419747bcbd; scheme=http://schemas.ogf.org/occi/infrastructure#;' \
    -H 'X-Auth-Token: $TOKEN' -H 'Content-type: text/occi'

* Retrieve all the details of th VM with identifier $ID

  ::

    curl -X GET localhost:8080/compute/$ID -H 'X-Auth-Token: $TOKEN'

* Start/Stop/Restart a VM with $ID:

  ::

    curl -X POST -H 'X-Auth-Token: $TOKEN' localhost:8080/compute/$ID?action=start \
    -H 'Category: start ; scheme=\"http://schemas.ogf.org/occi/infrastructure/compute/action#\"; class=\"action\"'

    curl -X POST -H 'X-Auth-Token: $TOKEN' localhost:8080/compute/$ID?action=stop \
    -H 'Category: stop ; scheme=\"http://schemas.ogf.org/occi/infrastructure/compute/action#\"; class=\"action\"'

    curl -X POST -H 'X-Auth-Token: $TOKEN' localhost:8080/compute/$ID?action=restart \
    -H 'Category: restart ; scheme=\"http://schemas.ogf.org/occi/infrastructure/compute/action#\"; class=\"action\"'

* Delete the VM with identifier $ID

  ::
  
    curl -X DELETE localhost:8080/compute/$ID -H 'X-Auth-Token: $TOKEN'


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

