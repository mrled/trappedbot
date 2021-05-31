#!/usr/bin/env python3

# Show the version of the trappedbot package.
# Useful for e.g. build scripts.

import configparser
import os


scriptdir = os.path.dirname(os.path.realpath(__file__))
setupcfg = os.path.join(scriptdir, "setup.cfg")
config = configparser.ConfigParser()
config.read_file(open(setupcfg))
print(config.get("metadata", "version"))
