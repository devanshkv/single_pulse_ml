# Liam Connor 25 July 2018
# Script to classify single-pulses 
# using tensorflow/keras model. Output probabilities 
# can be saved and plotted

import optparse
import numpy as np
import h5py

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import matplotlib as mpl
mpl.use('pdf')

import frbkeras
import reader
import plot_tools

def classify(data, model, save_ranked=False, 
             plot_ranked=False, prob_threshold=0.5,
             fnout='ranked', nside=8, params=None,
             ranked_ind=None, yaxlabel='Freq'):

    model = frbkeras.load_model(model)

    mshape = model.input.shape
    dshape = data.shape

    # normalize data
    data = data.reshape(len(data), -1)
    data -= np.median(data, axis=-1)[:, None]
    data /= np.std(data, axis=-1)[:, None]

    # zero out nans
    data[data!=data] = 0.0
    data = data.reshape(dshape)

    if dshape[-1]!=1:
        data = data[..., None]

    if len(mshape)==3:
        data = data.mean(1)
        dshape = data.shape

    if mshape[1]<dshape[1]:
        print('Mismatch axis 1')
        nm = int(mshape[1])
        nd = dshape[1]
        data = data[:, nd//2-nm//2:nd//2+nm//2]
    elif mshape[1]>dshape[1]:
        print("Model expects:", mshape)
        print("Data has:", dshape) 

        return 

    if mshape[2]<dshape[2]:
        print('Mismatch axis 2')
        nm = int(mshape[2])
        nd = dshape[2]
        data = data[:, :, nd//2-nm//2:nd//2+nm//2]
    elif mshape[2]>dshape[2]:
        print("Model expects:", mshape)
        print("Data has:", dshape) 

        return 

    y_pred_prob = model.predict(data)
    y_pred_prob = y_pred_prob[:,1]

    ind_frb = np.where(y_pred_prob>prob_threshold)[0]

    print("\n%d out of %d events with probability > %.2f:\n %s" % 
            (len(ind_frb), len(y_pred_prob), 
                prob_threshold, ind_frb))

    if len(ind_frb)==0:
        return 

    low_to_high_ind = np.argsort(y_pred_prob)

    if save_ranked is True:
        print("Need to fix the file naming")
#        fnout_ranked = fn_data.rstrip('.hdf5') + \
#                       'freq_time_candidates.hdf5'

        fnout_ranked = fnout + '.hdf5'

        g = h5py.File(fnout_ranked, 'w')
        g.create_dataset('data_frb_candidate', data=data[ind_frb])
        g.create_dataset('frb_index', data=ind_frb)
        g.create_dataset('probability', data=y_pred_prob)
        g.create_dataset('params', data=params)
        g.close()
        print("\nSaved them and all probabilities to: \n%s" % fnout_ranked)


    if plot_ranked is True:
        if save_ranked is False:
            argtup = (data[ind_frb], ind_frb, y_pred_prob)

            ranked_ind_ = plot_tools.plot_multiple_ranked(argtup, nside=nside, \
                                            fnfigout=fnout, ascending=False, 
                                            params=params, ranked_ind=ranked_ind,
                                            yaxlabel=yaxlabel)
        else:
            ranked_ind_ = plot_tools.plot_multiple_ranked(fnout_ranked, nside=nside, \
                                            fnfigout=fnout, ascending=False,
                                            params=params, ranked_ind=ranked_ind,
                                            yaxlabel=yaxlabel)

        return ranked_ind_

    return None

if __name__=="__main__":
    parser = optparse.OptionParser(prog="classify.py", \
                        version="", \
                        usage="%prog FN_DATA FN_MODEL [OPTIONS]", \
                        description="Apply DNN model to FRB candidates")

    parser.add_option('--fn_model_dm', dest='fn_model_dm', type='str', \
                        help="Filename of dm_time model. Default None", \
                        default=None)

    parser.add_option('--fn_model_time', dest='fn_model_time', type='str', \
                        help="Filename of 1d time model. Default None", \
                        default=None)

    parser.add_option('--fn_model_mb', dest='fn_model_mb', type='str', \
                        help="Filename of multibeam model. Default None", \
                        default=None)

    parser.add_option('--pthresh', dest='prob_threshold', type='float', \
                        help="probability treshold", default=0.5)

    parser.add_option('--save_ranked', dest='save_ranked', 
                        action='store_true', \
                        help="save FRB events + probabilities", \
                        default=False)

    parser.add_option('--plot_ranked', dest='plot_ranked', \
                        action='store_true',\
                        help="plot triggers", default=False)

    parser.add_option('--twindow', dest='twindow', type='int', \
                        help="time width, default 64", default=64)

    parser.add_option('--fnout', dest='fnout', type='str', \
                       help="beginning of figure names", \
                       default='ranked')

    parser.add_option('--nside', dest='nside', type='int', \
                       help="number of rows/cols of subplots per figure", \
                       default=7)

    options, args = parser.parse_args()

    assert len(args)==2, "Arguments are FN_DATA FN_MODEL [OPTIONS]"

    fn_data = args[0]
    fn_model_freq = args[1]

    print("Using datafile %s" % fn_data)
    print("Using keras model in %s" % fn_model_freq)

    data_freq, y, data_dm, data_mb, params = reader.read_hdf5(fn_data)

    NFREQ = data_freq.shape[1]
    NTIME = data_freq.shape[2]
    WIDTH = options.twindow

    # low time index, high time index
    tl, th = NTIME//2-WIDTH//2, NTIME//2+WIDTH//2

    if data_freq.shape[-1] > (th-tl):
        data_freq = data_freq[..., tl:th]

    fn_fig_out = options.fnout + '_freq_time'
    print("\nCLASSIFYING FREQ/TIME DATA\n")
    ranked_ind_freq = classify(data_freq, fn_model_freq, 
                             save_ranked=options.save_ranked, 
                             plot_ranked=options.plot_ranked, 
                             prob_threshold=options.prob_threshold,
                             fnout=fn_fig_out, params=params, 
                             nside=options.nside, yaxlabel='Freq')

    if options.fn_model_dm is not None:
        if len(data_dm)>0:
            print("\nCLASSIFYING DM/TIME DATA\n)")
            fn_fig_out = options.fnout + '_dm_time'
            classify(data_dm, options.fn_model_dm, 
                     save_ranked=options.save_ranked, 
                     plot_ranked=options.plot_ranked, 
                     prob_threshold=options.prob_threshold,
                     fnout=fn_fig_out, params=params, 
                     nside=options.nside, 
                     ranked_ind=ranked_ind_freq, yaxlabel='DM')
        else:
            print("No DM/time data to classify")

    if options.fn_model_time is not None:
        print("\nCLASSIFYING 1D TIME DATA\n)")
        fn_fig_out = options.fnout + '_1d_time'
        classify(data_freq, options.fn_model_time, 
             save_ranked=options.save_ranked, 
             plot_ranked=options.plot_ranked, 
             prob_threshold=options.prob_threshold,
             fnout=fn_fig_out, params=params, 
             nside=options.nside, 
             ranked_ind=ranked_ind_freq, yaxlabel='')

    if options.fn_model_mb is not None:
        classify(data_mb, options.fn_model_mb, 
             save_ranked=options.save_ranked, 
             plot_ranked=options.plot_ranked, 
             prob_threshold=options.prob_threshold,
             fnout=options.fnout, params=params, 
             nside=options.nsidem, ranked_ind=ranked_ind_freq)








            
