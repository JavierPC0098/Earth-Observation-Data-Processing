#
# Code developed by Javier Palacios Calatayud
# Master in Space Engineering (MiSE) - UC3M
# Earth Observation Data Processing
# Laboratory 2 - ISM
######################################################################################################################
from common.io.writeToa import readToa
from common.io.readMat import readMat
import numpy as np
import pandas as pd
from netCDF4 import Dataset
import os
import sys
from common.io.mkdirOutputdir import mkdirOutputdir

# Variable Definition
eodp_toa_tolerance = 0.01 # in %
eodp_ism_toa_isrf_VNIR= ['ism_toa_isrf_VNIR-0.nc', 'ism_toa_isrf_VNIR-1.nc', 'ism_toa_isrf_VNIR-2.nc', 'ism_toa_isrf_VNIR-3.nc']
eodp_ism_toa_optical_VNIR= ['ism_toa_optical_VNIR-0.nc', 'ism_toa_optical_VNIR-1.nc', 'ism_toa_optical_VNIR-2.nc', 'ism_toa_optical_VNIR-3.nc']

# Load the data
outdir_student_ism_toa_isfr_optical = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-ISM\\my_output_ism"
outdir_lucia = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-ISM\\output"

def readArray(directory, filename):
    ncfile = os.path.join(directory, filename)
    if not os.path.isfile(ncfile):
        sys.exit('File not found ' + ncfile + ". Exiting.")
    print('Reading ' + ncfile)

    # Load dataset
    dset = Dataset(ncfile)

    # Extract data from NetCDF file
    array = np.array(dset.variables['array'][:])
    dset.close()
    print('Size of matrix ' + str(array.shape))

    return array

#####################################################################################################################
# Exercise 1
# Check for all bands that the differences with respect to the output TOA (l1b_toa_) are <0.01% for at least 3-sigma of the points.

bands = ["VNIR-0", "VNIR-1", "VNIR-2", "VNIR-3"]
prefixes = ["ism_toa_isrf_", "ism_toa_optical_"]  # List of prefixes to iterate over

# Compute the 3-sigma
for prefix in prefixes:
    for band in bands:

        print("-------------------------------------")
        print(" -- " + prefix + band + " comparation")

        lucia_toa = readToa(outdir_lucia, prefix + band + '.nc')
        my_toa = readToa(outdir_student_ism_toa_isfr_optical, prefix + band + '.nc')

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



# Plot for all bands the System MTF across and along track (for the central pixels). Report the MTF at
# the Nyquist frequency. Explain whether this is a decent or mediocre value and why
# Define the prefixes
prefixes = ['Hdiff_', 'Hdefoc_', 'Hwfe_', 'Hdet_', 'Hsmear_', 'Hmotion_', 'Hsys_']
arrays = ['fnAct_', 'fnAlt_']

# Dictionary to store results for each band
results = {}

# Loop over each band
for band in bands:
    # Create a nested dictionary to store matrices, arrays, and computed values for the current band
    band_results = {}

    # Read matrices and store in the nested dictionary
    for prefix in prefixes:
        # Read matrix for the current prefix and band
        matrix = readMat(outdir_student_ism_toa_isfr_optical, prefix + band + '.nc')
        band_results[prefix] = matrix

        # Compute nlines_ALT, ACT_central_line, nlines_ACT, and ALT_central_line for the matrix
        nlines_ALT = matrix.shape[0]
        ACT_central_line = int(nlines_ALT / 2)
        nlines_ACT = matrix.shape[1]
        ALT_central_line = int(nlines_ACT / 2)

        # Store computed values in the results dictionary for this prefix
        band_results[f"{prefix}_nlines_ALT"] = nlines_ALT
        band_results[f"{prefix}_ACT_central_line"] = ACT_central_line
        band_results[f"{prefix}_nlines_ACT"] = nlines_ACT
        band_results[f"{prefix}_ALT_central_line"] = ALT_central_line

    # Read arrays and store in the nested dictionary
    for array in arrays:
        band_results[array] = readArray(outdir_student_ism_toa_isfr_optical, array + band + '.nc')

    # Store the results for this band in the main results dictionary
    results[band] = band_results

