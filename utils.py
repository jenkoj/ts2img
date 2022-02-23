#path = "D:/jjenko/nilm data/GAF_DS/"

import datetime
from fileinput import filename

from tokenize import String
from turtle import stamp
import h5py
import warnings
from pyts.image import GramianAngularField
from pyts.image import RecurrencePlot
import pathlib
import numpy as np 


#TODO make dir if not exist
path = str(pathlib.Path().cwd())+"/out/"

def print_parameters(par):
    print_log(par,
        "dataset name: ",par["dataset_name"],", date : ",datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')," \n"

        "using data from ",par["start_date"]," to ", par["end_date"]," \n"

        " using appliances: ",par["appliances"],"\n"

        " transtype: ",par["trs_type"],"\n"
        " gaf trans type: "f"{par['trs_type_gaf']}","\n"

        " windows size in mins: "f"{par['step_in_mins']}","\n"
        " image size in pixels: "f"{par['img_size']}","\n"

        " sample period: "f"{par['sample_period']}","\n"

        " number if images that are stacked together and in series(series!): "f"{par['frames']}","\n"
        " allowed max delta between images  "f"{par['allowed_delta_between_images']}","\n"

        " added brightness:  "f"{par['add_brightness']}","\n"

        " save source timeseries: "f"{par['ts_save']}","\n"

        " number of appliances: "f"{len(par['appliances'])}","\n"
        " number of buildings: "f"{par['n_buildings']}","\n"

        " max number of images per appliance per building: "f"{par['max_images']}","\n"

        " include multiple buildings (Y for Yes N for No): "f"{par['multiple_buildings']}","\n"
        " building selected: "f"{par['selected_building']}","\n"
    )


def get_appliances(dataset,par):
    
    if par["manauly_select_appliances"]:

        if dataset.metadata["name"] == "REDD":
            #appliances for redd
            #all
            par["appliances"] = ["microwave","sockets","washer dryer", "dish washer","electric stove","electric oven","fridge","electric space heater","light","air conditioner","CE applaince","electric furnace","air handling unit"]
            #short
            #par["appliances"] = ["microwave"]
            
        elif dataset.metadata["name"] == "iAWE":
            #applicances for iawe 
            par["appliances"] = ["fridge","television","clothes iron","washing machine","computer","air conditioner"]

        elif dataset.metadata["name"] == "UK-DALE":
            #appliances for ukdale
            #all
            par["appliances"] = ["microwave","toaster","kettle","HTPC","dish washer","server computer","washing machine","freezer","fridge freezer","desktop computer","light","computer monitor", "laptop computer", "television", "washer dryer","boiler","fridge"]
            #short
            #par["appliances"] = ["microwave","toaster","kettle"]

        elif dataset.metadata["name"] == "REFIT":
            #appliances for refit
            par["appliances"] = ['washing machine','television','dish washer','fridge','computer',"toaster","washer dryer","tumble dryer","unknown","audio system","fridge freezer","electric space heater","food processor","broadband router","breadmaker","appliance","dehumidifier","fan","pond pump","games console"]
            #short
            #par["appliances"]= ["microwave","kettle","toaster"]
        
        elif dataset.metadata["name"] == "ECO":
            #appliances for eco 
            #all    
            par["appliances"] = ["kettle","microwave","HTPC","freezer","fridge","coffee maker","computer","laptop computer","lamp","washing machine","dish washer","audio system","air handling unit","broadband router","garden sprinkler"]
            #short
            #par["appliances"] = ["kettle","microwave"]

        else:
            raise ValueError("Invalid dataset name") 

    else:
        appliances = set()
        for building in dataset.buildings:
        
            for meter in dataset.buildings[building].elec.submeters().meters:
                
                appliance_metadata = meter.appliances[0].metadata
                label = appliance_metadata.get("type")
                appliances.add(label)
                
        par["appliances"] = list(appliances)
    
def print_log(par, *args, **kwargs):
    #print(*args, **kwargs)
    file_name = get_file_name(par)

    with open(path+file_name+"_log.txt",'a') as file:
        print(*args, **kwargs, file=file)

def get_file_name(par:dict) -> str:
    """
    Creates meaningful filename based on used parameters.

    :param: par - Dictionary containing all parameters 
    :return: string - File name 
    """
    trs_type_cp = par["trs_type"]

    if trs_type_cp == "GAF":
        trs_type_cp = par['trs_type_gaf']
    
    file_name =f"{par['dataset_name']}""_" \
                f"{trs_type_cp}""_" \
                f"{par['step_in_mins']}""m_" \
                f"{par['img_size']}""S" \
                f"{par['frames']}""X_" \
                f"{len(par['appliances'])}""A" \
                f"{par['max_images']}""N_" \
                f"{par['selected_building']}""B"
                    
    if par["add_brightness"]:
        file_name += "_BRIG"

    if par["ts_save"]:
        file_name += "_SRC-TS"

    return file_name

