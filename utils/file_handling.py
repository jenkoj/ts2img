import numpy as np
from pathlib import Path
import h5py


def get_path() -> str:
    """
    Returns output path.
    """
    p = Path().cwd().joinpath("out")
    p.mkdir(exist_ok=True)

    return str(p)+"/"

path = get_path()


def get_file_name(par: dict) -> str:
    """
    Returns file name based on used parameters.
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


def create_file(par: dict) -> str:
    """
    Creates hdf5 file.
    """
    file_name = get_file_name(par)

    # Check if file exists.
    try:
        file = h5py.File(path+file_name+".hdf5","r")
        print("file exists!")
        file.close()

    except:
        print("creating new file! ...")
        file = h5py.File(path+file_name+".hdf5", "w")
        file.close()

    return file_name


def create_hdf5_group(file_name: str, group_name: str) -> None: 
    """
    Creates HDF5 group.
    Groups are appliances such as fridge or toaster.
    """  
    file = h5py.File(path+file_name+".hdf5", "a")
    file.create_group(f"{group_name}")
    file.close()


def store_single_hdf5(file_name, data, file_id, group_name) -> None: 
    """
    Stores single image to HDF5.
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


def store_many_hdf5(file_name: str, images: np.ndarray, group_name: str, image_set_name: str, **kwargs) -> None:
    """
    Stores multiple images to HDF5.
    **kwargs(force_del="yes" to replace existing data)
    """     
    # Define parameters.
    num_images = len(images)

    force_del_flag = kwargs.get('force_del', None)
    label_flag = kwargs.get('labels', None)

    # Read HDF5 file.
    try:
        file = h5py.File(path+file_name+".hdf5", "a")
    except:
        print("file not found!")
    

    # Open specified group.
    try:
        group = file[f"{group_name}"]
    except:
        # If it does not exist create it.
        group = file.create_group(f"{group_name}")
        
     
    # Check if data set already exists, then prompt user.
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

    print("storing... samples to store: "f"{num_images}")
    
    # Create a dataset inside the group.   
    if label_flag == True:
        group.create_dataset(f"{image_set_name}", np.shape(images), h5py.h5t.H5T_STD_I8BE , data=images) # Save labels as integers.
    else:
        group.create_dataset(f"{image_set_name}", np.shape(images), h5py.h5t.IEEE_F32LE , data=images)
    
    file.close()
    print("finshed. stored to " f"{file_name}""/"f"{group_name}""/"f"{image_set_name}")


def read_many_hdf5(file_name: str, group_name: str, image_set_name: str) -> np.array:
    """ 
    Reads image from HDF5.
    """
    images = []
    
    # Open the HDF5 file.
    file = h5py.File(path+file_name+".hdf5", "r+")

    images = np.array(file[f"{group_name}""/"f"{image_set_name}"])

    return images