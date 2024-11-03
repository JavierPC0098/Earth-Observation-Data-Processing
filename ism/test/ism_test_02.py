#
# Code developed by Javier Palacios Calatayud
# Master in Space Engineering (MiSE) - UC3M
# Earth Observation Data Processing
# Laboratory 2 - ISM
######################################################################################################################
from common.io.writeToa import readToa
import numpy as np
import pandas as pd


#Check for all bands that the differences with respect to the output TOA (ism_toa_) are <0.01% for at least 3-sigma of the points.

bands = ['VNIR-0','VNIR-1','VNIR-2','VNIR-3']
# Load the data
outdir_student_ism_toa = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-ISM\\my_output_ism"
outdir_lucia = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-ISM\\output"

prefix = 'ism_toa_'

# Compute the 3-sigma
for band in bands:

    print("-------------------------------------")
    print(" -- " + prefix + band + " comparation")

    lucia_toa = readToa(outdir_lucia, prefix + band + '.nc')
    my_toa = readToa(outdir_student_ism_toa, prefix + band + '.nc')

    # Compare
    result = my_toa - lucia_toa
    percentaje = result / my_toa * 100
    df = pd.DataFrame(percentaje)
    percentaje_df = df.fillna(0)  # Replace NaNs from division by zero with 0

    # Boolean comparison matrix for values within the 0.01% threshold
    boolean_comparison = np.array(percentaje_df < 0.01)

    # Total values and matching values
    total_values = boolean_comparison.size
    matching_values = np.sum(boolean_comparison)

    # Threshold for 99.7% (3-sigma) matching values
    threshold = 0.997 * total_values
    is_3sigma = matching_values >= threshold

    # Print the results
    if is_3sigma:
        print(
            f" -- The matrices difference is within the 0.01% for 3-Sigma of the points for the output TOA ({prefix + band})")
    else:
        print(
            f" -- WARNING: The matrices difference is outside of the 0.01% for 3-Sigma of the points for the output TOA ({prefix + band})")



    # For all bands, check whether there are any saturated pixels. Quantify the percentage of saturated
    # pixels per band.

    # Read final toa
    my_toa = readToa(outdir_student_ism_toa, prefix + band + '.nc')

    number_saturated_values = np.sum(my_toa == 4095)
    porcentaje_saturated = number_saturated_values * 100 / my_toa.size
    print("The percentage of saturated values for", prefix + band,"is", "{:.2f}".format(porcentaje_saturated), "%.")