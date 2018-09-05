#!/usr/bin/env python3

import h5py
import os
import sys
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'
import logging

logger = logging.getLogger()
logger=logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')

h5_file=sys.argv[1]
attribute = sys.argv[2]
value = sys.argv[3]

with h5py.File(h5_file,'r+') as f:
    f.attrs[attribute] = value
    logger.info(f"{f.attrs['cand_id']}: {attribute} changed to {value}")    



