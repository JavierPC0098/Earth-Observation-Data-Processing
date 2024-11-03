from common.io.writeToa import readToa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from config import globalConfig
from config.l1bConfig import l1bConfig

# Check for all bands that the differences with respect to the output TOA (l1b_toa_) are <0.01% for at
# least 3-sigma of the points.
bands = ['VNIR-0','VNIR-1','VNIR-2','VNIR-3']
outdir_student_gmrs_toa = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1C\\my_output_mgrs"
outdir_lucia = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1C\\output"

prefix = 'l1c_toa_'

#Check for all bands that the differences with respect to the output TOA are <0.01% for 3-sigma of the points.

for band in bands:

    lucia_toa = readToa(outdir_lucia, prefix + band + '.nc')
    my_toa = readToa(outdir_student_gmrs_toa, prefix + band + '.nc')

    # Compare
    result = np.sort(my_toa) - np.sort(lucia_toa)
    porcentaje = result / my_toa * 100
    df = pd.DataFrame(porcentaje)
    porcentaje_df = df.fillna(0) # The division per zero gives some annoying NaN values
    boolean_comparison = np.array(porcentaje_df < 0.01)

    # Calculate the total number of values in each matrix
    total_values = boolean_comparison.size
    trues_matrix = np.full(boolean_comparison.shape, True)
    # Calculate the number of matching values (True values in the same positions)
    matching_values = np.sum(boolean_comparison == trues_matrix)
    # Calculate the threshold for 99.7% (3sigma) matching values
    threshold = 0.997 * total_values
    # Apply threshold to the matching values
    is_3sigma = matching_values >= threshold

    # Print the results
    if is_3sigma:
        print(
            f" -- The matrices difference is within the 0.01% for 3-Sigma of the points for the output TOA ({prefix + band})")
    else:
        print(
            f" -- WARNING: The matrices difference is outside of the 0.01% for 3-Sigma of the points for the output TOA ({prefix + band})")