def create_file(par):
    
    file_name = get_file_name(par)

    #check if file exists
    try:
        file = h5py.File(path+file_name+".hdf5","r")
        print("file exists!")
        file.close()

    except:
        print("creating new file! ...")
        file = h5py.File(path+file_name+".hdf5", "w")
        file.close()

    return file_name

def create_hdf5_group(file_name, group_name): 
    """
    Creates HDF5 group
    groups are appliances such as fridge or toaster
    """  
    file = h5py.File(path+file_name+".hdf5", "a")
    dataset = file.create_group(f"{group_name}")
    file.close()


def store_single_hdf5(file_name, data, file_id, group_name): 
    """
    Stores single image to HDF5
    """     
    file = h5py.File(path+file_name+".hdf5", "a")
    group = file[f"{group_name}"]
    
    try:
        group.create_dataset(f"{file_id}",np.shape(data),data = data)  
    except:
        del group[f"{file_id}"]
        group.create_dataset(f"{file_id}",np.shape(data),data = data)
        print("  replaced "f"{file_id}""!")
   
    file.close()

def store_many_hdf5(file_name, images, group_name, image_set_name, **kwargs):
    """
    Stores multiple images to HDF5
    **kwargs(force_del="yes" to replace existing db w/o prompt)
    """     
    #define some parameters
    num_images = len(images)
    force_del_flag = kwargs.get('force_del', None)# we need it, if "store many" is frequently called
    
    label_flag = kwargs.get('labels', None)# we need it, if "store many" is frequently called

    # read HDF5 file
    try:
        file = h5py.File(path+file_name+".hdf5", "a")
    except:
        print("file not found!")
    
    
    # open specified group
    try:
        group = file[f"{group_name}"]
    except:
        #if if does not exist create it
        group = file.create_group(f"{group_name}")
        
     
    #check if ds already exists, then prompt user
    for name in group:
        if str(name) == str(image_set_name):
            if force_del_flag == "yes":
                print("  removed "f"{name}""!")   
                del group[name]
            else:
                print("Dataset '"f"{name}" "' already exists in " f"{file_name}""/"f"{group_name}")
                
                ans = input("Do you want to replace existing dataset? (y,n) Press enter to contine")
                    
                if ans == "y":
                    print("  removed "f"{name}""!")   
                    del group[name]
                else:
                    print("  quiting! ") 
                    raise

    # Create a dataset in the group       
    print("storing... samples to store: "f"{num_images}")
    
    if label_flag == True:
        #save labels as integers. If sentence needed in case no labels are provided
        dataset = group.create_dataset(f"{image_set_name}", np.shape(images), h5py.h5t.H5T_STD_I8BE , data=images)
    else:
        dataset = group.create_dataset(f"{image_set_name}", np.shape(images), h5py.h5t.IEEE_F32LE , data=images)
    
    file.close()
    print("finshed. stored to " f"{file_name}""/"f"{group_name}""/"f"{image_set_name}")


def read_many_hdf5(file_name, group_name, image_set_name):
    """ 
    Reads image from HDF5.

    """
    images = []
    
    # Open the HDF5 file
    file = h5py.File(path+file_name+".hdf5", "r+")

    images = np.array(file[f"{group_name}""/"f"{image_set_name}"])

    return images


def get_good_sections(meter:object, diff_in_seconds:int) -> list:
    """ 
    Returns array of time sections when appliance was operating.

    :param meter: generator object containing data
    :param diff_in_seconds: int value to set maximum time difference between returen time slots 
    :return: Returns array of time slots

    """
    df = next(meter.load(physical_quantity='power'))
    timestamps = df.index.view(np.int64)//10**9

    good_sections_start = []
    good_sections_stop = []

    good_sections_start.append(df.index[0].replace(tzinfo=None))

    for i in range(len(timestamps[0:-2])):
        
        diff = timestamps[i+1] - timestamps[i]
        
        if diff > diff_in_seconds:
            good_sections_stop.append(df.index[i].replace(tzinfo=None))
            
            good_sections_start.append(df.index[i+1].replace(tzinfo=None))

    good_sections_stop.append(df.index[-1].replace(tzinfo=None))
    good_sections = [good_sections_start, good_sections_stop]
    
    return good_sections

