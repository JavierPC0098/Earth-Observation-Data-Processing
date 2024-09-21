#
# Code developed by Javier Palacios Calatayud
# Master in Space Engineering (MiSE) - UC3M
# Earth Observation Data Processing
# Laboratory 1 - L1B
######################################################################################################################
from common.io.writeToa import readToa
from common.plot.plotF import plotF
import matplotlib.pyplot as plt
import numpy as np

# Variable Definition
eodp_toa_tolerance = 0.01 # in %
eodp_l1b_toa_VNIR= ['l1b_toa_VNIR-0.nc', 'l1b_toa_VNIR-1.nc', 'l1b_toa_VNIR-2.nc', 'l1b_toa_VNIR-3.nc']
eodp_l1b_toa_VNIR_isfr= ['ism_toa_isrf_VNIR-0.nc', 'ism_toa_isrf_VNIR-1.nc', 'ism_toa_isrf_VNIR-2.nc', 'ism_toa_isrf_VNIR-3.nc']

# Load the data
indir = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1B\\input"
outdir_student = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1B\\myoutputs"
outdir_lucia = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1B\\output"
outdir_isfr = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1B\\input"

# Functions Definition
def data_saver(address_dir, file_name_list):
    toa_list = []
    for toa_file_count, toa_file_name in enumerate(file_name_list):
        toa_list.append(readToa(address_dir, file_name_list[toa_file_count]))
    return toa_list

def sigma3_toa_diff(toa_files_lucia, toa_files_student, toa_tolerance):
    counter_in_sigma = 0
    counter_out_sigma = 0

    # Compute the 3-sigma of the point value
    total_points = toa_files_lucia[0].shape[0] * toa_files_lucia[0].shape[1]
    sigma3_points = np.ceil(0.997 * total_points)

    for toa_elements in range(len(toa_files_student)):
        # Compute the relative difference in %
        toa_rel_difference = np.absolute(toa_files_lucia[toa_elements] - toa_files_student[toa_elements]) / toa_files_lucia[toa_elements]

        # check how many elements are within the 3-sigma
        # Loop through all elements in the matrix
        for matrix_element in np.nditer(toa_rel_difference):
            if matrix_element < toa_tolerance:
                # You are in inside 3-sigma
                counter_in_sigma = counter_in_sigma + 1
            else:
                # You are outside 3-sigma
                counter_out_sigma = counter_out_sigma + 1

            # Check for the 3-sigma condition
            if counter_in_sigma >= sigma3_points:
                print(" - The matrices difference is withing the 0.01% for 3-Sigma of the points")
                break
            elif counter_out_sigma >= total_points - sigma3_points:
                print(" - WARNING: The matrices difference is outside of the 0.01% for 3-Sigma of the points")
                break

def alt_toa_extractor(toa_files):
    toa_alt_row_list = []
    for toa_element in range(len(toa_files)):
        mean_row = int(np.ceil(toa_files[toa_element].shape[0] / 2))
        toa_alt_row_list.append(toa_files[toa_element][mean_row])
    return toa_alt_row_list

def toa_plot_comparator(toa_alt_row_student_list, toa_alt_row_isfr_list, label_1, label_2, x_axis, y_axis, title):
    for toa_element in range(len(eodp_toa_alt_row_student_list)):
        y_1 = toa_alt_row_student_list[toa_element]
        y_2 = toa_alt_row_isfr_list[toa_element]
        x_1 = np.linspace(0, y_1.shape[0], y_1.shape[0])  # X values from 0 to 150
        x_2 = np.linspace(0, y_2.shape[0], y_2.shape[0])  # X values from 0 to 150
        # Create a plot
        plt.figure(figsize=(10, 5))
        # Plot the arrays
        plt.plot(x_1, y_1, label=label_1, color='blue')
        plt.plot(x_2, y_2, label=label_2, color='orange')

        # Plot characteristics
        plt.xlabel(x_axis)
        plt.ylabel(y_axis)
        plt.title(f"{title} Case: {toa_element + 1}")
        plt.legend()
        plt.grid()
    plt.show()

#####################################################################################################################
# Exercise 1
# Check for all bands that the differences with respect to the output TOA (l1b_toa_) are <0.01% for at
# least 3-sigma of the points.
# Load of the data
eodp_toa_files_student = np.array(data_saver(outdir_student, eodp_l1b_toa_VNIR))
eodp_toa_files_lucia = np.array(data_saver(outdir_lucia, eodp_l1b_toa_VNIR))

# Compute the 3-sigma
sigma3_toa_diff(eodp_toa_files_student, eodp_toa_files_lucia, eodp_toa_tolerance)

#####################################################################################################################
# Exercise 2
#  For the central ALT position, plot the restored signal (l1b_toa), and the TOA after the ISRF
# (ism_toa_isrf). Explain the differences.
eodp_toa_files_isfr = np.array(data_saver(outdir_isfr, eodp_l1b_toa_VNIR_isfr))

eodp_toa_alt_row_student_list = alt_toa_extractor(eodp_toa_files_student)
eodp_toa_alt_row_isfr_list = alt_toa_extractor(eodp_toa_files_isfr)

toa_plot_comparator(eodp_toa_alt_row_student_list, eodp_toa_alt_row_isfr_list,
                    'ALT TOA (Student)', 'ALT TOA (ISFR)',
                    'ACT pixel [-]', 'TOA [mW/m2/sr]',
                    'Effects of TOA with and without ISFR.')

#####################################################################################################################
# Exercise 3
#  Do another run of the L1B with the equalization enabled to false. Plot the restored signal for this case
# and for the case with the equalization set to True. Compare.


