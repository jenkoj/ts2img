import numpy as np
import itertools as it
import pandas as pd
from pyts.image import GramianAngularField
from pyts.image import RecurrencePlot


def moving_window(x:np.ndarray, length:int, step:int=1) -> np.ndarray:
    """
    Slices input x to specified length and step. Remainder is dicarded. 
    """
    streams = it.tee(x, length)
    return np.asarray(list(zip(*[it.islice(stream, i, None, step*length) for stream, i in zip(streams, it.count(step=step))])))


def all_equal(sig: np.ndarray) -> bool:
    """
    Checks if elements in input array are all of equal value. 
    """
    return True if np.min(sig)-np.max(sig) == 0 else False
    

def percent_nan(sig:np.ndarray) -> int:  
    """
    Return percent of missing data. 
    """  
    return (np.count_nonzero(~np.isnan(sig))/sig.shape[0])


def fill_missing(sig:np.ndarray) -> np.ndarray:
    """
    Fill missing data first with backfill,then with forwardfill, finally convert to list and return it.
    """
    return np.asarray(pd.Series(sig).bfill().ffill().tolist())


def filter_empty_slices_and_fill_missing_samples(signal_slices:np.ndarray, time_stamp_slices:np.ndarray, par: dict) -> np.ndarray:
    """
    Loop trough slices of signal data and remove data that has less that par["missing_data_allowed"], if more fill NaNs with bfill and ffill. 

    :param: slignal_slices - np.array of singal slices
    :param: time_stamp_slices - np.arrat of slices of time stamps

    :return: signal_out, time_stamp_out - tuple of [np.ndarray np.ndarray] of processed slices
    """
    try:
        signal_out, time_stamp_out =  zip(*[(fill_missing(sig), stamp) for sig, stamp in zip(signal_slices, time_stamp_slices) if percent_nan(sig) > par["percentage_of_missing_data_allowed"] ])

    except ValueError:
        # In case when nothing to return, list comprehension returns ValueError.
        signal_out, time_stamp_out = ([],[])

    except: raise

    return np.asarray(list(signal_out)), np.asarray(list(time_stamp_out))


def filter_low_entropy_slices(signal_slices: np.ndarray, time_stamp_slices: np.ndarray, par: dict):
    """ 
    Removes slices with power less than 10W and slices that have all samples of the same value. 
    """
    try:
        signal_out, time_stamp_out =  zip(*[[sig,stamp] for sig, stamp in zip(signal_slices, time_stamp_slices) if not all_equal(sig) and np.any(sig > 10) ])
        
    except ValueError:
        # In case when nothing to return, list comprehension returns ValueError.
        signal_out, time_stamp_out = ([],[])
        
    except: raise

    return np.asarray(list(signal_out)), np.asarray(list(time_stamp_out))


def trasfrom_ts(sig: np.ndarray, par:dict):
    """
    Returns image of input time series signal.

    :param sig: Time series power signal.
    :param par: Dictionary of parameters. 
    :return img: Trasformed image.
    :return sig: Time series power signal. 
    """

    sig = sig[np.newaxis,:]

    # Recurrence plot
    if par["trs_type"] == "RECU":
        rp = RecurrencePlot(threshold=None)
        img = rp.fit_transform(sig)

    # Gramian angular fields
    if par["trs_type"] == "GAF":
        
        if par["trs_type_gaf"] == "GASF":
            gasf = GramianAngularField(image_size=par["img_size"], method='summation')
            img = gasf.fit_transform(sig)

        elif par["trs_type_gaf"] == "GADF":
            gadf = GramianAngularField(image_size=par["img_size"], method='difference')
            img = gadf.fit_transform(sig)

        else:
            raise ValueError("GAF type not defined!")
    else: 
        raise ValueError("trs type not defined!")
    
    # Multiply image with non-zero mean of the signal.
    if par["add_brightness"] == "Y":
        sig_mean = np.true_divide(sig.sum(),(sig!=0).sum())
        img = img*sig_mean
    
    return sig, img





