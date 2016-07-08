"""Tidal disruption-specific constant variables.
"""
from astropy import constants as const
from astropy import units as un


CLIGHT = const.c.cgs.value
KM = (1.0 * un.km).cgs.value

PREF_KINDS = ['heliocentric', 'cmb', 'spectroscopic',
              'photometric', 'host', 'cluster', '']

REPR_BETTER_QUANTITY = {
    'redshift',
    'ebv',
    'velocity',
    'lumdist',
    'discoverdate',
    'maxdate'
}

MAX_BANDS = [
    ['B', 'b', 'g'],  # B-like bands first
    ['V', 'G'],       # if not, V-like bands
    ['R', 'r']        # if not, R-like bands
]
