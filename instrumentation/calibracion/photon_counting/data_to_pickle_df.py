import os
import numpy as np
import pandas as pd

# Directory where the .npy files are located
directory = "/home/tdinapoli/Documents/personales/facultad/tesis/git/data/rodamina/med1"

# Get a list of all .npy files in the directory
npy_files = [f for f in os.listdir(directory) if f.endswith(".npy")]

# Initialize a dictionary to store the data
data_dict = {}

# Iterate through the .npy files and extract the data
for npy_file in npy_files:
    # Extract the integration time and measurement number from the filename
    file_parts = npy_file.split("_")
    integration_time = float(file_parts[0])
    measurement_number = int(file_parts[1].split(".")[0])
    
    # Load the data from the .npy file
    data = np.load(os.path.join(directory, npy_file))
    
    # Store the data in the dictionary
    data_dict.setdefault(integration_time, {})[measurement_number] = data

# Create a DataFrame from the dictionary
df = pd.DataFrame(data_dict)

# Optionally, you can transpose the DataFrame to have integration times as rows
df = df.transpose().sort_index(ascending=True).sort_index(axis=1, ascending=True)

# Display the resulting DataFrame
print(df)
df.to_pickle(f"{directory}/data.pickle")