def get_clean_data(df, pwr_flag, par):
    """
    Returns power data if time slot cannot be read, it raises ValueError

    :param df: pandas dataFrame containing timeseries data
    :param pwr_flag: array of boolean flags, prevents overloging 
    :param par: dictionary of parameters 
    :return: Returns timeseries power data numpy.ndarray
    """
        
    #do some metric calcs in order to determine if selected window needs to be dropped
    metric = par["org_img_size"]*par["percentage_of_missing_data_allowed"]
    if len(df) < metric:
        par["count"][0] +=1
        raise ValueError
    
    #resample data to 6s
    df = df.resample("6s").bfill(limit=1).interpolate()

    #read power data and write it to timeseries 
    try:
        ts = df.fillna(0).power.active.values.transpose()
    except:
        if pwr_flag[0]:
            print("no active power!")
            print_log("no active power!")
            pwr_flag[0] = False
        try:
            if pwr_flag[1]:
                print("using apparent power!")
                print_log("using apparent power!")
                pwr_flag[1] = False
            ts = df.fillna(0).power.apparent.values.transpose()
        except:
            if pwr_flag[2]:
                print("no apparent power!")
                print_log("no apparent power!")
                pwr_flag[2] = False

            par["count"][1] +=1
            raise ValueError

    #check if all values in an array are equal to 0
    All_equal = np.all(ts==ts[0])

    #power below 15 W is considered noise
    All_lessthan = np.all(ts < 15 ) 

    if  All_equal or All_lessthan :
        par["count"][2] +=1
        raise ValueError

    return ts


def trasfrom_ts(sig,par):
    """
    Returns image of timeseries 

    :param ts: timeseries power data
    :param par: dictionary of parameters 
    :return img: Returns image numpy array
    :return sig: Returns padded power data timeseries numpy array
    """

    sig = sig[np.newaxis,:]

    #recurrence transform
    if par["trs_type"] == "RECU":
        rp = RecurrencePlot(threshold=None)
        img = rp.fit_transform(sig)

    #gaf transform
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
    
    #multiply mean
    if par["add_brightness"] == "Y":
        sig_mean = np.true_divide(sig.sum(),(sig!=0).sum())
        img = img*sig_mean
    
    return sig, img


def append_images(img,img_stack, img_stack_tmp, sig, sig_stack, sig_stack_tmp, time_stamp, last_stamp, par):
    """
    Appends images and ts 

    :param img: timeseries images numpy array
    :param img_stack: stack of past images numpy array
    :param img_stack_tmp: stack of temp images for n_dim images numpy array

    :param sig: padded timeseries numpy array
    :param sig_stack: stack of past time series numpy array
    :param sig_stack_tmp: stack of temp images for n_dim images numpy array

    :param time_stamp: current intreval int
    :param last_stamp: for tracking diff between images int
    :param par: dictionary of user defined parameters 

    :return: None
    """
    
    delta = time_stamp[0] - last_stamp
    last_stamp = time_stamp[-1]

    if delta <= par["allowed_delta_between_frames"] or img_stack_tmp.shape[0] == 0: 
        #append only if images are strictly in series
        img_stack_tmp = np.append(img_stack_tmp, img, axis=0)
        sig_stack_tmp = np.append(sig_stack_tmp, sig, axis=0)

        if img_stack_tmp.shape[0] == par["frames"]:
            #append to main
            img_stack_tmp = img_stack_tmp[np.newaxis, ...] #add new axis for compatability
            img_stack = np.append(img_stack, img_stack_tmp, axis=0)
            
            sig_stack_tmp = sig_stack_tmp[np.newaxis, ...] #add new axis for compatability
            sig_stack = np.append(sig_stack, sig_stack_tmp, axis=0)

            #reset stack to 0
            sig_stack_tmp = np.zeros([0, par["ts_size"]])
            img_stack_tmp = np.zeros([0, par["img_size"], par["img_size"]])

    else:
        #if not, reset stack to 0
        sig_stack_tmp = np.zeros([0, par["ts_size"]])
        img_stack_tmp = np.zeros([0, par["img_size"], par["img_size"]])


    return img_stack, img_stack_tmp, sig_stack, sig_stack_tmp, last_stamp


