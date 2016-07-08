"""Import tasks for data directly donated to the Open Supernova Catalog.
"""
import csv
import json
import os
from glob import glob
from math import isnan

from astrocats.catalog.utils import is_number, pbar, pbar_strings, rep_chars


def do_donations(catalog):
    task_str = catalog.get_current_task_str()

    catalog.journal_entries()
    return
