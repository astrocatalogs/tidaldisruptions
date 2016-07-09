"""Tasks related to the ASASSN survey.
"""
import os

from astrocats.catalog.utils import pbar
from bs4 import BeautifulSoup


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
            if tdi == 4:
                dec = td.text
            if tdi == 5:
                discdate = td.text.replace('-', '/')
            if tdi == 11:
                tdt = td.text
                if 'TDE' in tdt:
                    claimedtype = 'TDE'
                if 'z=' in tdt:
                    redshift = (tdt[tdt.find('z=')+2:]
                                .split(',')[0].split(';')[0].strip())

        if claimedtype != 'TDE' and name not in catalog.entries:
            continue

        name = catalog.add_entry(name)

        sources = [catalog.entries[name].add_source(
            url=asn_url, name='ASAS-SN Supernovae')]
        typesources = sources[:]
        if atellink:
            sources.append(
                (catalog.entries[name]
                 .add_source(name='ATel ' +
                             atellink.split('=')[-1], url=atellink)))
        sources = ','.join(sources)
        typesources = ','.join(typesources)
        catalog.entries[name].add_quantity('alias', name, sources)
        if alias != '---':
            catalog.entries[name].add_quantity('alias', alias, sources)
        catalog.entries[name].add_quantity('discoverdate', discdate, sources)
        catalog.entries[name].add_quantity('ra', ra, sources,
                                           unit='floatdegrees')
        catalog.entries[name].add_quantity('dec', dec, sources,
                                           unit='floatdegrees')
        catalog.entries[name].add_quantity('redshift', redshift, sources)
        catalog.entries[name].add_quantity(
            'hostoffsetang', hostoff, sources, unit='arcseconds')
        for ct in claimedtype.split('/'):
            if ct != 'Unk':
                catalog.entries[name].add_quantity('claimedtype', ct,
                                                   typesources)
        if host != 'Uncatalogued':
            catalog.entries[name].add_quantity('host', host, sources)

    catalog.journal_entries()
    return
