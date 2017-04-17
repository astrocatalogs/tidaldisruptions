"""Import tasks for data directly donated to the Open TDE Catalog.
"""
import csv
import json
import os
from math import floor, isnan

from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.spectrum import SPECTRUM
from astrocats.catalog.utils import get_sig_digits, pbar, pretty_num
from astrocats.tidaldisruptions.tidaldisruption import TIDALDISRUPTION
from astropy.io.ascii import read
from astropy.time import Time as astrotime

from decimal import Decimal


def do_donated_photo(catalog):
    task_str = catalog.get_current_task_str()

    datafile = os.path.join(catalog.get_current_task_repo(), 'Donations',
                            'Auchettl-2016.csv')

    with open(datafile, 'r') as f:
        tsvin = csv.reader(f, delimiter=',', skipinitialspace=True)

        for ri, row in enumerate(pbar(list(tsvin), task_str)):
            if ri <= 3 or not row or not row[0]:
                continue
            (name, source) = catalog.new_entry(
                row[0], bibcode='2017ApJ...838..149A')
            smjd = Decimal(row[3])
            emjd = str(smjd + Decimal(row[4]) / Decimal(86400))[:9]
            mjd = [str(smjd), str(emjd)]
            instrument = ''
            tel = ''
            if row[-1] == 'chandra':
                instrument = 'ACIS-S'
                tel = 'Chandra'
            elif row[-1] == 'xmm' or row[-1] == 'slew':
                instrument = 'PN'
                tel = 'XMM'
            elif row[-1] == 'swift':
                instrument = 'XRT'
                mode = 'PC'
                tel = 'Swift'
            elif row[-1] == 'rosat':
                instrument = 'PSPC'
                tel = 'ROSAT'
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
                PHOTOMETRY.INSTRUMENT: instrument,
                PHOTOMETRY.TELESCOPE: tel,
                PHOTOMETRY.MODE: mode,
                PHOTOMETRY.SOURCE: source
            }
            if row[11] == 'D' and row[21] != row[22]:
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
                row[0].strip(), bibcode='2017ApJ...838..149A')
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
            PHOTOMETRY.FREQUENCY:
            str(Decimal(row['freq']) / Decimal('1.0e9')),
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


def do_donated_spectra(catalog):
    task_str = catalog.get_current_task_str()
    fpath = os.path.join(catalog.get_current_task_repo(), 'donations')
    with open(os.path.join(fpath, 'meta.json'), 'r') as f:
        metadict = json.loads(f.read())

    donationscnt = 0
    oldname = ''
    for fname in pbar(metadict, task_str):
        name = metadict[fname]['name']
        name = catalog.get_preferred_name(name)
        if oldname and name != oldname:
            catalog.journal_entries()
        oldname = name
        sec_bibc = metadict[fname]['bibcode']
        name, source = catalog.new_entry(name, bibcode=sec_bibc)

        date = metadict[fname].get('date', '')
        year, month, day = date.split('/')
        sig = get_sig_digits(day) + 5
        day_fmt = str(floor(float(day))).zfill(2)
        time = astrotime(year + '-' + month + '-' + day_fmt).mjd
        time = time + float(day) - floor(float(day))
        time = pretty_num(time, sig=sig)

        with open(os.path.join(fpath, fname), 'r') as f:
            specdata = list(
                csv.reader(
                    f, delimiter=' ', skipinitialspace=True))
            specdata = list(filter(None, specdata))
            newspec = []
            oldval = ''
            for row in specdata:
                if row[0][0] == '#':
                    continue
                if row[1] == oldval:
                    continue
                newspec.append(row)
                oldval = row[1]
            specdata = newspec
        haserrors = len(specdata[0]) == 3 and specdata[0][2] and specdata[0][
            2] != 'NaN'
        specdata = [list(i) for i in zip(*specdata)]

        wavelengths = specdata[0]
        fluxes = specdata[1]
        errors = ''
        if haserrors:
            errors = specdata[2]

        specdict = {
            SPECTRUM.U_WAVELENGTHS: 'Angstrom',
            SPECTRUM.U_TIME: 'MJD',
            SPECTRUM.TIME: time,
            SPECTRUM.WAVELENGTHS: wavelengths,
            SPECTRUM.FLUXES: fluxes,
            SPECTRUM.ERRORS: errors,
            SPECTRUM.SOURCE: source,
            SPECTRUM.FILENAME: fname
        }
        if 'instrument' in metadict[fname]:
            specdict[SPECTRUM.INSTRUMENT] = metadict[fname]['instrument']
        if 'telescope' in metadict[fname]:
            specdict[SPECTRUM.TELESCOPE] = metadict[fname]['telescope']
        if 'yunit' in metadict[fname]:
            specdict[SPECTRUM.U_FLUXES] = metadict[fname]['yunit']
            specdict[SPECTRUM.U_ERRORS] = metadict[fname]['yunit']
        else:
            if max([float(x) for x in fluxes]) < 1.0e-5:
                fluxunit = 'erg/s/cm^2/Angstrom'
            else:
                fluxunit = 'Uncalibrated'
            specdict[SPECTRUM.U_FLUXES] = fluxunit
            specdict[SPECTRUM.U_ERRORS] = fluxunit
        catalog.entries[name].add_spectrum(**specdict)
        donationscnt = donationscnt + 1
        if (catalog.args.travis and
                donationscnt % catalog.TRAVIS_QUERY_LIMIT == 0):
            break

    catalog.journal_entries()
    return
