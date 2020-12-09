# -*- coding:utf-8 -*-

import random
import string

from . import utils
from .primitive import rand_str


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
    for x in utils.rand_gen(rand_msisdn, segs, cc_prefix):
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
    for x in utils.rand_gen(rand_imsi):
        yield x
