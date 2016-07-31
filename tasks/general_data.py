# -*- coding: utf-8 -*-
"""General data import tasks.
"""
import csv
import os
import re
import urllib
from glob import glob

from astropy.time import Time as astrotime

from astrocats.catalog.utils import pbar_strings
from astrocats.tidaldisruptions.tidaldisruption import (TIDALDISRUPTION,
                                                        TidalDisruption)
from cdecimal import Decimal


def do_external(catalog):
    task_str = catalog.get_current_task_str()
    oldbanddict = {
        "Pg": {"instrument": "Pan-STARRS1",
               "band": "g"},
        "Pr": {"instrument": "Pan-STARRS1",
               "band": "r"},
        "Pi": {"instrument": "Pan-STARRS1",
               "band": "i"},
        "Pz": {"instrument": "Pan-STARRS1",
               "band": "z"},
        "Mu": {"instrument": "MegaCam",
               "band": "u"},
        "Mg": {"instrument": "MegaCam",
               "band": "g"},
        "Mr": {"instrument": "MegaCam",
               "band": "r"},
        "Mi": {"instrument": "MegaCam",
               "band": "i"},
        "Mz": {"instrument": "MegaCam",
               "band": "z"},
        "Su": {"instrument": "SDSS",
               "band": "u"},
        "Sg": {"instrument": "SDSS",
               "band": "g"},
        "Sr": {"instrument": "SDSS",
               "band": "r"},
        "Si": {"instrument": "SDSS",
               "band": "i"},
        "Sz": {"instrument": "SDSS",
               "band": "z"},
        "bU": {"instrument": "Bessel",
               "band": "U"},
        "bB": {"instrument": "Bessel",
               "band": "B"},
        "bV": {"instrument": "Bessel",
               "band": "V"},
        "bR": {"instrument": "Bessel",
               "band": "R"},
        "bI": {"instrument": "Bessel",
               "band": "I"},
        "4g": {"instrument": "PTF 48-Inch",
               "band": "g"},
        "4r": {"instrument": "PTF 48-Inch",
               "band": "r"},
        "6g": {"instrument": "PTF 60-Inch",
               "band": "g"},
        "6r": {"instrument": "PTF 60-Inch",
               "band": "r"},
        "6i": {"instrument": "PTF 60-Inch",
               "band": "i"},
        "Uu": {"instrument": "UVOT",
               "band": "U"},
        "Ub": {"instrument": "UVOT",
               "band": "B"},
        "Uv": {"instrument": "UVOT",
               "band": "V"},
        "Um": {"instrument": "UVOT",
               "band": "M2"},
        "U1": {"instrument": "UVOT",
               "band": "W1"},
        "U2": {"instrument": "UVOT",
               "band": "W2"},
        "GN": {"instrument": "GALEX",
               "band": "NUV"},
        "GF": {"instrument": "GALEX",
               "band": "FUV"},
        "CR": {"instrument": "Clear",
               "band": "r"},
        "RO": {"instrument": "ROTSE"},
        "X1": {"instrument": "Chandra"},
        "X2": {"instrument": "XRT"},
        "Xs": {"instrument": "XRT",
               "band": "soft"},
        "Xm": {"instrument": "XRT",
               "band": "hard"},
        "XM": {"instrument": "XMM"}
    }
    path_pattern = os.path.join(catalog.get_current_task_repo(),
                                'old-tdefit/*.dat')
    for datafile in pbar_strings(glob(path_pattern), task_str):
        f = open(datafile, 'r')
        tsvin = csv.reader(f, delimiter='\t', skipinitialspace=True)

        source = ''
        yrsmjdoffset = 0.
        for row in tsvin:
            if row[0] == 'name':
                name = re.sub('<[^<]+?>', '', row[1].split(',')[0].strip())
                name = catalog.add_entry(name)
            elif row[0] == 'citations':
                citarr = row[1].split(',')
                for cite in citarr:
                    if '*' in cite:
                        bibcode = urllib.parse.unquote(
                            cite.split('/')[-2].split("'")[0])
                        source = catalog.entries[name].add_source(
                            bibcode=bibcode)
            elif row[0] == 'nhcorr':
                hostnhcorr = True if row[1] == 'T' else False
            elif row[0] == 'restframe':
                restframe = True if row[1] == 'T' else False
            elif row[0] == 'yrsmjdoffset':
                yrsmjdoffset = float(row[1])
            if row[0] == 'redshift':
                redshift = float(row[1].split(',')[0].strip(' *'))

        f.seek(0)

        for row in tsvin:
            if not row or len(row) < 2 or not row[1]:
                continue
            if row[0] == 'redshift':
                for rs in [x.strip() for x in row[1].split(',')]:
                    catalog.entries[name].add_quantity('redshift',
                                                       rs.strip(' *'), source)
            elif row[0] == 'host':
                hostname = re.sub('<[^<]+?>', '', row[1])
                catalog.entries[name].add_quantity('host', hostname, source)
            elif row[0] == 'claimedtype':
                catalog.entries[name].add_quantity('claimedtype', row[1],
                                                   source)
            elif row[0] == 'citations':
                catalog.entries[name].add_quantity('citations', row[1], source)
            elif row[0] == 'notes':
                catalog.entries[name].add_quantity('notes', row[1], source)
            elif row[0] == 'nh':
                catalog.entries[name].add_quantity('nh', row[1], source)
            elif row[0] == 'photometry':
                timeunit = row[1]
                if timeunit == 'yrs':
                    timeunit = 'MJD'
                    if restframe:
                        # Currently presume only the time, not the flux, has
                        # been affected by redshifting.
                        time = str(yrsmjdoffset + float(row[2]) * 365.25 * (
                            1.0 + redshift))
                    else:
                        time = str(yrsmjdoffset + float(row[2]) * 365.25)
                    lrestframe = False
                else:
                    time = row[2]
                    if timeunit == 'floatyr':
                        timeunit = 'MJD'
                        time = str(astrotime(float(time), format='jyear').mjd)
                    lrestframe = restframe

                instrument = ''
                iband = row[3]
                if iband in oldbanddict:
                    if 'band' in oldbanddict[iband]:
                        band = oldbanddict[iband]['band']
                    if 'instrument' in oldbanddict[iband]:
                        instrument = oldbanddict[iband]['instrument']
                else:
                    band = iband
                upperlimit = True if row[6] == '1' else False
                if 'X' in iband:
                    # Old TDEFit stored counts in log
                    e_counts = str((Decimal(10.0)**(Decimal(row[4]) + Decimal(
                        row[5])) - Decimal(10.0)**Decimal(row[4]))
                                   if float(row[5]) != 0.0 else '')
                    counts = Decimal(10.0)**Decimal(row[4])
                    catalog.entries[name].add_photometry(
                        time=time,
                        u_time=timeunit,
                        band=band,
                        counts=counts,
                        e_counts=e_counts,
                        upperlimit=upperlimit,
                        restframe=lrestframe,
                        hostnhcorr=hostnhcorr,
                        instrument=instrument,
                        source=source)
                else:
                    magnitude = row[4]
                    e_magnitude = row[5] if float(row[5]) != 0.0 else ''
                    catalog.entries[name].add_photometry(
                        time=time,
                        u_time=timeunit,
                        band=band,
                        magnitude=magnitude,
                        e_magnitude=e_magnitude,
                        upperlimit=upperlimit,
                        restframe=lrestframe,
                        hostnhcorr=hostnhcorr,
                        instrument=instrument,
                        source=source)

    catalog.journal_entries()
    return


def do_internal(catalog):
    """Load events from files in the 'internal' repository, and save them.
    """
    task_str = catalog.get_current_task_str()
    path_pattern = os.path.join(catalog.get_current_task_repo(), '*.json')
    files = glob(path_pattern)
    catalog.log.debug("found {} files matching '{}'".format(
        len(files), path_pattern))
    for datafile in pbar_strings(files, task_str):
        new_event = TidalDisruption.init_from_file(
            catalog, path=datafile, clean=True)
        catalog.entries.update({new_event[TIDALDISRUPTION.NAME]: new_event})

    return
