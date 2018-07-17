"""Import tasks for Pan-STARRS.
"""
import csv
import json
import os
import urllib
import warnings
from glob import glob

import requests
from astrocats.catalog.photometry import PHOTOMETRY
from astrocats.catalog.utils import is_number, make_date_string, pbar, uniq_cdl
from astropy.time import Time as astrotime
from bs4 import BeautifulSoup

from ..tidaldisruption import TIDALDISRUPTION


def do_ps_threepi(catalog):
    """Import data from Pan-STARRS' 3pi page."""
    task_str = catalog.get_current_task_str()
    bad_aliases = ['SN1994J']
    teles = 'Pan-STARRS1'
    fname = os.path.join(catalog.get_current_task_repo(), '3pi/page00.html')
    ps_url = ("https://star.pst.qub.ac.uk/"
              "ps1threepi/psdb/public/?page=1&sort=followup_flag_date")
    html = catalog.load_url(ps_url, fname, write=False, update_mode=True)

    # Check if offline.
    offline = False
    if not html:
        offline = True
    else:
        # Clean some common HTML manglings
        html = html.replace('ahref=', 'a href=')

        bs = BeautifulSoup(html, 'html5lib')
        div = bs.find('div', {'class': 'pagination'})
        if not div:
            offline = True
        else:
            links = div.findAll('a')
            if not links:
                offline = True

    if offline:
        if catalog.args.update:
            return
        warnings.warn('Pan-STARRS 3pi offline, using local files only.')
        with open(fname, 'r') as f:
            html = f.read()
        bs = BeautifulSoup(html, 'html5lib')
        div = bs.find('div', {'class': 'pagination'})
        links = div.findAll('a')
    else:
        with open(fname, 'w') as f:
            f.write(html)

    numpages = int(links[-2].contents[0]) + 1
    oldnumpages = len(
        glob(os.path.join(catalog.get_current_task_repo(), '3pi/page*')))
    for page in pbar(range(1, numpages), task_str):
        fname = os.path.join(catalog.get_current_task_repo(), '3pi/page') + \
            str(page).zfill(2) + '.html'
        if offline:
            if not os.path.isfile(fname):
                continue
            with open(fname, 'r') as f:
                html = f.read()
        else:
            if (catalog.current_task.load_archive(catalog.args) and
                    page < oldnumpages and os.path.isfile(fname)):
                with open(fname, 'r') as f:
                    html = f.read()
            else:
                response = urllib.request.urlopen(
                    "https://star.pst.qub.ac.uk/ps1threepi/psdb/public/?page=" +
                    str(page) + "&sort=followup_flag_date")
                with open(fname, 'w') as f:
                    html = response.read().decode('utf-8')
                    f.write(html)

        bs = BeautifulSoup(html, 'html5lib')
        trs = bs.findAll('tr')
        for tr in pbar(trs, task_str):
            tds = tr.findAll('td')
            if not tds:
                continue
            refs = []
            aliases = []
            ttype = ''
            ctype = ''
            for tdi, td in enumerate(tds):
                if tdi == 0:
                    psname = td.contents[0]
                    pslink = psname['href']
                    psname = psname.text
                elif tdi == 1:
                    ra = td.contents[0]
                elif tdi == 2:
                    dec = td.contents[0]
                elif tdi == 3:
                    ttype = td.contents[0]
                elif tdi == 6:
                    if not td.contents:
                        continue
                    ctype = td.contents[0]
                    if ctype == 'Observed':
                        ctype = ''
                elif tdi == 17:
                    if td.contents:
                        crossrefs = td.findAll('a')
                        for cref in crossrefs:
                            if 'atel' in cref.contents[0].lower():
                                refs.append([cref.contents[0], cref['href']])
                            elif is_number(cref.contents[0][:4]):
                                continue
                            else:
                                aliases.append(cref.contents[0])

            name = ''
            for alias in aliases:
                if alias in bad_aliases:
                    continue
                if alias[:2] == 'AT':
                    name = alias
            if not name:
                name = psname

            if not any([catalog.entry_exists(x) for x in (aliases + [psname])]):
                continue

            name = catalog.add_entry(name)
            sources = [
                catalog.entries[name].add_source(
                    name='Pan-STARRS 3Pi',
                    url=('https://star.pst.qub.ac.uk/'
                         'ps1threepi/psdb/'))
            ]
            catalog.entries[name].add_quantity(TIDALDISRUPTION.ALIAS, name,
                                               sources[0])
            for ref in refs:
                sources.append(catalog.entries[name].add_source(
                    name=ref[0], url=ref[1]))
            source = uniq_cdl(sources)
            for alias in aliases:
                newalias = alias
                if alias[:3] in ['CSS', 'SSS', 'MLS']:
                    newalias = alias.replace('-', ':', 1)
                newalias = newalias.replace('PSNJ', 'PSN J')
                catalog.entries[name].add_quantity(TIDALDISRUPTION.ALIAS, newalias,
                                                   source)
            catalog.entries[name].add_quantity(TIDALDISRUPTION.RA, ra, source)
            catalog.entries[name].add_quantity(TIDALDISRUPTION.DEC, dec, source)
            catalog.entries[name].add_quantity(TIDALDISRUPTION.CLAIMED_TYPE, ctype,
                                               source)

            fname2 = os.path.join(catalog.get_current_task_repo(),
                                  '3pi/candidate-')
            fname2 += pslink.rstrip('/').split('/')[-1] + '.html'
            if offline:
                if not os.path.isfile(fname2):
                    continue
                with open(fname2, 'r') as f:
                    html2 = f.read()
            else:
                if (catalog.current_task.load_archive(catalog.args) and
                        os.path.isfile(fname2)):
                    with open(fname2, 'r') as f:
                        html2 = f.read()
                else:
                    pslink = ('https://star.pst.qub.ac.uk/'
                              'ps1threepi/psdb/public/') + pslink
                    try:
                        session2 = requests.Session()
                        response2 = session2.get(pslink)
                    except Exception:
                        offline = True
                        if not os.path.isfile(fname2):
                            continue
                        with open(fname2, 'r') as f:
                            html2 = f.read()
                    else:
                        html2 = response2.text
                        with open(fname2, 'w') as f:
                            f.write(html2)

            bs2 = BeautifulSoup(html2, 'html5lib')
            scripts = bs2.findAll('script')
            nslines = []
            nslabels = []
            for script in scripts:
                if 'jslcdata.push' not in script.text:
                    continue
                slines = script.text.splitlines()
                for line in slines:
                    if 'jslcdata.push' in line:
                        json_fname = (line.strip()
                                      .replace('jslcdata.push(', '')
                                      .replace(');', ''))
                        nslines.append(json.loads(json_fname))
                    if ('jslabels.push' in line and 'blanks' not in line and
                            'non det' not in line):
                        json_fname = (line.strip()
                                      .replace('jslabels.push(', '')
                                      .replace(');', ''))
                        nslabels.append(json.loads(json_fname)['label'])
            for li, line in enumerate(nslines[:len(nslabels)]):
                if not line:
                    continue
                for obs in line:
                    catalog.entries[name].add_photometry(
                        time=str(obs[0]),
                        u_time='MJD',
                        band=nslabels[li],
                        instrument='GPC',
                        magnitude=str(obs[1]),
                        e_magnitude=str(obs[2]),
                        source=source,
                        telescope=teles)
            # Ignoring upper limits as they are usually spurious chip gaps.
            # for li, line in enumerate(nslines[2 * len(nslabels):]):
            #     if not line:
            #         continue
            #     for obs in line:
            #         catalog.entries[name].add_photometry(
            #             time=str(obs[0]),
            #             u_time='MJD',
            #             band=nslabels[li],
            #             instrument='GPC',
            #             magnitude=str(obs[1]),
            #             upperlimit=True,
            #             source=source,
            #             telescope=teles)
            assoctab = bs2.find('table', {'class': 'generictable'})
            hostname = ''
            redshift = ''
            if assoctab:
                trs = assoctab.findAll('tr')
                headertds = [x.contents[0] for x in trs[1].findAll('td')]
                tds = trs[1].findAll('td')
                for tdi, td in enumerate(tds):
                    if tdi == 1:
                        hostname = td.contents[0].strip()
                    elif tdi == 4:
                        if 'z' in headertds:
                            redshift = td.contents[0].strip()
            # Skip galaxies with just SDSS id
            if is_number(hostname):
                continue
            catalog.entries[name].add_quantity(TIDALDISRUPTION.HOST, hostname,
                                               source)
            if redshift:
                catalog.entries[name].add_quantity(
                    [TIDALDISRUPTION.REDSHIFT, TIDALDISRUPTION.HOST_REDSHIFT],
                    redshift,
                    source,
                    kind='host')
            if catalog.args.update:
                catalog.journal_entries()

        catalog.journal_entries()
        # Only run first page for Travis
        if catalog.args.travis:
            break

    return
