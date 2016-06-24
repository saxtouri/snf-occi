'''
Created on Jul 31, 2013

@author: nassia
'''

import json
import M2Crypto
import ast

from logging import getLogger, DEBUG
import voms_helper
from kamaki.clients import ClientError
from astavomaki.client import AstavomsClient

# import saferun

LOG =  getLogger(__name__)


# Environment variable used to pass the request context
CONTEXT_ENV = 'snf.context'

SSL_CLIENT_S_DN_ENV = "SSL_CLIENT_S_DN"
SSL_CLIENT_CERT_ENV = "SSL_CLIENT_CERT"
SSL_CLIENT_CERT_CHAIN_ENV_PREFIX = "SSL_CLIENT_CERT_CHAIN_"

"""Global variables that contain VOMS related paths
"""
VOMS_POLICY = "/etc/snf/voms.json"
VOMSDIR_PATH = "/etc/grid-security/vomsdir/"
CA_PATH = "/etc/grid-security/certificates/"
VOMSAPI_LIB = "/usr/lib/libvomsapi.so.1"
#VOMSAPI_LIB = "voms.x86_64 0:2.0.10-3.el6" 
AUTOCREATE_USERS = False
PARAMS_ENV = 'snf_voms.params'

ASTAVOMS_URL = 'https://okeanos-astavoms.hellasgrid.gr'
ASTAVOMS_TOKEN = 'Nothing for now'


#saferun.logger.setLevel(DEBUG)
#@saferun.saferun
#def test_and_log_astavoms(ssl_certs):
#    astavoms = AstavomsClient(ASTAVOMS_URL, ASTAVOMS_TOKEN)
#    saferun.logger.info('LALA 1')
#    astavoms.astacert = '/etc/grid-security/certificates/TERENA-eScience-SSL-CA-3.pem'
#    saferun.logger.info('LALA 2')
#    saferun.logger.info('Authenticate this: {certs}'.format(certs=ssl_certs))
#    saferun.logger.info('LALA 3')
#    # Not tryied that yet, do it next
#    from kamaki.clients.utils import https
#    #https.patch_with_certs(CA_PATH)
#    https.patch_ignore_ssl()
#    r = astavoms.authenticate(**ssl_certs)
#    from kamaki.clients.utils import https
#    saferun.logger.info('SAFERUN RESPONSE: {0}'.format(json.dumps(r, indent=2)))
#    return r


#@saferun.saferun
#def compare_results(old, new):
#    saferun.logger.info('OLD: {old}\nNEW:{new}'.format(old=old, new=new))
#    keydiff = set(old).symmetric_difference(new)
#    saferun.logger.info('KEY DIFF: %s', keydiff)
#    for k in set(old).intersection(new):
#        ov, nv = old[k], new[k]
#        msg = '  OK' if ov == nv else '  diff: %s != %s' % (ov, nv)
#        saferun.logger.info('Check key %s ... %s' % (k, msg))


class VomsError():
    """Voms credential management error"""

    errors = {
        0: ('none', None),
        1: ('nosocket', 'Socket problem'),
        2: ('noident', 'Cannot identify itself (certificate problem)'),
        3: ('comm', 'Server problem'),
        4: ('param', 'Wrong parameters'),
        5: ('noext', 'VOMS extension missing'),
        6: ('noinit', 'Initialization error'),
        7: ('time', 'Error in time checking'),
        8: ('idcheck', 'User data in extension different from the real'),
        9: ('extrainfo', 'VO name and URI missing'),
        10: ('format', 'Wrong data format'),
        11: ('nodata', 'Empty extension'),
        12: ('parse', 'Parse error'),
        13: ('dir', 'Directory error'),
        14: ('sign', 'Signature error'),
        15: ('server', 'Unidentifiable VOMS server'),
        16: ('mem', 'Memory problems'),
        17: ('verify', 'Generic verification error'),
        18: ('type', 'Returned data of unknown type'),
        19: ('order', 'Ordering different than required'),
        20: ('servercode', 'Error from the server'),
        21: ('notavail', 'Method not available'),
    }

    http_codes = {
        5: (400, "Bad Request"),
        11: (400, "Bad Request"),
        14: (401, "Not Authorized"),
    }

    def __init__(self, code):
        short, message = self.errors.get(code, ('oops',
                                                'Unknown error %d' % code))
        message = "(%s, %s)" % (code, message)
    #    super(VomsError, self).__init__(message=message)

        code, title = self.http_codes.get(code, (500, "Unexpected Error"))
        self.code = code
        self.title = title

