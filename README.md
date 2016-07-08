# Open Tidal Disruption Event Catalog #

[![Build Status](https://img.shields.io/travis/astrocatalogs/tidaldisruptions.svg)](https://travis-ci.org/astrocatalogs/tidaldisruptions)
[![Python Version](https://img.shields.io/badge/python-3.3%2C%203.4%2C%203.5-blue.svg)](https://www.python.org)

This is the primary repository for the Open Tidal Disruption Event Catalog (OTC) which contains a Python script ([import.py](https://github.com/astrocatalogs/sne/blob/master/scripts/import.py)) that generates the event JSON files and additional scripts that process those files. This repository also contains the primary JSON catalog file generated by the [make-catalog.py](https://github.com/astrocatalogs/sne/blob/master/scripts/make-catalog.py) script, which is used to drive the web-based table available on [sne.space](https://sne.space). Because GitHub repositories are limited to 1GB each, individual event JSON files are stored in separate repositories that are collated by year; these repositories contain the entirety of the data collected by the OTC:

https://github.com/astrocatalogs/tde-1980-2025 – All discovered tidal disruptions.

## Contributing Data ##

To contribute data to the repository, please read our [contribution guide](https://sne.space/contribute/).

## Format of Data Files ##

The data files are in [JSON format](http://www.json.org/), a detailed description of the particular structure we have chosen is available [here](https://github.com/astrocatalogs/supernovae/blob/master/SCHEMA.md).

## Installing and Running OSC Import Script ##

If you are interested in reproducing the catalog on your own machine, installation can be done by following the `install:` subsection in the [.travis.yml](https://github.com/astrocatalogs/sne/blob/master/.travis.yml) file, which installs all required modules via pip and clones all required input repositories. The OSC software is run in Python 3.5 and is not tested for compatability with Python 2. 

After installing, navigate to the [scripts](https://github.com/astrocatalogs/sne/blob/master/scripts) folder and execute the import script,

```shell
cd scripts
./import.py
```

and the import process will begin. The first time you run the import may take over a day as the caches of many sources will need to be built from scratch (particularly the host images); typical run time for the import is a few hours, and in update mode (`./import.py -u`), typical runtime is less than an hour. Runtime can be reduced significantly by commenting out tasks in the task array near the top of the `import.py` file; the slowest import steps tend to be spectra imports so if you're just interested in testing you may want to comment these tasks out first.

## Using the Collected OSC Data ##

There are several scripts in the [scripts](https://github.com/astrocatalogs/sne/blob/master/scripts) folder that use the produced datafiles to generate various data products, print out metrics, etc. The first command you should probably run is [repo-status.sh](https://github.com/astrocatalogs/sne/blob/master/scripts/repo-status.sh), which will highlight changes in the output JSON files relative to the last pushed changes to these files. If the import ran successfully, these changes should be minimal and only consist of the most recent supernovae. Changes to the output repositories can be reverted by running the [reset-repos.sh](https://github.com/astrocatalogs/sne/blob/master/scripts/reset-repos.sh) script. Don't be afraid to play around with the data!
