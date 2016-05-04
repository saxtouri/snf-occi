
"""
This it the entry point for paste deploy .

Paste config file needs to point to egg:<package name>:<entrypoint name>:

use = egg:snfOCCI#sample_app

sample_app entry point is defined in setup.py:

entry_points='''
[paste.app_factory]
sample_app = snf_voms:main
''',

which point to this function call (<module name>:function).
"""

# W0613:unused args
# pylint: disable=W0613

from snfOCCI import APIserver


#noinspection PyUnusedLocal
def main(global_config, **settings):
    """
This is the entry point for paste into the OCCI OS world.
"""
    return APIserver.MyAPP()