class VomsAuthN():
    """Filter that checks for the SSL data in the reqest.

    Sets 'ssl' in the context as a dictionary containing this data.
    """
    
    def __init__(self, *args, **kwargs):
        self.astavoms = AstavomsClient(ASTAVOMS_URL, ASTAVOMS_TOKEN)
        # VOMS stuff
        try:
            with open(VOMS_POLICY) as f:
                self.voms_json = json.load(f)
        except ValueError:
            raise ClientError(
                'Bad Formatted VOMS json',
                details='The VOMS json data was not corectly formatted in file %s' % VOMS_POLICY)
        except Exception as e:
            raise ClientError(
                'No loading of VOMS json file',
                details='The VOMS json file located in %s was not loaded (%s:, e)' % (
                    VOMS_POLICY, type(e), e))
        
        self._no_verify = False

        #super(VomsAuthN, self).__init__(*args, **kwargs)

    @staticmethod
    def _get_cert_chain(ssl_info):
        """Return certificate and chain from the ssl info in M2Crypto format"""
        cert = M2Crypto.X509.load_cert_string(ssl_info.get("cert"))
        chain = M2Crypto.X509.X509_Stack()
        for c in ssl_info.get("chain", []):
            aux = M2Crypto.X509.load_cert_string(c)
            chain.push(aux)
        return cert, chain

    def _get_voms_info(self, ssl_info):
        """Extract voms info from ssl_info and return dict with it."""
	# Use astavoms instead of doing it by yourself
	# astaresults = test_and_log_astavoms(ssl_info)

        from kamaki.clients.utils import https
        https.patch_ignore_ssl()
        return self.astavoms.authenticate(**ssl_info)
        # STOP HERE       
        
        # Keep this until verification is supported in astavoms
        try:
            cert, chain = self._get_cert_chain(ssl_info)
        except M2Crypto.X509.X509Error:
            raise ClientError(
                              'SSL data not verified',
                              details=CONTEXT_ENV)


        with voms_helper.VOMS(VOMSDIR_PATH,
                              CA_PATH, VOMSAPI_LIB) as v:

            if self._no_verify:
                v.set_no_verify()
               
            voms_data = v.retrieve(cert, chain)
            
            if not voms_data:
                # TODO(aloga): move this to a keystone exception
                raise VomsError(v.error.value)

            d = {}
            for attr in ('user', 'userca', 'server', 'serverca',
                         'voname',  'uri', 'version', 'serial',
                         ('not_before', 'date1'), ('not_after', 'date2')):
                if isinstance(attr, basestring):
                    d[attr] = getattr(voms_data, attr)
                else:
                    d[attr[0]] = getattr(voms_data, attr[1])

            d["fqans"] = []
            for fqan in iter(voms_data.fqan):
                if fqan is None:
                    break
                d["fqans"].append(fqan)

	# compare_results(d, astaresults)

        return d

    @staticmethod
    def _split_fqan(fqan):
        """
        gets a fqan and returns a tuple containing
        (vo/groups, role, capability)
        """
        l = fqan.split("/")
        capability = l.pop().split("=")[-1]
        role = l.pop().split("=")[-1]
        vogroup = "/".join(l)
        return (vogroup, role, capability)
    
    def _process_environ(self, environ):
        
        LOG.warning("Getting the environment parameters...")
        # the environment variable CONTENT_LENGTH may be empty or missing
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
            raise ClientError(
                'Not auth method provided',
                details='The request body is empty, while it should contain the authentication method')
            
        request_body = environ['wsgi.input'].read(request_body_size)
        
        # print request_body
        request_body = request_body.replace("true","\"true\"")
        request_body = request_body.replace('"','\'' )  

        try:
            params_parsed = ast.literal_eval(request_body)
        except Exception as e:
            LOG.warning('Skipping error: {t}: {e}'.format(t=type(e), e=e))
            print 'Skipping error: {t}: {e}'.format(t=type(e), e=e)
            params_parsed = {}
        params = {}
        for k, v in params_parsed.iteritems():
            if k in ('self', 'context'):
                continue
            if k.startswith('_'):
                continue
            params[k] = v
            
        
        environ[PARAMS_ENV] = params
        # print environ[PARAMS_ENV]

    def is_applicable(self, environ):
        """Check if the request is applicable for this handler or not"""
        print "Checking if the request is applicable for this handler"
        self._process_environ(environ)
        params = environ.get(PARAMS_ENV, {})
        auth = params.get("auth", {})
        if "voms" in auth:
            if "true" in auth["voms"]:
                return True
            else:
                raise ClientError(
                'Error in json',
                details='Error in JSON, voms must be set to true')
            
        return False

    def authenticate(self,ssl_data):

        try:
            voms_info = self._get_voms_info(ssl_data)
        except VomsError as e:
            raise e
        user_dn = voms_info["user"]
        user_vo = voms_info["voname"]
        user_fqans = voms_info["fqans"] 

        return (
            user_dn, user_vo, user_fqans, voms_info['snf:token'],
            voms_info['snf:project'])

          
    def process_request(self, environ):
        print "Inside process_request!!!!"
        if not self.is_applicable(environ):
            raise ClientError('This environ is not applicable')
            # return self.application

        ssl_dict = {
            "dn": environ.get(SSL_CLIENT_S_DN_ENV, None),
            "cert": environ.get(SSL_CLIENT_CERT_ENV, None),
            "chain": [],
        }
        for k, v in environ.iteritems():
            if k.startswith(SSL_CLIENT_CERT_CHAIN_ENV_PREFIX):
                ssl_dict["chain"].append(v)

        voms_info = self._get_voms_info(ssl_dict)

        params  = environ[PARAMS_ENV]
        
        tenant_from_req = params["auth"].get("tenantName", None)
        
        user_dn = voms_info["user"]
        user_vo = voms_info["voname"]
        user_fqans = voms_info["fqans"] 
        environ['REMOTE_USER'] = user_dn
        
        return (
            user_dn, user_vo, user_fqans, voms_info['snf:token'],
            voms_info['snf:project'])

