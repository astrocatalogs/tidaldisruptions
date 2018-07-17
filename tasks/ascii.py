# -*- coding: utf-8 -*-
"""ASCII datafiles, often produced from LaTeX tables in the original papers,
but sometimes provided as supplementary datafiles on the journal webpages.
"""
import csv
import os

from astropy.io.ascii import read

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import pbar
from decimal import Decimal


def do_ascii(catalog):
    """Process ASCII files that were extracted from datatables appearing in
    published works.
    """
    task_str = catalog.get_current_task_str()

    # iPTF16fnl
    file_path = os.path.join(catalog.get_current_task_repo(), 'ASCII',
                             'iPTF16fnl.tex')
    data = read(file_path, format='latex')
    name, source = catalog.new_entry(
        'iPTF16fnl', bibcode='2017ApJ...844...46B')
    header = [s[s.find("{") + 1:s.find("}")].replace('$', '')
              for s in list(data.columns)]
    bands = header[2:]
    for row in pbar(data, task_str):
        for bi, band in enumerate(bands):
            if row[bi + 2] == '--':
                continue
            mag, err = row[bi + 2].split('$\pm$')
            tel, ins = row[1].split('+')
            photodict = {
                PHOTOMETRY.MAGNITUDE: mag,
                PHOTOMETRY.TIME: str(row[0]),
                PHOTOMETRY.U_TIME: 'MJD',
                PHOTOMETRY.BAND: band,
                PHOTOMETRY.TELESCOPE: tel,
                PHOTOMETRY.INSTRUMENT: ins,
                PHOTOMETRY.SOURCE: source
            }
            if float(err) > 0.0:
                photodict[PHOTOMETRY.E_MAGNITUDE] = err
            catalog.entries[name].add_photometry(**photodict)

    # 2011ApJ...735..106D
    file_path = os.path.join(catalog.get_current_task_repo(), 'ASCII',
                             '2011ApJ...735..106D.tsv')
    with open(file_path, 'r') as f:
        name, source = catalog.new_entry('CSS100217:102913+404220',
                                         bibcode='2011ApJ...735..106D')
        data = list(
            csv.reader(
                f, delimiter='\t', quotechar='"', skipinitialspace=True))
        telescope = ''
        instrument = ''
        for r, row in enumerate(pbar(data, task_str)):
            if row[0][0] == '#' and len(row[0]) > 1:
                infosplit = row[0][1:].split(',')
                telescope = infosplit[0]
                instrument = ''
                if len(infosplit) > 1:
                    instrument = infosplit[1]
                bands = row[2:]
            if row[0][0] == '#':
                continue
            mjd = row[0]
            for ci, col in enumerate(row[2:]):
                csplit = col.split('+or-')
                if len(csplit) <= 1:
                    continue
                mag, emag = (x.strip() for x in csplit)
                photodict = {
                    PHOTOMETRY.TIME: mjd,
                    PHOTOMETRY.BAND: bands[ci],
                    PHOTOMETRY.MAGNITUDE: mag,
                    PHOTOMETRY.E_MAGNITUDE: emag,
                    PHOTOMETRY.TELESCOPE: telescope,
                    PHOTOMETRY.SOURCE: source
                }
                if instrument:
                    photodict[PHOTOMETRY.INSTRUMENT] = instrument
                if telescope == 'SDSS':
                    photodict[PHOTOMETRY.HOST] = True
                if telescope == 'Swift':
                    photodict[PHOTOMETRY.INCLUDES_HOST] = True
                catalog.entries[name].add_photometry(**photodict)

    # 2016arXiv160201088H
    file_path = os.path.join(catalog.get_current_task_repo(), 'ASCII',
                             '2016arXiv160201088H.txt')
    with open(file_path, 'r') as f:
        name, source = catalog.new_entry('ASASSN-15oi',
                                         bibcode='2016arXiv160201088H')
        data = list(
            csv.reader(
                f, delimiter=' ', quotechar='"', skipinitialspace=True))
        for r, row in enumerate(pbar(data, task_str)):
            if row[0][0] == '#':
                continue
            photodict = {
                PHOTOMETRY.TIME: row[0],
                PHOTOMETRY.BAND: row[1],
                PHOTOMETRY.MAGNITUDE: row[2],
                PHOTOMETRY.E_MAGNITUDE: row[3],
                PHOTOMETRY.TELESCOPE: row[4],
                PHOTOMETRY.SOURCE: source
            }
            catalog.entries[name].add_photometry(**photodict)

    catalog.journal_entries()
    return
