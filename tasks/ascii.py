# -*- coding: utf-8 -*-
"""ASCII datafiles, often produced from LaTeX tables in the original papers,
but sometimes provided as supplementary datafiles on the journal webpages.
"""
import csv
import os

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import pbar
from cdecimal import Decimal


def do_ascii(catalog):
    """Process ASCII files that were extracted from datatables appearing in
    published works.
    """
    task_str = catalog.get_current_task_str()

    # 2016arXiv160201088H
    file_path = os.path.join(catalog.get_current_task_repo(),
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

    # 2011ApJ...741...73V
    file_path = os.path.join(catalog.get_current_task_repo(),
                             '2011ApJ...741...73V.txt')
    with open(file_path, 'r') as f:
        data = list(
            csv.reader(
                f, delimiter=' ', quotechar='"', skipinitialspace=True))
        bandcols = {}
        ebandcols = {}
        limitcols = {}
        for r, row in enumerate(pbar(data, task_str)):
            if r == 0:
                for ci, col in enumerate(row):
                    if col.startswith('MAG_'):
                        bandcols[ci] = col.replace('MAG_', '')
                    elif col.startswith('MAGERR_'):
                        ebandcols[col.replace('MAGERR_', '')] = ci
                    elif col.startswith('MAGLIM_'):
                        limitcols[col.replace('MAGLIM_', '')] = ci
                continue
            elif row[0][0] == '#':
                name, source = catalog.new_entry(
                    row[0].lstrip('#'), bibcode='2011ApJ...741...73V')
                continue
            mjd = row[0]
            for ci, col in enumerate(row):
                if ci in bandcols:
                    e_mag = str(-Decimal(row[ebandcols[bandcols[ci]]]))
                    if float(e_mag) < 0.0 or float(col) < 0.0:
                        mag = limitcols[bandcols[ci]]
                        e_mag = ''
                        upplim = True
                    else:
                        mag = col
                        upplim = False
                    photodict = {
                        PHOTOMETRY.TIME: mjd,
                        PHOTOMETRY.BAND: bandcols[ci],
                        PHOTOMETRY.MAGNITUDE: mag,
                        PHOTOMETRY.E_MAGNITUDE: e_mag,
                        PHOTOMETRY.UPPER_LIMIT: upplim,
                        PHOTOMETRY.SOURCE: source
                    }
                    catalog.entries[name].add_photometry(**photodict)

    catalog.journal_entries()
    return
