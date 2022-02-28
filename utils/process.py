import numpy as np
import itertools as it
from pyts.image import GramianAngularField
from pyts.image import RecurrencePlot


def moving_window(x:np.ndarray, length:int, step:int=1) -> np.ndarray:
    """
    Slices input x to specified length and step. Remainder is discarded. 
    """
    streams = it.tee(x, length)
    return np.asarray(list(zip(*[it.islice(stream, i, None, step*length) for stream, i in zip(streams, it.count(step=step))])))


def transform_ts(sig: np.ndarray, par:dict):
    """
    Returns image of input time series signal.

    :param sig: Time series power signal.
    :param par: Dictionary of parameters. 
    :return img: Transformed image.
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





