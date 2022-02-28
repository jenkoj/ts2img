import numpy as np
import pandas as pd
from utils.log import print_log 


def mount_data(meter: pd.DataFrame, par: dict) -> np.ndarray:
    """ 
    Reads data from dataframe generator and resamples it to 6s.
    In case active power cannot be mounted, it warns user and mounts apparent power. 
    """ 
    # Load power meter data.
    df = next(meter.load(physical_quantity='power'))

    # Resample power data to "6s" and in case data is missing, back fill 10 samples
    df = df.resample('6s').bfill(limit=10)

    # Implementation with no backfill, resamples power data to "6s", works only when sample rate of source data set it 6s.
    #df = df.resample("6s").asfreq()

    # Get time stamps. 
    time_stamps = df.index.view(np.int64)//10**9

    # Try mount active power, if unsuccessful use apparent.
    try:
        ts = df.power.active.values.transpose()
    except:
        print("no active power!")
        print_log(par,"no active power!")
        try:
            print("using apparent power!")
            print_log(par,"using apparent power!")
            ts = df.fillna(0).power.apparent.values.transpose()
        except:
            print("no apparent power!")
            print_log(par,"no apparent power!")
            raise ValueError
    
    return [ts, time_stamps]


def append_images(img: np.ndarray, img_stack: np.ndarray, img_stack_tmp: np.ndarray, sig: np.ndarray, sig_stack: np.ndarray, sig_stack_tmp: np.ndarray, time_stamp: np.ndarray, last_stamp: int, par: dict):
    """
    Appends images and ts to main array.
    In case of video, it first appends N images to temporary array, and then to main array.   

    :param img: Current image.
    :param img_stack: Array of all images.
    :param img_stack_tmp: Array of N temporary images.

    :param sig: Current power signal.
    :param sig_stack: Array of all signals. 
    :param sig_stack_tmp: Array of N temporary signals.

    :param time_stamp: Array of time stamps
    :param last_stamp: Value of last time stamp, from previous iteration.
    :param par: Dictionary of user defined parameters.

    :return: Appended img_stack and sig_stack. 
    :return last_stamp: Updated with new last time stamp.
    """
    delta = time_stamp[0] - last_stamp
    last_stamp = time_stamp[-1]

    if delta <= par["allowed_delta_between_frames"] or img_stack_tmp.shape[0] == 0: 
        # Append only if images are strictly in series.
        img_stack_tmp = np.append(img_stack_tmp, img, axis=0)
        sig_stack_tmp = np.append(sig_stack_tmp, sig, axis=0)

        if img_stack_tmp.shape[0] == par["frames"]:
            # Append to main array.
            img_stack_tmp = img_stack_tmp[np.newaxis, ...]
            img_stack = np.append(img_stack, img_stack_tmp, axis=0)
            
            sig_stack_tmp = sig_stack_tmp[np.newaxis, ...]
            sig_stack = np.append(sig_stack, sig_stack_tmp, axis=0)

            # Reset stack
            sig_stack_tmp = np.zeros([0, par["ts_size"]])
            img_stack_tmp = np.zeros([0, par["img_size"], par["img_size"]])

    else:
        # If not in series, reset stack.
        sig_stack_tmp = np.zeros([0, par["ts_size"]])
        img_stack_tmp = np.zeros([0, par["img_size"], par["img_size"]])


    return img_stack, img_stack_tmp, sig_stack, sig_stack_tmp, last_stamp