#!/usr/bin/env python3

from pymongo import MongoClient
import candidate
import os
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'
import numpy as np
import h5py
import pprint
import glob

   
def add_cand(h5_file, db, label=None):
    with h5py.File(h5_file,'r') as cand_h5:
        cand_attrs = {}
        for key in cand_h5.attrs.keys():
            if isinstance(cand_h5.attrs[key],bytes):
                if cand_h5.attrs[key] == b'None':
                    cand_attrs[key] = None
                else:
                    cand_attrs[key] = cand_h5.attrs[key].decode()
            elif isinstance(cand_h5.attrs[key],np.int64):
                cand_attrs[key] = int(cand_h5.attrs[key])
            elif isinstance(cand_h5.attrs[key],np.float64):
                cand_attrs[key] = float(cand_h5.attrs[key])
            else:
                if key == 'cand_id':
                    cand_attrs['_id'] = cand_h5.attrs[key]                                                              
                else:
                    cand_attrs[key] = cand_h5.attrs[key]
        if label is not None:
            cand_attrs['label'] = int(label)
        cand_attrs['h5_loc'] = glob.glob(h5_file)[0] 
    
    a = db.gbtrans.insert_one(cand_attrs)
    return a.acknowledged, a.inserted_id


def get_cand(cand_id,db):
    return db.gbtrans.find_one({"_id":cand_id})

def update_cand(cand_id, db):
    #db.gbtrans.update_one({""})
    pass

def remove_cand(cand_id,db):
    db.gbtrans.delete_one({"_id":cand_id})
    return db

def get_spec_cand(db,dict):
    return db.gbtrans.find(dict)

def clear_database(db):
    db.gbtrans.delete_many({})


if __name__ == '__main__':
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    
    db = client.canDB
#    clear_database(db)
#    cand_h5 = h5py.File('/hyrule/data/users/dagarwal/spml/data/cand_tstart_57419.313315050000_tcand_12.8550000_dm_1402.04000_snr_10.58700.h5','r')
#    add_cand('/hyrule/data/users/dagarwal/spml/data/cand_tstart_57419.313315050000_tcand_12.8550000_dm_1402.04000_snr_10.58700.h5', db)
#    cand_id = 'cand_tstart_57419.313315050000_tcand_12.8550000_dm_1402.04000_snr_10.58700'
#    cand = get_cand(cand_id ,db)
##    pprint.pprint(cand)