def mount_data(meter: pd.DataFrame) -> np.ndarray:
    """ 
        Reads data from dataframe generator and resamples it to 6s.
        In case active power cannot be mounted, it warns user and mounts apparent power. 
    """
    #read power data and write it to timeseries 

    df = next(meter.load(physical_quantity='power'))

    # possible implementation with bigger output
    #df = df.resample('6s').bfill(limit=2)

    df = df.resample("6s").asfreq()

    tstamps = df.index.view(np.int64)//10**9

    try:
        ts = df.power.active.values.transpose()
    except:
        print("no active power!")
        print_log("no active power!")
        
        try:
            print("using apparent power!")
            print_log("using apparent power!")
            
            ts = df.fillna(0).power.apparent.values.transpose()
        
        except:
            print("no apparent power!")
            print_log("no apparent power!")
            
            raise ValueError
    
    return [ts, tstamps]

def all_equal(sig: np.ndarray) -> bool:
    """
        Checks if elements in input array are all equal. 
    """
    return True if np.min(sig)-np.max(sig) == 0 else False
    

def moving_window(x:np.ndarray, length:int, step:int=1) -> np.ndarray:
    """
        Slices input x to specified length and step. Remainder is dicarded. 
    """
    streams = it.tee(x, length)
    
    return np.asarray(list(zip(*[it.islice(stream, i, None, step*length) for stream, i in zip(streams, it.count(step=step))])))
     

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
        # in case when nothing to return, list comprehension returns ValueError
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
        # in case when nothing to return, list comprehension returns ValueError
        signal_out, time_stamp_out = ([],[])
        
    except: raise

    return np.asarray(list(signal_out)), np.asarray(list(time_stamp_out))

def print_progress(i, signal_slices, img_stack, print_flag, par):
    """
    Prints current progress of transfomation every 10 %.
    """
    if round(100*i/(signal_slices.shape[0]),2) > print_flag:
        print_flag += 10

        print("procesed: "f"{round(100*i/(signal_slices.shape[0]),2)}% finished: "f"{round(100*((img_stack.shape[0])/par['max_images']),2)}%")
        print_log(par,"procesed: "f"{round(100*i/(signal_slices.shape[0]),2)}% finished: "f"{round(100*((img_stack.shape[0])/par['max_images']),2)}%")
    
    return print_flag


def print_break(par):
    """
    Informs user that maximum number of images has been reached. 
    """
    print("max size of "f"{par['max_images']}"" reached, skipping!")   
    print_log(par,"max size of "f"{par['max_images']}"" reached, skipping!")

def print_begin_appliance(appliance,par):
    """
    Informs user what appliance will script be processing. 
    """
    print_log(par,"\n")
    print_log(par," Starting " f"{appliance} ("+str(par["appliances"].index(appliance)+1)+"/"+str(len(par["appliances"]))+"):")
    print("\n")
    print(" Starting " f"{appliance} ("+str(par["appliances"].index(appliance)+1)+"/"+str(len(par["appliances"]))+"):")

def print_begin_building(building,par):
    """
    Informs user which building will scripb be processing. 
    """
    print("Starting building ",building)
    print_log(par,"\n")
    print_log(par,"Starting building "f"{building}")

def print_end_of_loop(images_stacked,appliance,par):
    """
    Informs user that script has reached end of loop.
    """
    print_log(par,"")
    print_log(par,"number of images (per appliance) stacked: "f"{images_stacked}")
    print("")
    print("number of images (per appliance) stacked: "f"{images_stacked}")

    print_log(par,"finished "f"{appliance}")
    print("finished "f"{appliance}")
    
    print("\n")
    print_log(par,"\n")

def print_end(all_images_stacked,healthy_appliances,par):
    """
    Informs user that script has come to an end.  
    """
    print_log(par,"num of images stored: ", all_images_stacked)
    print("num of images stored: ", all_images_stacked)
    print_log(par,"appliances stored: ", healthy_appliances)
    print("appliances stored: ", healthy_appliances)

def param_setup(dataset,par):
    """
    Sets up and fixes possible misconfiguration.
    """
    #get params from metadata 
    par["dataset_name"] = dataset.metadata["name"].lower()
    par["n_buildings"] = len(dataset.buildings)

    #calculate time esitmated size of time series
    par["ts_size"] = round(par["step_in_mins"]*60/par["sample_period"])

    #fix parms 
    #RECU already includes brightness 
    if par["trs_type"] == "RECU": par["add_brightness"] = False

    if par["multiple_buildings"]: par["selected_building"] = "A"
        
    #handle edge case for RECU
    par["org_img_size"] = par["img_size"]

    if par["trs_type"] == "RECU": par["img_size"] = par["ts_size"] 
