# -*- coding: utf-8 -*-
"""Imports for the WISeREP spectroscopic repository.
"""
import json
import os
import warnings
from glob import glob
from html import unescape

from astropy.time import Time as astrotime

from astrocats.catalog.source import SOURCE
from astrocats.catalog.utils import is_number, pbar, pbar_strings, uniq_cdl

from ..tidaldisruption import TIDALDISRUPTION


def do_wiserep_spectra(catalog):
    if (not catalog.args.travis and not catalog.args.archived):
        from ..input.WISeWEBSpider.wisewebspider import spider
        spider(
            update=True,
            daysago=7,
            include_type=["TDE"],
            path="/../../tde-external-WISEREP/")

    task_str = catalog.get_current_task_str()
    secondaryreference = 'WISeREP'
    secondaryrefurl = 'http://wiserep.weizmann.ac.il/'
    secondarybibcode = '2012PASP..124..668Y'
    wiserepcnt = 0

    # These are known to be in error on the WISeREP page, either fix or ignore
    # them.
    wiserepbibcorrectdict = {'2000AJ....120..367G]': '2000AJ....120..367G',
                             'Harutyunyan et al. 2008': '2008A&A...488..383H',
                             '0609268': '2007AJ....133...58K',
                             '2006ApJ...636...400Q': '2006ApJ...636..400Q',
                             '2011ApJ...741...76': '2011ApJ...741...76C',
                             '2016PASP...128...961': '2016PASP..128...961',
                             '2002AJ....1124..417H': '2002AJ....1124.417H',
                             '2013ApJ…774…58D': '2013ApJ...774...58D',
                             '2011Sci.333..856S': '2011Sci...333..856S',
                             '2014MNRAS.438,368': '2014MNRAS.438..368T',
                             '2012MNRAS.420.1135': '2012MNRAS.420.1135S',
                             '2012Sci..337..942D': '2012Sci...337..942D',
                             'stt1839': '2013MNRAS.436.3614S',
                             'arXiv:1605.03136': '2016arXiv160503136T',
                             '10.1093/mnras/stt1839': '2013MNRAS.436.3614S'}

    file_names = list(glob(os.path.join(catalog.get_current_task_repo(), '*')))
    for folder in pbar_strings(file_names, task_str):
        if '.txt' in folder or '.json' in folder:
            continue
        name = os.path.basename(folder).strip()
        if name.startswith('sn'):
            name = 'SN' + name[2:]
        if (name.startswith(('CSS', 'SSS', 'MLS')) and ':' not in name):
            name = name.replace('-', ':', 1)
        if name.startswith('MASTERJ'):
            name = name.replace('MASTERJ', 'MASTER OT J')
        if name.startswith('PSNJ'):
            name = name.replace('PSNJ', 'PSN J')
        name = catalog.add_entry(name)

        secondarysource = catalog.entries[name].add_source(
            name=secondaryreference,
            url=secondaryrefurl,
            bibcode=secondarybibcode,
            secondary=True)
        catalog.entries[name].add_quantity(TIDALDISRUPTION.ALIAS, name,
                                           secondarysource)

        with open(os.path.join(folder, 'README.json'), 'r') as f:
            fileinfo = json.loads(f.read())

        files = list(
            set(glob(folder + '/*')) - set(glob(folder + '/README.json')))
        for fname in pbar(files, task_str):
            specfile = os.path.basename(fname)
            if specfile not in fileinfo:
                catalog.log.warning('Metadata not found for "{}"'.format(
                    fname))
                continue
            claimedtype = fileinfo[specfile]["Type"]
            instrument = fileinfo[specfile]["Instrument"]
            epoch = fileinfo[specfile]["Obs. Date"]
            observer = fileinfo[specfile]["Observer"]
            reducer = fileinfo[specfile]["Reducer"]
            bibcode = fileinfo[specfile]["Bibcode"]
            redshift = fileinfo[specfile]["Redshift"]
            survey = fileinfo[specfile]["Program"]
            reduction = fileinfo[specfile]["Reduction Status"]

            if bibcode:
                newbibcode = bibcode
                if bibcode in wiserepbibcorrectdict:
                    newbibcode = wiserepbibcorrectdict[bibcode]
                if newbibcode and len(newbibcode) == 19:
                    source = catalog.entries[name].add_source(
                        bibcode=unescape(newbibcode))
                else:
                    bibname = unescape(bibcode)
                    source = catalog.entries[name].add_source(name=bibname)
                    catalog.log.warning('Bibcode "{}" is invalid, using as '
                                        '`{}` instead'.format(bibname,
                                                              SOURCE.NAME))
                sources = uniq_cdl([source, secondarysource])
            else:
                sources = secondarysource

            if claimedtype not in ['Other']:
                catalog.entries[name].add_quantity(
                    TIDALDISRUPTION.CLAIMED_TYPE, claimedtype, secondarysource)
            catalog.entries[name].add_quantity(TIDALDISRUPTION.REDSHIFT,
                                               redshift, secondarysource)

            with open(fname, 'r') as f:
                data = [x.split() for x in f]

                skipspec = False
                newdata = []
                oldval = ''
                for row in data:
                    if row and '#' not in row[0]:
                        if (len(row) >= 2 and is_number(row[0]) and
                                is_number(row[1]) and row[1] != oldval):
                            newdata.append(row)
                            oldval = row[1]

                if skipspec or not newdata:
                    warnings.warn('Skipped adding spectrum file ' + specfile)
                    continue

                data = [list(i) for i in zip(*newdata)]
                wavelengths = data[0]
                fluxes = data[1]
                errors = ''
                if len(data) == 3:
                    errors = data[1]
                time = str(astrotime(epoch).mjd)

                if max([float(x) for x in fluxes]) < 1.0e-5:
                    fluxunit = 'erg/s/cm^2/Angstrom'
                else:
                    fluxunit = 'Uncalibrated'

                catalog.entries[name].add_spectrum(
                    u_wavelengths='Angstrom',
                    errors=errors,
                    u_fluxes=fluxunit,
                    u_errors=fluxunit if errors else '',
                    wavelengths=wavelengths,
                    fluxes=fluxes,
                    u_time='MJD',
                    time=time,
                    instrument=instrument,
                    source=sources,
                    observer=observer,
                    reducer=reducer,
                    reduction=reduction,
                    filename=specfile,
                    survey=survey,
                    redshift=redshift)

        catalog.journal_entries()

        wiserepcnt = wiserepcnt + 1
        if (catalog.args.travis and
                wiserepcnt % catalog.TRAVIS_QUERY_LIMIT == 0):
            break

    return
