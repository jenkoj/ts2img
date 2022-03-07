import warnings
import pandas as pd


def get_appliances(dataset: pd.DataFrame, par: dict) -> list:
    """
        Returns list of appliances. 
    """
    if par["manually_select_appliances"]:

        if dataset.metadata["name"] == "REDD":
            # Appliances for REDD.
            # all
            appliances = ["microwave","sockets","washer dryer", "dish washer","electric stove","electric oven","fridge","electric space heater","light","air conditioner","CE applaince","electric furnace","air handling unit"]
            # short
            # par["appliances"] = ["microwave"]
            
        elif dataset.metadata["name"] == "iAWE":
            # Applicances for iAWE. 
            appliances = ["fridge","television","clothes iron","washing machine","computer","air conditioner"]

        elif dataset.metadata["name"] == "UK-DALE":
            # Appliances for UKDALE.
            # all
            appliances = ["microwave","toaster","kettle","HTPC","dish washer","server computer","washing machine","freezer","fridge freezer","desktop computer","light","computer monitor", "laptop computer", "television", "washer dryer","boiler","fridge"]
            # short
            # par["appliances"] = ["microwave","toaster","kettle"]

        elif dataset.metadata["name"] == "REFIT":
            # Appliances for REFIT.
            appliances = ['washing machine','television','dish washer','fridge','computer',"toaster","washer dryer","tumble dryer","unknown","audio system","fridge freezer","electric space heater","food processor","broadband router","breadmaker","appliance","dehumidifier","fan","pond pump","games console"]
            # short
            # par["appliances"]= ["microwave","kettle","toaster"]
        
        elif dataset.metadata["name"] == "ECO":
            # Appliances for ECO. 
            # all    
            appliances = ["kettle","microwave","HTPC","freezer","fridge","coffee maker","computer","laptop computer","lamp","washing machine","dish washer","audio system","air handling unit","broadband router","garden sprinkler"]
            # short
            # par["appliances"] = ["kettle","microwave"]

        else:
            raise ValueError("Dataset not supported for manual selection! Please add it in get_appliances() or set manual selection to False.") 

    else:
        appliances = set()
        for building in dataset.buildings:
        
            for meter in dataset.buildings[building].elec.submeters().meters:
                
                appliance_metadata = meter.appliances[0].metadata
                label = appliance_metadata.get("type")
                appliances.add(label)

        # Get rid of duplicates.     
        appliances = list(appliances)
    
    return appliances


def param_setup(dataset: pd.DataFrame, par: dict) -> None:
    """
    Sets up and fixes possible misconfiguration.
    """
    # Get parameters from metadata.
    par["dataset_name"] = dataset.metadata["name"].lower()
    par["n_buildings"] = len(dataset.buildings)

    # Calculate estimated size of time series.
    par["ts_size"] = round((par["step_in_mins"]*60)/par["resample_period"])

    # RECU already includes brightness.
    if par["trs_type"] == "RECU": 
        warnings.warn("Warning........... Reccurrent plots already include brightness!")
        par["add_brightness"] = False

    # When using all buildings parameter selected_building must be A.
    if par["multiple_buildings"]: par["selected_building"] = "A"
        
    # Handle edge case for RECU.
    par["org_img_size"] = par["img_size"]

    # In case of reccurrent plot input size must be same as output.
    if par["trs_type"] == "RECU": par["img_size"] = par["ts_size"] 

    if par["backfill_limit"] > (par["ts_size"] / 2):
         warnings.warn("Warning........... par['backfill_limit'] is too large, it could resampling could result in invalid time series data.")
