# -*- coding:utf-8 -*-

import utils
import prims
import random
import time
import string
import fs

# reseed now
utils.reseed()

def rand_ip(prefix=[]):
    ip_parts = prefix[:]
    if ip_parts is None:
        ip_parts = []
    for i in range(len(ip_parts), 4):
        part = prims.rand_int(min=0, max=255)
        ip_parts.append(str(part))

    return '.'.join(ip_parts)

def ip_gen(prefix=[]):
    """IP generator."""
    for x in utils.x_gen(rand_ip, prefix):
        yield x


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

# http status ocurr ditribution
HTTP_STATUS_DIST = {
    0.99 : ['200'],
    0.01 : ['100', '300', '301', '302', '304', '400', '401', '403', '404', '410', '500', '501', '503']
}

def rand_status(status_dist=HTTP_STATUS_DIST):
    rand = random.random()
    base = 0
    for prob, stats in status_dist.iteritems():
        if rand >= base and rand < base + prob:
            return random.choice(stats)
        base += prob

    # return 200 for default
    return '200'

def status_gen(status_dist=HTTP_STATUS_DIST):
    """HTTP status code generator."""
    for x in utils.x_gen(rand_status, status_dist):
        yield x


HOST_SUFFIX = ['com', 'cn', 'net', 'org', 'com.cn', 'jp', 'us', 'uk']

def rand_host(min_hn=3, max_hn=10, 
              min_depth=2, max_depth=4, 
              prefix=[], suffix=[]):
    _prefix = prefix is None and [] or prefix[:]
    _suffix = suffix is None and [] or suffix[:]

    if len(_suffix) == 0:
        # choose one suffix from HOST_SUFFIX to make the host seems reasonable
        _suffix = [random.choice(HOST_SUFFIX)]

    seen_len = len(_prefix) + len(_suffix)

    parts = []
    depth = prims.rand_int(min_depth, max_depth)
    depth = max(seen_len, depth)

    for i in range(seen_len, depth):
        part = prims.rand_str(min_hn, max_hn, string.lowercase)
        parts.append(part)

    parts = _prefix + parts + _suffix
    return '.'.join(parts)

def host_gen(min_hn=3, max_hn=10, 
             min_depth=2, max_depth=4, 
             prefix=[], suffix=[]):
    """Host name generator."""
    for x in utils.x_gen(rand_host, 
                         min_hn=min_hn, max_hn=max_hn, 
                         min_depth=min_depth, max_depth=max_depth, 
                         prefix=prefix, suffix=suffix):
        yield x


def rand_url(schema='http://', 
             min_hn_depth=2, max_hn_depth=4, 
             hn_prefix=[], hn_suffix=[],
             min_path_depth=2, max_path_depth=4,
             path_prefix=[], path_suffix=[]):
    host = rand_host(min_depth=min_hn_depth, max_depth=max_hn_depth, 
                     prefix=hn_prefix, suffix=hn_suffix)
    path = fs.rand_path(min_depth=min_path_depth, max_depth=max_path_depth, 
                        prefix=path_prefix, suffix=path_suffix, abs=True)
    return schema + host + path

def url_gen(schema='http://',
            min_hn_depth=2, max_hn_depth=4,
            hn_prefix=[], hn_suffix=[],
            min_path_depth=2, max_path_depth=4,
            path_prefix=[], path_suffix=[]):
    """URL generator."""
    for x in utils.x_gen(rand_url, schema,
                         min_hn_depth, max_hn_depth, hn_prefix, hn_suffix,
                         min_path_depth, max_path_depth, path_prefix, path_suffix):
        yield x


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
    for x in url_gen():
        print x
        time.sleep(0.1)
