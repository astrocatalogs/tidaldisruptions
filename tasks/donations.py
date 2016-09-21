"""Import tasks for data directly donated to the Open Supernova Catalog.
"""
import csv
import os

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import pbar
from cdecimal import Decimal


def do_donations(catalog):
    task_str = catalog.get_current_task_str()

    datafile = os.path.join(catalog.get_current_task_repo(), 'Donations',
                            'Auchettl-2016.csv')

    with open(datafile, 'r') as f:
        tsvin = csv.reader(f, delimiter=',', skipinitialspace=True)

        for ri, row in enumerate(pbar(tsvin, task_str)):
            if ri <= 3 or not row or not row[0]:
                continue
            (name, source) = catalog.new_entry(
                row[0], srcname='Open TDE Catalog')
            smjd = Decimal(row[3])
            emjd = str(smjd + Decimal(row[4]) / Decimal(86400))[:9]
            mjd = [str(smjd), str(emjd)]
            photodict = {
                PHOTOMETRY.TIME: mjd,
                PHOTOMETRY.U_TIME: 'MJD',
                PHOTOMETRY.COUNTS: row[12],
                PHOTOMETRY.ENERGY: ["0.3", "2.0"],
                PHOTOMETRY.U_ENERGY: 'keV',
                PHOTOMETRY.FLUX: row[21],
                PHOTOMETRY.U_FLUX: 'ergs/cm^2/s',
                PHOTOMETRY.SOURCE: source
            }
            if row[11] == 'D':
                photodict[PHOTOMETRY.E_COUNTS] = row[13]
                photodict[PHOTOMETRY.E_LOWER_FLUX] = row[22]
                photodict[PHOTOMETRY.E_UPPER_FLUX] = row[23]
            else:
                photodict[PHOTOMETRY.UPPER_LIMIT] = True
            catalog.entries[name].add_photometry(**photodict)

    catalog.journal_entries()
    return
