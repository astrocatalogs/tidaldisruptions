"""Import tasks for the SIMBAD astrophysical database.
"""
import re

from astroquery.simbad import Simbad

from astrocats.catalog.utils import is_number, pbar, single_spaces, uniq_cdl
from astrocats.tidaldisruptions.tidaldisruption import TIDALDISRUPTION
from astrocats.tidaldisruptions.utils import name_clean


def do_simbad(catalog):
    # Simbad.list_votable_fields()
    # Some coordinates that SIMBAD claims belong to the SNe actually belong to
    # the host.
    task_str = catalog.get_current_task_str()
    simbadmirrors = ['http://simbad.harvard.edu/simbad/sim-script',
                     'http://simbad.u-strasbg.fr/simbad/sim-script']
    simbadbadcoordbib = ['2013ApJ...770..107C']
    simbadbadnamebib = ['2004AJ....127.2809W', '2005MNRAS.364.1419Z',
                        '2015A&A...574A.112D', '2011MNRAS.417..916G',
                        '2002ApJ...566..880G']
    simbadbannedcats = ['[TBV2008]', 'OGLE-MBR']
    customSimbad = Simbad()
    customSimbad.ROW_LIMIT = -1
    customSimbad.TIMEOUT = 120
    customSimbad.add_votable_fields('otype', 'sptype', 'sp_bibcode', 'id')
    table = []
    for mirror in simbadmirrors:
        customSimbad.SIMBAD_URL = mirror
        try:
            table = customSimbad.query_criteria('maintype="SN?"')
        except:
            continue
        else:
            break

    if not table:
        catalog.log.warning('SIMBAD unable to load, probably offline.')

    # 2000A&AS..143....9W
    for brow in pbar(table, task_str):
        row = {x: re.sub(r'b\'(.*)\'', r'\1', str(brow[x]))
               for x in brow.colnames}
        # Skip items with no bibliographic info aside from SIMBAD, too
        # error-prone
        if row['OTYPE'] == 'Candidate_SN*' and not row['SP_TYPE']:
            continue
        if not row['COO_BIBCODE']:
            continue
        if any([x in row['MAIN_ID'] for x in simbadbannedcats]):
            continue
        if row['COO_BIBCODE'] and row['COO_BIBCODE'] in simbadbadnamebib:
            continue
        name = single_spaces(re.sub(r'\[[^)]*\]', '', row['MAIN_ID']).strip())
        if name == 'SN':
            continue
        if is_number(name):
            continue

        name = name_clean(name)
        # SIMBAD doesn't have a TDE type, so we must skip most events
        if not catalog.entry_exists(name):
            continue

        name = catalog.add_entry(name)
        source = (catalog.entries[name].add_source(
            name='SIMBAD astronomical database',
            bibcode="2000A&AS..143....9W",
            url="http://simbad.u-strasbg.fr/",
            secondary=True))
        aliases = row['ID'].split(',')
        for alias in aliases:
            if any([x in alias for x in simbadbannedcats]):
                continue
            ali = single_spaces(re.sub(r'\[[^)]*\]', '', alias).strip())
            if is_number(ali):
                continue
            ali = name_clean(ali)
            catalog.entries[name].add_quantity(TIDALDISRUPTION.ALIAS, ali,
                                               source)
        if row['COO_BIBCODE'] and row['COO_BIBCODE'] not in simbadbadcoordbib:
            csources = ','.join([source, catalog.entries[name].add_source(
                bibcode=row['COO_BIBCODE'])])
            catalog.entries[name].add_quantity(TIDALDISRUPTION.RA, row['RA'],
                                               csources)
            catalog.entries[name].add_quantity(TIDALDISRUPTION.DEC, row['DEC'],
                                               csources)
    catalog.journal_entries()
    return
