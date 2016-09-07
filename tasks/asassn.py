"""Tasks related to the ASASSN survey.
"""
import os

from bs4 import BeautifulSoup

from astrocats.catalog.utils import pbar
from astrocats.tidaldisruptions.tidaldisruption import TIDALDISRUPTION


def do_asassn(catalog):
    task_str = catalog.get_current_task_str()
    asn_url = 'http://www.astronomy.ohio-state.edu/~assassin/transients.html'
    html = catalog.load_cached_url(asn_url, os.path.join(
        catalog.get_current_task_repo(), 'ASASSN/transients.html'))
    if not html:
        return
    bs = BeautifulSoup(html, 'html5lib')
    trs = bs.find('table').findAll('tr')
    for tri, tr in enumerate(pbar(trs, task_str)):
        name = ''
        alias = ''
        ra = ''
        dec = ''
        redshift = ''
        hostoff = ''
        claimedtype = ''
        host = ''
        atellink = ''
        if tri <= 1:
            continue
        tds = tr.findAll('td')
        for tdi, td in enumerate(tds):
            if tdi == 0:
                name = td.text.strip()
            if tdi == 1:
                alias = td.text.strip()
            if tdi == 2:
                atellink = td.find('a')
                if atellink and td.text == 'ATEL':
                    atellink = atellink['href']
                else:
                    atellink = ''
            if tdi == 3:
                ra = td.text
                rasplit = ra.split(':')
                rasecs = rasplit[2].split('.')
                ra = ':'.join([rasplit[0], rasplit[1].zfill(2),
                               rasecs[0].zfill(2) + (
                                   ('.' + rasecs[1])
                                   if len(rasecs) > 1 else '')])
            if tdi == 4:
                dec = td.text
                decsplit = dec.split(':')
                decsecs = decsplit[2].split('.')
                dec = ':'.join([decsplit[0], decsplit[1].zfill(2),
                                decsecs[0].zfill(2) + (
                                    ('.' + decsecs[1])
                                    if len(decsecs) > 1 else '')])
            if tdi == 5:
                discdate = td.text.replace('-', '/')
            if tdi == 11:
                tdt = td.text
                if 'TDE' in tdt:
                    claimedtype = 'TDE'
                if 'z=' in tdt:
                    redshift = (tdt[tdt.find('z=') + 2:]
                                .split(',')[0].split(';')[0].strip())

        if claimedtype != 'TDE' and name not in catalog.entries:
            continue

        name = catalog.add_entry(name)

        sources = [catalog.entries[name].add_source(
            url=asn_url, name='ASAS-SN Supernovae')]
        typesources = sources[:]
        if atellink:
            sources.append((catalog.entries[name].add_source(
                name='ATel ' + atellink.split('=')[-1], url=atellink)))
        sources = ','.join(sources)
        typesources = ','.join(typesources)
        catalog.entries[name].add_quantity(TIDALDISRUPTION.ALIAS, name,
                                           sources)
        if alias != '---':
            catalog.entries[name].add_quantity(TIDALDISRUPTION.ALIAS, alias,
                                               sources)
        catalog.entries[name].add_quantity(TIDALDISRUPTION.DISCOVER_DATE,
                                           discdate, sources)
        catalog.entries[name].add_quantity(
            TIDALDISRUPTION.RA, ra, sources, u_value='floatdegrees')
        catalog.entries[name].add_quantity(
            TIDALDISRUPTION.DEC, dec, sources, u_value='floatdegrees')
        catalog.entries[name].add_quantity(TIDALDISRUPTION.REDSHIFT, redshift,
                                           sources)
        catalog.entries[name].add_quantity(
            TIDALDISRUPTION.HOST_OFFSET_ANG,
            hostoff,
            sources,
            u_value='arcseconds')
        for ct in claimedtype.split('/'):
            if ct != 'Unk':
                catalog.entries[name].add_quantity(
                    TIDALDISRUPTION.CLAIMED_TYPE, ct, typesources)
        if host != 'Uncatalogued':
            catalog.entries[name].add_quantity(TIDALDISRUPTION.HOST, host,
                                               sources)

    catalog.journal_entries()
    return
