import xarray as xr

def var_exists(var_list : list, ds : xr.Dataset):
    """ Check if variables exist in the dataset and if not remove them from the list
        
    :param var_list: list of variables to check
    :param ds: xarray dataset
    :return: list of variables that exist in the dataset
    """ 
    for var in var_list:
        if var not in ds:
            var_list.remove(var)
    return var_list