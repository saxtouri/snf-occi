Upgrade guide from 0.5 (or less) to 0.6
---------------------------------------

To support OCCI 1.2, make sure OOI version >= 1.0.0
We have tested with OOI 1.1.1
If snf-occi runs in a virtual env::

    $ pip install ooi -U

Now, pull the code and install as usuall::

    $ python setup.py clean build install

If a WSGI is used, it needs to be restarted, e.g.::

    # service gunicorn restart

