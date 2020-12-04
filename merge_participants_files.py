from bids_neuropoly import bids
import pandas as pd
import json
import os

# This scripts merges the participants.tsv and participants.json so 2 BIDS datasets can be merged and sequentially read by IVADOMED
# 3 fields should be added:
# 1. Folder of first dataset
# 2. Folder of second dataset
# 3. Folder where everything will be copied at

######################################################################################################################################################


# Directory where the merged participants.tsv will be saved
output_folder = '/home/nas/Desktop/'

# Input datasets to merge
datasetFolder1 = '/home/nas/Consulting/ivado-project/Datasets/Karolinska/'
datasetFolder2 = '/home/nas/Consulting/ivado-project/Datasets/data_example_spinegeneric/'


######################################################################################################################################################



print('The easiest way to merge some inconsistencies in the participants.tsv column names, is to change it straight from the file, not in here')


# Load and merge the .tsv files
df1 = bids.BIDS(datasetFolder1).participants.content
df2 = bids.BIDS(datasetFolder2).participants.content

# Merge the tsv files and save them a new file
df_merged = pd.merge(left=df1, right=df2, how='outer')
df_merged.to_csv(os.path.join(output_folder, 'participants.tsv'), sep='\t', index=False)


# Do the same for the .json files
jsonFile1 = os.path.join(datasetFolder1, 'participants.json')
jsonFile2 = os.path.join(datasetFolder2, 'participants.json')

with open(jsonFile1) as json_file:
    json1 = json.load(json_file)
with open(jsonFile2) as json_file:
    json2 = json.load(json_file)

# Merge files
json_merged = {**json1, **json2}

with open(os.path.join(output_folder, 'participants.json'), 'w') as outfile:
    json.dump(json_merged, outfile, indent=4)



