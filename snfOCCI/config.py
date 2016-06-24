SERVER_CONFIG = {
    'port': 9000,
    'hostname': 'snf-136122.vm.okeanos.grnet.gr',
    'compute_arch': 'x86'
    }

KAMAKI_CONFIG = {
    'compute_url': 'https://cyclades.okeanos.grnet.gr/compute/v2.0/',
    'astakos_url': 'https://accounts.okeanos.grnet.gr/identity/v2.0/',
    'network_url': 'https://cyclades.okeanos.grnet.gr/network/v2.0'
}
        
VOMS_CONFIG = {
    'enable_voms' : 'True',           
    'voms_policy' : '/etc/snf/voms.json',
    'vomsdir_path' : '/etc/grid-security/vomsdir/',
    'ca_path': '/etc/grid-security/certificates/',
    'cert_dir' : '/etc/ssl/certs/',
    'key_dir' : '/etc/ssl/private/',
    'token' : '2iar6Uk36gBjFkdn0HfsxWZBB3TKQjoklYtZO9TRed0'
}

ASTAVOMS_URL = 'https://okeanos-astavoms.hellasgrid.gr'

