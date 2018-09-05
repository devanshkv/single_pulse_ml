#!/usr/bin/env python3

import h5py
import sys
import pylab as plt
import os
import numpy as np
import glob
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'

h5_files=glob.glob(sys.argv[1])

for h5_file in h5_files:
    with h5py.File(h5_file,'r') as f:
        dm_time=np.array(f['data_dm_time'])
        freq_time=np.array(f['data_freq_time'])
        fig, ax = plt.subplots(3,1,figsize=(4,6),sharex=True)
        fch1,foff,nchan,dm,cand_id,tsamp=f.attrs['fch1'],f.attrs['foff'],f.attrs['nchans'],f.attrs['dm'],f.attrs['cand_id'],f.attrs['tsamp']
        ts=np.arange(freq_time.shape[0])*tsamp
        ax[0].plot(ts,freq_time.mean(1),'k-')
        ax[0].set_ylabel('Flux (Arb. Units)')
        ax[1].imshow(freq_time.T, aspect='auto',extent=[ts[0],ts[-1],fch1,fch1 + (nchan*foff)],interpolation='none')
        ax[1].set_ylabel('Frequency (MHz)')
        ax[2].imshow(dm_time,aspect='auto',extent=[ts[0],ts[-1],-dm,3*dm],interpolation='none')
        ax[2].set_ylabel(r'DM (pc cm$^{-3}$)')
        plt.tight_layout()
        plt.xlabel('Time (s)')
        plt.savefig(cand_id+'.png',bbox_inches='tight')
        plt.show()
