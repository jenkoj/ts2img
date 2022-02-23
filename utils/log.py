import numpy as np
import datetime
from utils.file_handling import get_file_name, get_path

path = get_path()


def print_parameters(par: dict) -> None:
    """
    Prints user defined parameters. 
    """
    print_log(par,
        "dataset name: ",par["dataset_name"],", date : ",datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')," \n"

        " using appliances: ", par['appliances'],"\n"

        " transtype: ",par["trs_type"],"\n"
        " gaf trans type: "f"{par['trs_type_gaf']}","\n"

        " windows size in mins: "f"{par['step_in_mins']}","\n"
        " image size in pixels: "f"{par['img_size']}","\n"

        " sample period: "f"{par['sample_period']}","\n"

        " number if images that are stacked together and in series(series!): "f"{par['frames']}","\n"
        " allowed max delta between images  "f"{par['allowed_delta_between_frames']}","\n"

        " added brightness:  "f"{par['add_brightness']}","\n"

        " save source timeseries: "f"{par['ts_save']}","\n"
        
        " manually select appliances: "f"{par['manually_select_appliances']}","\n"

        " number of appliances: "f"{len(par['appliances'])}","\n"
        " number of buildings: "f"{par['n_buildings']}","\n"

        " max number of images per appliance per building: "f"{par['max_images']}","\n"

        " include multiple buildings (Y for Yes N for No): "f"{par['multiple_buildings']}","\n"
        " building selected: "f"{par['selected_building']}","\n"
    )


def print_log(par: dict, *args, **kwargs):
    """
    Prints log to stdout and file. 
    """
    print(*args, **kwargs)
    file_name = get_file_name(par)

    with open(path+file_name+"_log.txt",'a') as file:
        print(*args, **kwargs, file=file)


def print_progress(i: int, signal_stack: np.ndarray, img_stack: np.ndarray, print_flag:int, par: dict) -> int:
    """
    Prints current progress of transfomation every 10 %.
    """
    signal_slices_len = signal_stack.shape[0]
    img_stack_len = img_stack.shape[0]

    if round(100*i/(signal_slices_len),2) > print_flag:
        print_flag += 10

        #print("procesed: "f"{round(100*i/(signal_slices.shape[0]),2)}% finished: "f"{round(100*((img_stack.shape[0])/par['max_images']),2)}%")
        print_log(par,"procesed: "f"{round(100*i/(signal_slices_len),2)} % finished: "f"{round(100*((img_stack_len)/par['max_images']),2)} %")
    
    return print_flag


def print_break(par: dict):
    """
    Informs user that maximum number of images has been reached. 
    """
    #print("max size of "f"{par['max_images']}"" reached, skipping!")   
    print_log(par,"max size of "f"{par['max_images']}"" reached, skipping!")


def print_begin_appliance(appliance: str, par: dict):
    """
    Informs user what appliance will script process next. 
    """
    print_log(par,"\n")
    print_log(par,"Starting " f"{appliance} ("+str(par["appliances"].index(appliance)+1)+"/"+str(len(par["appliances"]))+"):")
    # print("\n")
    # print(" Starting " f"{appliance} ("+str(par["appliances"].index(appliance)+1)+"/"+str(len(par["appliances"]))+"):")


def print_begin_building(building: int, par: dict):
    """
    Informs user which building will script be processing. 
    """
    #print("Starting building ",building)
    print_log(par,"\n")
    print_log(par,"Starting building "f"{building}")


def print_end_of_loop(images_stacked: int, appliance: str, par: dict):
    """
    Informs user that script has reached the end of the loop.
    """
    print_log(par,"")
    print_log(par,"number of images (per appliance) stacked: "f"{images_stacked}")
    # print("")
    # print("number of images (per appliance) stacked: "f"{images_stacked}")

    print_log(par,"finished "f"{appliance}")
    #print("finished "f"{appliance}")
    
    #print("\n")
    print_log(par,"\n")


def print_end(all_images_stacked: int, healthy_appliances: int, par: dict):
    """
    Informs user that script has come to an end.  
    """
    print_log(par,"num of images stored: ", all_images_stacked)
    #print("num of images stored: ", all_images_stacked)
    print_log(par,"appliances stored: ", healthy_appliances)
    #print("appliances stored: ", healthy_appliances)