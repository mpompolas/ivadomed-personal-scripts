from distutils.dir_util import copy_tree
from bids_neuropoly import bids
import pandas as pd
import json
import glob
import os

# This scripts merges the participants.tsv and participants.json so 2 BIDS datasets can be merged and sequentially read by IVADOMED
# 4 Inputs should be added:
# 1. Folder of first dataset
# 2. Folder of second dataset
# 3. Folder where everything will be copied at
# 4. Flag to copy or not the subjects-subfolders

######################################################################################################################################################

# Directory where the merged participants.tsv will be saved
output_folder = '/home/nas/Desktop/merging_playground/mergedDataset/'

# Input datasets to merge
datasetFolder1 = '/home/nas/Desktop/merging_playground/first_Dataset/'
datasetFolder2 = '/home/nas/Desktop/merging_playground/second_Dataset/'
copySubjectsFolders = True

######################################################################################################################################################


print('The easiest way to merge some inconsistencies in the participants.tsv column names, is to change it straight from the file, not in here')

# Create output folder if it doesnt exist
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

# Load the .tsv files
df1 = bids.BIDS(datasetFolder1).participants.content
df2 = bids.BIDS(datasetFolder2).participants.content

# Merge the .tsv files and save them in a new file (This keeps also non-overlapping fields)
df_merged = pd.merge(left=df1, right=df2, how='outer')
df_merged.to_csv(os.path.join(output_folder, 'participants.tsv'), sep='\t', index=False)


# Do the same for the .json files
jsonFile1 = os.path.join(datasetFolder1, 'participants.json')
jsonFile2 = os.path.join(datasetFolder2, 'participants.json')

with open(jsonFile1) as json_file:
    json1 = json.load(json_file)
with open(jsonFile2) as json_file:
    json2 = json.load(json_file)

# Merge .json files
json_merged = {**json1, **json2}

with open(os.path.join(output_folder, 'participants.json'), 'w') as outfile:
    json.dump(json_merged, outfile, indent=4)


# Create a dataset_decription.json -  This is needed on the BIDS loader
with open(os.path.join(output_folder, 'dataset_description.json'), 'w') as outfile:
    json.dump({"BIDSVersion": "1.0.1", "Name": "SCT_testing"}, outfile, indent=4) # Confirm the version is correct


all_datasets = [datasetFolder1, datasetFolder2]
if copySubjectsFolders:
    for datasetFolder in all_datasets:
        subjectsFolders = glob.glob(os.path.join(datasetFolder, 'sub-*'))
        derivativesFolder = glob.glob(os.path.join(datasetFolder, 'derivatives'))

        if derivativesFolder!=[]:
            foldersToCopy = subjectsFolders.append(derivativesFolder)
            print("No derivatives are present in this folder")
        else:
            foldersToCopy = subjectsFolders

        for subFolder in foldersToCopy:
            copy_tree(subFolder, os.path.join(output_folder, os.path.basename(os.path.normpath(subFolder))))
