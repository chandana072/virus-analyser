


import pandas as pd
# Make sure NewD90.py is in the same directory or same folder
from NewD90 import ssRNA  

#path to the data file
file_path = "/Users/prasiddha_10/documents/python_virus/backend/mayarog.txt"

# Load the data
data_s = pd.read_table(file_path, header=None, names=["BaseCount"])

# Calculate GSize based on the total length of all sequences
# If the length is based on the first sequence, this can be adjusted as needed

GSize = len(data_s['BaseCount'].values[0])


# Run the function from the imported module
result = ssRNA(data_s, GSize)

# Output the result

"""
D90 values:
dengueg.txt = 33.578515
aichig.txt = 256.7488
mayarog.txt = 40.753289
"""

print("D90 Calculation Result:", result)

