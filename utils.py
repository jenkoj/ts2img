#path = "D:/jjenko/nilm data/GAF_DS/"

import datetime
from fileinput import filename
import re
from tokenize import String
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
        #start and end date are generaly not used, except when using non-optimized verison
    if dataset.metadata["name"] == "REDD":
        par["start_date"] = "2010-1-10T0000"
        par["end_date"] = "2012-5-20T0000"
        #appliances for redd
        #all
        par["appliances"] = ["microwave","sockets","washer dryer", "dish washer","electric stove","electric oven","fridge","electric space heater","light","air conditioner","CE applaince","electric furnace","air handling unit"]
        #short
        #par["appliances"] = ["microwave"]
        
    elif dataset.metadata["name"] == "iAWE":
        par["start_date"] = "2013-1-18T1800"
        par["end_date"] = "2013-12-18T1900"
        #applicances for iawe 
        par["appliances"] = ["fridge","television","clothes iron","washing machine","computer","air conditioner"]

    elif dataset.metadata["name"] == "UK-DALE":
        par["start_date"] = "2013-1-10T0000"
        par["end_date"] = "2014-2-20T0000"
        #appliances for ukdale
        #all
        par["appliances"] = ["microwave","toaster","kettle","HTPC","dish washer","server computer","washing machine","freezer","fridge freezer","desktop computer","light","computer monitor", "laptop computer", "television", "washer dryer","boiler","fridge"]
        #short
        #par["appliances"] = ["microwave","toaster","kettle"]

    elif dataset.metadata["name"] == "REFIT":
        par["start_date"] = "2013-10-10T0000"
        par["end_date"] = "2015-8-20T0000"
        #appliances for refit
        par["appliances"] = ['washing machine','television','dish washer','fridge','computer',"toaster","washer dryer","tumble dryer","unknown","audio system","fridge freezer","electric space heater","food processor","broadband router","breadmaker","appliance","dehumidifier","fan","pond pump","games console"]
        #short
        #par["appliances"]= ["microwave","kettle","toaster"]
       
    elif dataset.metadata["name"] == "ECO":
        par["start_date"] = "2012-06-10T0000"
        par["end_date"] = "2013-03-20T0000"
        #appliances for eco 
        #all    
        par["appliances"] = ["kettle","microwave","HTPC","freezer", "fridge", "coffee maker","computer","laptop computer","lamp","washing machine","dish washer","audio system","air handling unit","broadband router","garden sprinkler"]
        #short
        #par["appliances"] = ["kettle","microwave"]

    else:
        raise ValueError("Invalid dataset name") 

    
    if par["manauly_select_appliances"] == False:

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


def trasfrom_ts(ts,par):
    """
    Returns image of timeseries 

    :param ts: timeseries power data
    :param par: dictionary of parameters 
    :return img: Returns image numpy array
    :return ts_pad: Returns padded power data timeseries numpy array
    """

    #calculate mean value of timeseries, that will be multiplied to the matrix. 
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        try:
            ts_mean = ts[ts != 0].mean()
        except RuntimeWarning:
            #nadaljuj 
            raise ValueError
    
    ts = ts[np.newaxis,:]

    #do some timeseries reshaping and padding 
    
    # TODO probaj narest brez if elsa 
    if ts.shape[1] <= par["ts_size"]:
        #dodaj novo spremniljvko paddng 

        ts_pad = np.pad(ts, [(0,0),(0, par["ts_size"]-ts.shape[1])], 'constant')
    
    else:
        #handle edge case 
        ts_pad = ts[:,:par["ts_size"]]

    #recurrence transform
    if par["trs_type"] == "RECU":
        rp = RecurrencePlot(threshold=None)
        img = rp.fit_transform(ts_pad)

    #gaf transform
    if par["trs_type"] == "GAF":
        
        if par["trs_type_gaf"] == "GASF":
            gasf = GramianAngularField(image_size=par["img_size"], method='summation')
            img = gasf.fit_transform(ts_pad)

        elif par["trs_type_gaf"] == "GADF":
            gadf = GramianAngularField(image_size=par["img_size"], method='difference')
            img = gadf.fit_transform(ts_pad)

        else:
            raise ValueError("GAF type not defined!")
    else: 
        raise ValueError("trs type not defined!")
    
    #multiply mean
    if par["add_brightness"] == "Y":
        img = img*ts_mean
    
    return img, ts_pad

#TODO split images and timeseries to two functions 
#TODO define img_stack tmp for normal append
def append_images(img,img_stack, img_stack_tmp, ts_pad, ts_stack, ts_stack_tmp, interval, last_interval, par):
    """
    Appends images and ts 

    :param img: timeseries images numpy array
    :param img_stack: stack of past images numpy array
    :param img_stack_tmp: stack of temp images for n_dim images numpy array

    :param ts_pad: padded timeseries numpy array
    :param ts_stack: stack of past timeseries numpy array
    :param ts_stack_tmp: stack of temp images for n_dim images numpy array

    :param interval: current intreval int
    :param last_interval: for tracking diff between images int
    :param par: dictionary of user defined parameters 

    :return: None
    """
    
    #part where we save converted images
    if len(img_stack.shape) == 4:
        #append as multi dimensonal images 

        if img_stack_tmp.shape[0] < par["frames"]:
            #images in multi dim array must be in strict series order
            delta_interval = interval - last_interval 
            last_interval = interval
            
            if delta_interval <= par["allowed_delta_between_images"]: 
                #append, images are strictly in series
                img_stack_tmp = np.append(img_stack_tmp, img, axis=0)
                ts_stack_tmp = np.append(ts_stack_tmp, ts_pad, axis=0)

            else:
                #reset stack to 0
                ts_stack_tmp = np.zeros([0, par["ts_size"]])
                img_stack_tmp = np.zeros([0, par["img_size"], par["img_size"]])

        else:
            #full   
            img_stack_tmp = img_stack_tmp[np.newaxis, ...] #add new axis for compatability
            img_stack = np.append(img_stack, img_stack_tmp, axis=0)
            
            ts_stack_tmp = ts_stack_tmp[np.newaxis, ...] #add new axis for compatability
            ts_stack = np.append(ts_stack, ts_stack_tmp, axis=0)

            #reset stack to 0
            ts_stack_tmp = np.zeros([0, par["ts_size"]])
            img_stack_tmp = np.zeros([0, par["img_size"], par["img_size"]])

    else:
        #append as ordinary images
        img_stack = np.append(img_stack, img, axis=0)
        ts_stack = np.append(ts_stack, ts_pad, axis=0)
       


    return img_stack, img_stack_tmp, ts_stack, ts_stack_tmp