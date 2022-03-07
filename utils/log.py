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

        " sample period: "f"{par['resample_period']}","\n"

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


def print_progress(i: int, signal_stack: np.ndarray, img_stack: np.ndarray, next_percent:int, par: dict) -> int:
    """
    Prints current progress of transformation every 10 %.
    """
    signal_slices_len = signal_stack.shape[0]
    img_stack_len = img_stack.shape[0]
    
    if round(100*i/(signal_slices_len),2) > next_percent:
        next_percent += 10
        print_log(par,"processed: "f"{round(100*i/(signal_slices_len), 2)} % finished: "f"{round(100*((img_stack_len)/par['max_images']), 2)} %")
    
    return next_percent

    
def print_end_of_loop(images_stacked: int, appliance: str, par: dict):
    """
    Informs user that script has reached the end of the loop.
    """
    print_log(par,"\n")
    print_log(par,"number of images (per appliance) stacked: "f"{images_stacked}")
    
    print_log(par,"finished "f"{appliance}")
    print_log(par,"\n")


def print_end(all_images_stacked: int, healthy_appliances: int, par: dict):
    """
    Informs user that script has come to an end.  
    """
    print_log(par,"num of images stored: ", all_images_stacked)
    print_log(par,"appliances stored: ", healthy_appliances)
