#!/usr/bin/env python3

from candidate import Candidate
import pandas as pd
import pylab as plt
import os
import sys
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'
from pymongo import MongoClient
from mongo_utils import add_cand

data=pd.read_csv('../gbtrans/scripts/rfi_all_cands',names=['fil_file','snr','stime','dm','width'])
data=data[data['dm']>50]

client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.canDB

print(db)

for index, row in data.iterrows():
    print(index)
    cand = Candidate(row['fil_file'],snr=row['snr'],width=2**row['width'],dm=row['dm'],label=0,tcand=row['stime'])
    for val in row['fil_file'].split('/'):
        if 'out' in val:
            mjd_split=val.split('_')
            mjd=float(mjd_split[1]+'.'+mjd_split[2])
            cand.tstart=mjd
    data = cand.get_chunk().data
    cand.dedisperse()
    cand.dmtime()
    cand.optimize_dm()
    cand.label=0
    fout=cand.save_h5(out_dir='/hyrule/data/users/dagarwal/spml/data/')
    print(add_cand(fout,db))
    sys.exit(1)
    #plt.subplot(211)
    #plt.imshow(cand.dmt,aspect='auto')
    #plt.title(f'DM_opt: {cand.dm_opt} SNR_opt: {cand.snr_opt}')
    #plt.subplot(212)
    #plt.imshow(cand.dedispersed.T,aspect='auto')
    #plt.title(f'DM:{cand.dm} SNR: {cand.snr}')
    #plt.tight_layout()
    #plt.savefig(f"{cand.dm}_{cand.snr}_{cand.tcand}.png",bbox_inches='tight')
