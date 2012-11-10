# -*- coding:utf-8 -*-

import utils
import sys
import random


# seed current timestamp
utils.reseed()


def gens(name):
    '''Get register generator from name.'''
    gen_name = name + '_gen'
    try:
        return globals()[gen_name]
    except:
        return None


##############################
# Primitive types Generators #
##############################

# Generate integers
def rand_int(min=0, max=sys.maxint):
    return random.randint(min, max)


def int_gen(min=0, max=sys.maxint):
    """Integer generator."""
    for x in utils.x_gen(rand_int, min, max):
        yield x

# Generate strings
import string


def rand_str(minlen=1, maxlen=64, chrset=string.letters + string.digits):
    len_ = minlen
    if minlen != maxlen:
        # a variable-length string
        len_ = rand_int(minlen, maxlen)
    return ''.join(random.choice(chrset) for _ in xrange(len_))


def str_gen(len_=64, chrset=string.letters + string.digits):
    """Fixed-length string generator."""
    for x in utils.x_gen(rand_str, len_, len_, chrset):
        yield x


def varstr_gen(minlen=1, maxlen=64, chrset=string.letters + string.digits):
    """Variable-length string generator."""
    for x in utils.x_gen(rand_str, minlen, maxlen, chrset):
        yield x


##############################
# Telecom-related Generators #
##############################

MSISDN_CC = '+86'  # China's country code
MSISDN_SEGS = ['135', '136', '137', '138', '139', '155', '156', '157', '158', '159']

utils.reseed()


def rand_msisdn(segs=MSISDN_SEGS, cc_prefix=False):
    msisdn = cc_prefix and MSISDN_CC or ""
    msisdn += random.choice(segs)   # number segment
    msisdn += rand_str(minlen=8, maxlen=8, chrset=string.digits)  # area code + user number
    return msisdn


def msisdn_gen(segs=MSISDN_SEGS, cc_prefix=False):
    """MSISDN generator."""
    for x in utils.x_gen(rand_msisdn, segs, cc_prefix):
        yield x


IMSI_MCC = '460'
IMSI_MNC = ['00', '02', '07', '01', '03']


def rand_imsi():
    mcc = IMSI_MCC
    mnc = random.choice(IMSI_MNC)
    msin = rand_str(minlen=10, maxlen=10, chrset=string.digits)
    return mcc + mnc + msin


def imsi_gen():
    """IMSI generator."""
    for x in utils.x_gen(rand_imsi):
        yield x


#################################
# Filesystem-related Generators #
#################################

PATH_CHRSET = list(string.lowercase) * 10 + ['_', '-', '.']
PATH_SEP = '/'


def rand_path(min_fn=1, max_fn=10,
              min_depth=1, max_depth=5,
              prefix=[], suffix=[],
              abs=True):
    _rand_path = lambda: rand_str(minlen=min_fn, maxlen=max_fn, chrset=PATH_CHRSET)
    parts = utils.rand_list(_rand_path,
                            minlen=min_depth,
                            maxlen=max_depth,
                            prefix=prefix,
                            suffix=suffix)

    p = PATH_SEP.join(parts)
    if abs and p[0:1] != PATH_SEP:
        p = PATH_SEP + p

    return p


def path_gen(min_fn=1, max_fn=10,
             min_depth=1, max_depth=5,
             prefix=[], suffix=[]):
    """Path generator."""
    for x in utils.x_gen(rand_path,
                         min_fn=min_fn, max_fn=max_fn,
                         min_depth=min_depth, max_depth=max_depth,
                         prefix=prefix, suffix=suffix):
        yield x


#######################################
# HTTP/Network/Web-related Generators #
#######################################

def rand_ip(prefix=[]):
    parts = prefix[:]
    r = rand_int()
    for _ in range(len(prefix), 4):
        parts.append(str(r & 255))
        r = r >> 8

    return '.'.join(parts)


def ip_gen(prefix=[]):
    """IP generator."""
    for x in utils.x_gen(rand_ip, prefix):
        yield x