import matplotlib.pyplot as plt
import numpy as np

# Loop over each band in the bands list
for band in bands:
    # Retrieve the necessary data from the results dictionary
    fnAct = results[band]['fnAct_']
    fnAlt = results[band]['fnAlt_']

    Hdiff = results[band]['Hdiff_']
    Hdefoc = results[band]['Hdefoc_']
    Hwfe = results[band]['Hwfe_']
    Hdet = results[band]['Hdet_']
    Hsmear = results[band]['Hsmear_']
    Hmotion = results[band]['Hmotion_']
    Hsys = results[band]['Hsys_']

    ACT_central_line = results[band]['Hdiff__ACT_central_line']
    ALT_central_line = results[band]['Hdiff__ALT_central_line']

    # Plot for the ACT slice
    plt.plot(fnAct[75:150], Hdiff[ACT_central_line, 75:150], label='Diffraction MTF')
    plt.plot(fnAct[75:150], Hdefoc[ACT_central_line, 75:150], label='Defocus MTF')
    plt.plot(fnAct[75:150], Hwfe[ACT_central_line, 75:150], label='WFE Aberration MTF')
    plt.plot(fnAct[75:150], Hdet[ACT_central_line, 75:150], label='Detector MTF')
    plt.plot(fnAct[75:150], Hsmear[ACT_central_line, 75:150], label='Smearing MTF')
    plt.plot(fnAct[75:150], Hmotion[ACT_central_line, 75:150], label='Motion blur MTF')
    plt.plot(fnAct[75:150], Hsys[ACT_central_line, 75:150], color='black', linewidth=2.5, label='System MTF')
    plt.plot(np.full(2, 0.5), np.linspace(0, 1, 2), linestyle='--', color='black', label='f Nyquist')

    plt.xlabel('Spatial frequencies f/(1/w) [-]')
    plt.ylabel('MTF')
    plt.title("System MTF, slice ACT for " + band + " (for the central pixels of ALT)")
    plt.legend()
    plt.xlim(-0.025, 0.525)
    plt.ylim(-0.025, 1.025)
    plt.savefig("ism_plot_MTF_ACT_" + band + ".png")
    plt.show()

    # Plot for the ALT slice
    plt.plot(fnAlt[50:100], Hdiff[50:100, ALT_central_line], label='Diffraction MTF')
    plt.plot(fnAlt[50:100], Hdefoc[50:100, ALT_central_line], label='Defocus MTF')
    plt.plot(fnAlt[50:100], Hwfe[50:100, ALT_central_line], label='WFE Aberration MTF')
    plt.plot(fnAlt[50:100], Hdet[50:100, ALT_central_line], label='Detector MTF')
    plt.plot(fnAlt[50:100], Hsmear[50:100, ALT_central_line], label='Smearing MTF')
    plt.plot(fnAlt[50:100], Hmotion[50:100, ALT_central_line], label='Motion blur MTF')
    plt.plot(fnAlt[50:100], Hsys[50:100, ALT_central_line], color='black', linewidth=2.5, label='System MTF')
    plt.plot(np.full(2, 0.5), np.linspace(0, 1, 2), linestyle='--', color='black', label='f Nyquist')

    plt.xlabel('Spatial frequencies f/(1/w) [-]')
    plt.ylabel('MTF')
    plt.title("System MTF, slice ALT for " + band + " (for the central pixels of ACT)")
    plt.legend()
    plt.xlim(-0.025, 0.525)
    plt.ylim(-0.025, 1.025)
    plt.savefig("ism_plot_MTF_ALT_" + band + ".png")
    plt.show()
