# -*- coding:utf-8 -*-

import utils
import prims
import random
import time
import string


MSISDN_CC = '+86'  # China's country code
MSISDN_SEGS = ['135', '136', '137', '138', '139', '155', '156', '157', '158', '159']

utils.reseed()

def rand_msisdn(segs=MSISDN_SEGS, cc_prefix=False):
    msisdn = cc_prefix and MSISDN_CC or ""
    msisdn += random.choice(segs) # number segment
    msisdn += prims.rand_str(min_len=8, max_len=8, chrset=string.digits) # area code + user number
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
    msin = prims.rand_str(min_len=10, max_len=10, chrset=string.digits)
    return mcc + mnc + msin

def imsi_gen():
    """IMSI generator."""
    for x in utils.x_gen(rand_imsi):
        yield x

# test
if __name__ == '__main__':
    for x in msisdn_gen():
        print x
        time.sleep(0.1)

