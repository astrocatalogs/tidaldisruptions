"""Import tasks for data directly donated to the Open Supernova Catalog.
"""
import csv
import os

from astropy.io.ascii import read
from astropy.time import Time as astrotime

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

    # 2016arXiv161001788S
    datafile = os.path.join(catalog.get_current_task_repo(), 'Donations',
                            '2016arXiv161001788S.tex')

    data = read(datafile, format='latex')
    name, source = catalog.new_entry(
        'XMMSL1 J0740-85', bibcode='2016arXiv161001788S')
    for row in data[1:]:
        start = Decimal(
            astrotime(row['Date']
                      if row['Date'] != '1990' else '1990-01-01').mjd)
        end = str(start + Decimal(row['Exp time$^{b}$']) / Decimal('86400'))
        start = str(start)
        photodictbase = {PHOTOMETRY.U_TIME: 'MJD', PHOTOMETRY.SOURCE: source}
        photodictx = photodictbase.copy()
        photodictx[PHOTOMETRY.TELESCOPE] = row['Mission$^{a}$']
        photodictx[PHOTOMETRY.TIME] = [start, end]
        photodictx[PHOTOMETRY.ENERGY] = ['0.2', '2.0']
        photodictx[PHOTOMETRY.U_ENERGY] = 'keV'
        photodictx[PHOTOMETRY.U_FLUX] = 'ergs s^-1 cm^-2'
        fstr = row['Flux$^{c}$'].replace('$', '').replace('{', '').replace('}',
                                                                           '')
        if '<' in fstr:
            flux = fstr.replace('<', '')
            photodictx[PHOTOMETRY.FLUX] = str(
                Decimal(flux) * Decimal('1.0e-12'))
            photodictx[PHOTOMETRY.UPPER_LIMIT] = True
        else:
            flux = fstr.split('\pm')[0]
            photodictx[PHOTOMETRY.FLUX] = str(
                Decimal(flux) * Decimal('1.0e-12'))
            ferr = fstr.split('\pm')[-1]
            photodictx[PHOTOMETRY.E_FLUX] = str(
                Decimal(ferr) * Decimal('1.0e-12'))

        catalog.entries[name].add_photometry(**photodictx)

        for col in row.columns[4:]:
            val = str(row[col])
            if val == '--':
                continue
            mag, emag = str(row[col]).replace('$', '').replace(
                '{', '').replace('}', '').split('\pm')
            photodictu = photodictbase.copy()
            photodictu[PHOTOMETRY.TELESCOPE] = 'Swift'
            photodictu[PHOTOMETRY.INSTRUMENT] = 'UVOT'
            photodictu[PHOTOMETRY.TIME] = start
            photodictu[PHOTOMETRY.BAND] = col
            photodictu[PHOTOMETRY.MAGNITUDE] = mag
            photodictu[PHOTOMETRY.E_MAGNITUDE] = emag
            photodictu[PHOTOMETRY.SYSTEM] = 'Vega'
            catalog.entries[name].add_photometry(**photodictu)

    # 2016arXiv161003861A
    datafile = os.path.join(catalog.get_current_task_repo(), 'Donations',
                            '2016arXiv161003861A.cds')

    data = read(datafile, format='cds')
    name, source = catalog.new_entry(
        'XMMSL1 J0740-85', bibcode='2016arXiv161003861A')
    for row in data:
        photodict = {
            PHOTOMETRY.TIME: [row['tstart'], row['tstop']],
            PHOTOMETRY.FREQUENCY: str(Decimal(row['freq']) / Decimal('1.0e9')),
            PHOTOMETRY.U_FREQUENCY: 'GHz',
            PHOTOMETRY.FLUX_DENSITY:
            str(Decimal(str(row['flux'])) * Decimal('1.0e3')),
            PHOTOMETRY.E_FLUX_DENSITY:
            str(Decimal(str(row['unc'])) * Decimal('1.0e3')),
            PHOTOMETRY.U_FLUX_DENSITY: 'μJy',
            PHOTOMETRY.SOURCE: source
        }
        catalog.entries[name].add_photometry(**photodict)

    return
