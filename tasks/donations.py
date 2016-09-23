"""Import tasks for data directly donated to the Open Supernova Catalog.
"""
import csv
import os

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import pbar
from astrocats.tidaldisruptions.tidaldisruption import TIDALDISRUPTION
from cdecimal import Decimal


def do_donations(catalog):
    task_str = catalog.get_current_task_str()

    datafile = os.path.join(catalog.get_current_task_repo(), 'Donations',
                            'Auchettl-2016.csv')

    with open(datafile, 'r') as f:
        tsvin = csv.reader(f, delimiter=',', skipinitialspace=True)

        for ri, row in enumerate(pbar(list(tsvin), task_str)):
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
                PHOTOMETRY.PHOTON_INDEX: row[17],
                PHOTOMETRY.LUMINOSITY: row[24],
                PHOTOMETRY.SOURCE: source
            }
            if row[11] == 'D':
                photodict[PHOTOMETRY.E_COUNTS] = row[13]
                photodict[PHOTOMETRY.E_LOWER_FLUX] = row[22]
                photodict[PHOTOMETRY.E_UPPER_FLUX] = row[23]
                photodict[PHOTOMETRY.E_LOWER_LUMINOSITY] = row[25]
                photodict[PHOTOMETRY.E_UPPER_LUMINOSITY] = row[26]
            else:
                photodict[PHOTOMETRY.UPPER_LIMIT] = True
            # Need to ask about nh that includes both MW and host
            if not row[15]:
                photodict[PHOTOMETRY.NHMW] = row[14]
            catalog.entries[name].add_photometry(**photodict)

    catalog.journal_entries()

    datafile = os.path.join(catalog.get_current_task_repo(), 'Donations',
                            'Auchettl-2016-meta.csv')
    with open(datafile, 'r') as f:
        tsvin = csv.reader(f, delimiter=',', skipinitialspace=True)

        for ri, row in enumerate(pbar(list(tsvin), task_str)):
            if ri <= 2 or not row or not row[0]:
                continue
            (name, source) = catalog.new_entry(
                row[0].strip(), srcname='Open TDE Catalog')
            sources = [source]
            for new_src in [x.strip() for x in row[7].split(',')]:
                sources.append(catalog.entries[name].add_source(
                    bibcode=new_src))
            catalog.entries[name].add_quantity(
                TIDALDISRUPTION.HOST, row[1].strip(), source=source)
            catalog.entries[name].add_quantity(
                TIDALDISRUPTION.HOST_RA, row[2].strip(), source=source)
            catalog.entries[name].add_quantity(
                TIDALDISRUPTION.HOST_DEC, row[3].strip(), source=source)
            catalog.entries[name].add_quantity(
                TIDALDISRUPTION.RA, row[4].strip(), source=source)
            catalog.entries[name].add_quantity(
                TIDALDISRUPTION.DEC, row[5].strip(), source=source)
            catalog.entries[name].add_quantity(
                TIDALDISRUPTION.REDSHIFT, row[6].strip(), source=source)
    return
