.. snf-occi documentation master file, created by
   sphinx-quickstart on Mon Mar 26 13:45:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

About snf-occi
==============

**snf-occi** is an OCCI_  API proxy for the Synnefo_ IaaS cloud. The purpose
of snf-occi is to provide an OCCI REST API for the Cyclades API of Synnefo,
which provides compute, networking and volume services.

The implementation of snf-occi is based on the OOI_ (Openstack OCCI Interface)
project, since version 0.3. OOI is a WSGI proxy for OpenStack. Synnefo API is
(almost) compatible with OpenStack, so snf-occi patches OOI wherever needed to
ensure the desired API compatibility. Clients running on OOI should be able to
run on snf-occi as well.

**snf-occi** depends on the kamaki_ library for communicating with Synnefo and
OOI for receiving and understanding OCCI calls.

.. _OCCI: http://occi-wg.org/
.. _Synnefo: https://synnefo.org
.. _OOI: https://github.com/openstack/ooi
.. _kamaki: https://github.com/grnet/kamaki/

.. toctree::
   :maxdepth: 2

About Open Cloud Computing Interface (OCCI)
-------------------------------------------
OCCI unifies various cloud compute services in a common API and a product of
the EGI initiative. For more information on OCCI visit `Open Grid Forum`_
website.

.. _`Open Grid Forum`: http://www.ogf.org

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


.. note:: Metadata info in Synnefo's servers cannot be represented clearly
          using OCCI's components.


Current progress
=================
We currently have an adequate implementation of the **compute** API and we are
planning to extend it for **networking** and **volumes** as soon as possible.
We will also provide the corresponding implementations for OCCI 1.2, as soon as
they are implemented in OOI.

There are two ways to run snf-occi. You can run it natively or with docker.
Running with docker should be used for testing purposes.

Running Natively
================

Installation
------------

The following instructions have been tested on Debian Jessie.

Make sure you have installed python development libraries, e.g. using apt:

::

  # apt install python-dev


If you try to install on Debian Jessie system-wide you might run into some
problems, since Debian Jessie has an older version of python-six, which is
a dependency of pip. So, it is probably easier to use virtualenv for your
installation:

::

  # apt install virtualenv
  $ virtualenv /path/to/new/environment
  $ source /path/to/new/environment/bin/activate
  $ git clone https://github.com/grnet/snf-occi

Edit the ``soi/config.py`` file before running the service. You can find a
template in ``soi/config.py.template``. In the following example, we replicate
the settings of the hellasgrid service, but you can set your own cloud and
astavoms settings in your own deployment:

::

  AUTH_URL = 'https://accounts.okeanos.grnet.gr/identity/v2.0'
  CA_CERTS = '/etc/ssl/certs/ca-certificates.crt'
  KEYSTONE_URL = 'https://okeanos-astavoms.hellasgrid.gr'

  HOST = '127.0.0.1'
  PORT = '8080'
  PASTE_INI = '/path/to/snf-occi/ci/soi.ini'

  # Possible values (1,2)
  # Volume type=1, drbd
  # Volume type=2, archipelago
  VOLUME_TYPE = 2

  DISABLED_METHOD = ()


Finally, run the installation

::

  $ python setup.py install

.. note:: If you get a ``RuntimeError: maximum recursion depth exceeded``, try
  upgrading the ``setuptools`` package of your virtual environment:

  ::

    (venv)$ pip install setuptools --upgrade


Running
-------

If this installation is for testing purposes, you can run ``ci/run-server.py``:

::

  (venv)$ python ci/run-server.py


For production, snf-occi should run easily with gunicorn:

::

  $ gunicorn --paste /path/to/soi.ini

An example paste configuration is included in ci/soi.ini, but you can add
gunicorn specific configuration as follows:

::

  [composite:main]
  use = egg:Paste#urlmap
  /:snf_occiapp

  [app:snf_occiapp]
  use = egg:snf-occi#snf_occi_app

  [server:main]
  use = egg:gunicorn#main
  host = 127.0.0.1
  port = 8080
  workers = 3

.. note:: If you install gunicorn to the same virtual environment, you might get
  a ``SyntaxError: invalid syntax``. You can remedy this by upgrading
  pip:

  ::

    (venv)$ pip install pip --upgrade


Running with docker
===================

To test snf-occi you can build and use a docker image by following these steps:

::

  $ docker build -t snf-occi-ci https://github.com/grnet/snf-occi.git#develop:ci
  $ docker run -ti --name occi-ci --net host -p 127.0.0.1:8080:8080 \
      -e SNF_OCCI_BRANCH="master" \
      -e AUTH_URL='https://accounts.okeanos.grnet.gr/identity/v2.0' \
      -e KEYSTONE_URL='https://okeanos-astavoms.hellasgrid.gr' -d \
      snf-occi-ci

The default branch for CI testing is "develop", but you can test any
branch you want by setting the SNF_OCCI_BRANCH environment variable.

Also, the docker installation uses ``ci/config.py`` and not ``soi/config.py``.

To use a different host port, try ``-p 127.0.0.1:<PORT>:8080``, e.g.
``-p 127.0.0.1:9000:8080``

.. note:: You might run into the following output:

  ::

    $ docker build -t snf-occi-ci https://github.com/grnet/snf-occi.git#develop:ci
    Step 0 : <!DOCTYPE
    INFO[0001] Unknown instruction: <!DOCTYPE

  This means that your docker does not support a git repository as a command line
  argument. The following command is equivalent, after cloning the repository:

  ::

    $ cd snf-occi
    $ docker build -t snf-occi-ci ci/


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

The USER_PROXY is only needed if you run the rOCCI-based "rocci/*.sh",
while TOKEN is only needed if you run the "curl/*.sh" script.

You can setup a docker client for testing. Follow the
"soi/tests/functional/README.md" instructions and test the application with the
prepared queries or the examples of the current document. The instructions will
guide you to build a docker image based on the
`egifedcloud/fedcloud-userinterface` with all the functional tests loaded in
the container.

Examples
--------
For the examples below we assume server is running on localhost (port 8080) and authentication token is $TOKEN. For the HTTP requests we are using **curl**. All
these tests are also programmed in "soi/tests/functional/curl/"

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

