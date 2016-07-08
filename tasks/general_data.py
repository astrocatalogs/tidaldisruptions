# -*- coding: utf-8 -*-
"""General data import tasks.
"""
import os
from collections import OrderedDict
from glob import glob

from astrocats.catalog.utils import pbar_strings
from astrocats.tidaldisruptions.tidaldisruption import KEYS, TidalDisruption


def do_external(catalog):
    raise(SystemExit('Need to rewrite for TDEs'))
    task_str = catalog.get_current_task_str()
    path_pattern = os.path.join(catalog.get_current_task_repo(), '*.txt')
    for datafile in pbar_strings(glob(path_pattern), task_str):
        oldname = os.path.basename(datafile).split('.')[0]
        name = catalog.add_entry(oldname)
        radiosourcedict = OrderedDict()
        with open(datafile, 'r') as ff:
            for li, line in enumerate([xx.strip() for xx in
                                       ff.read().splitlines()]):
                if line.startswith('(') and li <= len(radiosourcedict):
                    key = line.split()[0]
                    bibc = line.split()[-1]
                    radiosourcedict[key] = catalog.entries[
                        name].add_source(bibcode=bibc)
                elif li in [xx + len(radiosourcedict) for xx in range(3)]:
                    continue
                else:
                    cols = list(filter(None, line.split()))
                    source = radiosourcedict[cols[6]]
                    catalog.entries[name].add_photometry(
                        time=cols[0], frequency=cols[2], u_frequency='GHz',
                        fluxdensity=cols[3], e_fluxdensity=cols[4],
                        u_fluxdensity='µJy',
                        instrument=cols[5], source=source)
                    catalog.entries[name].add_quantity(
                        'alias', oldname, source)

    catalog.journal_entries()
    return


def do_internal(catalog):
    """Load events from files in the 'internal' repository, and save them.
    """
    task_str = catalog.get_current_task_str()
    path_pattern = os.path.join(catalog.get_current_task_repo(), '*.json')
    files = glob(path_pattern)
    catalog.log.debug("found {} files matching '{}'".format(
        len(files), path_pattern))
    for datafile in pbar_strings(files, task_str):
        new_event = Supernova.init_from_file(
            catalog, path=datafile, clean=True)
        catalog.entries.update({new_event[KEYS.NAME]: new_event})

    return
