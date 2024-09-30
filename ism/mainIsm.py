
# MAIN FUNCTION TO CALL THE ISM MODULE

from ism.src.ism import ism

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\Assignment\\auxiliary'
indir = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-ISM\\input\\gradient_alt100_act150"
outdir = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-ISM\\my_output_ism"

# Initialise the ISM
myIsm = ism(auxdir, indir, outdir)
myIsm.processModule()