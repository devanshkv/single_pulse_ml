#!/usr/bin/env python3

import h5py
import sys
import pylab as plt
import os
import numpy as np
import glob
os.environ['HDF5_USE_FILE_LOCKING']='FALSE'

def plot_arg(h5_files,show=True):
    
    for h5_file in h5_files:
        with h5py.File(h5_file,'r') as f:
            for key in f.attrs.keys():
                print(key,f.attrs[key])
            dm_time=np.array(f['data_dm_time'])
            freq_time=np.array(f['data_freq_time'])
            print(f'dm time shape: {dm_time.shape}')
            print(f'freq time shape: {freq_time.shape}')
            fig, ax = plt.subplots(3,1,figsize=(4,6),sharex=True)
            fch1,foff,nchan,dm,cand_id,tsamp,dm_opt,snr,snr_opt=f.attrs['fch1'],\
                    f.attrs['foff'],f.attrs['nchans'],f.attrs['dm'],f.attrs['cand_id'],\
                    f.attrs['tsamp'],f.attrs['dm_opt'],f.attrs['snr'],f.attrs['snr_opt']
            print(f'DM:  {dm}')
            print(f'DM (opt): {dm_opt}')
            print(f'S/N:     {snr}')
            print(f'S/N (opt):   {snr_opt}')
            ts=np.arange(freq_time.shape[0])*tsamp
            ax[0].plot(ts,freq_time.mean(1),'k-')
            ax[0].set_ylabel('Flux (Arb. Units)')
            ax[1].imshow(freq_time.T, aspect='auto',extent=[ts[0],ts[-1],fch1,fch1 + (nchan*foff)],interpolation='none')
            ax[1].set_ylabel('Frequency (MHz)')
            ax[2].imshow(dm_time,aspect='auto',extent=[ts[0],ts[-1],3*dm,-dm],interpolation='none')
            ax[2].set_ylabel(r'DM (pc cm$^{-3}$)')
            plt.tight_layout()
            plt.xlabel('Time (s)')
            plt.savefig(cand_id+'.png',bbox_inches='tight')
            if show:
                plt.show()
            else:
                plt.close()

if __name__ == '__main__':
    plot_arg(glob.glob(sys.argv[1]))
