There are two options to setup a testing snf-occi deployment: with docker or
from scratch.

Deploy with docker (recommended)
---

Use docker to build the snf-occi image and deploy the snf-occi in a container.
In the following example, we use the "master" branch, but you can change this
when running the container, but setting the SNF_OCCI_BRANCH variable to the
branch you want to test.

::
    $ echo "Build the docker snf-occi-ci image"
    $ docker build -t snf-occi-ci https://github.com/grnet/snf-occi.git#develop:ci
    ...
    $ echo "Run the occi-ci container"
    $ docker run -ti --name occi-ci --net host -p 127.0.0.1:8080:8080 \
        -e SNF_OCCI_BRANCH="master" \
        -e AUTH_URL='https://accounts.okeanos.grnet.gr/identity/v2.0' \
        -e KEYSTONE_URL='https://okeanos-astavoms.hellasgrid.gr' -d \
        snf-occi-ci
    ...
    $ echo "(optional) check the service logs"
    $ docker logs -f occi-ci
    serving on http://127.0.0.1:8080
    ...

.. note: To use a different host port, try "-p 127.0.0.1:<PORT>:8080" e.g.,
    "-p 127.0.0.1:9000:8080"

Deploy from scratch
---

Here is how to run a local paste server. This is useful only for experimenting
and development and should not be used in production. We suggest to run this
test in a sandboxed environment e.g., virtualenv

::

  $ virtualenv mytest
  $ source mytest/bin/activate
  $ pip install Paste PasteDeploy
  $ cp soi/config.py.template soi/config.py
  $ vim soi/config.py
  ... (set the appropriate values here) ...
  $ python setup.py install
  $ python ci/run-server.py .
    serving on http://127.0.0.1:8080
    ...
