Build the image
---------------
$ docker build -t snf-occi-manual-ci:<version>

This will build a new image, which can be pushed or kept local.

Run a new container
-------------------
You need either a client proxy or a pair of keys.

If you have a pair of keys, load the directory containing them as /root/.globus
Then run the appropriate commands to generate a proxy

$ docker run -v ${HOME}/.globus:/root/.globus -ti snf-occi-manual-ci:latest
# fetch -p 20
# voms-proxy-init -voms fedcloud.egi.eu -rfc

If you have a valid proxy, load it somewhere on the machine

$ docker run -v my_proxy:/data/my_proxy  -ti snf-occi-manual-ci:latest

What is in the container
------------------------
You will find all the tools from egifedcloud/fedcloud-userinterface:latest plus
a shell script to test the snf-occi application.

To run the script, you must set some variables, either when you RUN the
container or while you are inside the container.

OCCI_ENDPOINT
USER_PROXY
OS_TPL
RESOURCE_TPL

For instance, if you have a proxy, you may want to run something like:

$ docker run -v my_proxy:/data/my_proxy \
    -e OCCI_ENDPOINT="https://okeanos-occi2.hellasgrid.gr:9000" \
    -e USER_PROXY="/data/my_proxy" \
    -e OS_TPL="debian_base" -e RESOURCE_TPL="c2r2048d20drbd" \
    -ti snf-occi-manual-ci:latest
