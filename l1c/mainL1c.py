
# MAIN FUNCTION TO CALL THE L1C MODULE

from l1c.src.l1c import l1c

# Directory - this is the common directory for the execution of the E2E, all modules
auxdir = r'C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\Assignment\\auxiliary'
# GM dir + L1B dir
indir = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1C\\input"
outdir = r"C:\\Users\\pc\\Desktop\\Earth_Observation_Data_Processing\\EODP_TER_2021\\EODP-TS-L1C\\myoutputs"

# Initialise the ISM
myL1c = l1c(auxdir, indir, outdir)
myL1c.processModule()