# Generator HTTP status code

# the most-seen http status codes
# ref: http://webhostinghelpguy.inmotionhosting.com/website-optimization/http-status-codes-a-guide-to-the-most-common-responses/
# HTTP_STATUS = [
#   '100',   # Continue
#   '200',   # OK
#   '300',   # Multiple choices
#   '301',   # Moved Permanently
#   '302',   # Found
#   '304',   # Not Modified
#   '400',   # Bad Request
#   '401',   # Unauthorized
#   '403',   # Forbidden
#   '404',   # Not Found
#   '410',   # Gone
#   '500',   # Internal Server Error
#   '501',   # Not Implemented
#   '503'    #Service Unavailable
# ]

# http status ditribution
HTTP_STATUS_DIST = {
    0.99: ['200'],
    0.01: ['100', '300', '301', '302', '304', '400', '401', '403', '404', '410', '500', '501', '503']
}


def rand_status(status_dist=HTTP_STATUS_DIST):
    return utils.prob_choice(status_dist, default=['200'])


def status_gen(status_dist=HTTP_STATUS_DIST):
    """HTTP status code generator."""
    for x in utils.x_gen(rand_status, status_dist):
        yield x

# Generator host names
HOST_SUFFIX = ['com', 'cn', 'net', 'org', 'com.cn', 'jp', 'us', 'uk']


def rand_host(min_hn=3, max_hn=10,
              min_depth=2, max_depth=4,
              prefix=[], suffix=[]):
    # choose one suffix from HOST_SUFFIX to make the host seems reasonable
    if suffix is None or len(suffix) == 0:
        suffix = HOST_SUFFIX

    _rand_host = lambda: rand_str(min_hn, max_hn, string.lowercase)
    parts = utils.rand_list(_rand_host, min_depth, max_depth, prefix, suffix)
    return '.'.join(parts)


def host_gen(min_hn=3, max_hn=10,
             min_depth=2, max_depth=4,
             prefix=[], suffix=[]):
    """Host name generator."""
    for x in utils.x_gen(rand_host, **locals()):
        yield x


# Generate URLs
def rand_url(schema='http://',
             min_hn_depth=2, max_hn_depth=4,
             hn_prefix=[], hn_suffix=[],
             min_path_depth=2, max_path_depth=4,
             path_prefix=[], path_suffix=[]):
    host = rand_host(min_depth=min_hn_depth,
                     max_depth=max_hn_depth,
                     prefix=hn_prefix,
                     suffix=hn_suffix)
    path = rand_path(min_depth=min_path_depth,
                     max_depth=max_path_depth,
                     prefix=path_prefix,
                     suffix=path_suffix,
                     abs=True)
    return schema + host + path


def url_gen(schema='http://',
            min_hn_depth=2, max_hn_depth=4,
            hn_prefix=[], hn_suffix=[],
            min_path_depth=2, max_path_depth=4,
            path_prefix=[], path_suffix=[]):
    """URL generator."""
    for x in utils.x_gen(rand_url, **locals()):
        yield x

# Generate web agent names
WEB_AGENTS = [
    "MAUI_WAP_Browser",
    "LG-KG70 MIC/1.1.14 MIDP-2.0/CLDC-1.1 UNTRUSTED/1.0",
    "Jakarta Commons-HttpClient/3.1",
    "Nokia6300/2.0 (07.21) Profile/MIDP-2.0 Configuration/CLDC-1.1",
    "MOT-V360i/08.D5.09R MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1",
    "HTC DIAMOND2",
    "HTC HD PRO",
    "NOKIA N97"]


def rand_webagent(agents=WEB_AGENTS):
    return random.choice(agents)


def webagent_gen(agents=WEB_AGENTS):
    """Web agent generator."""
    for x in utils.x_gen(rand_webagent, agents):
        yield x


# test
if __name__ == '__main__':
    a_host_gen = gens('host1')

    print a_host_gen
