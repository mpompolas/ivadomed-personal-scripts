
import pandas as pd
import joblib
import numpy as np
from bids_neuropoly import bids


# First load the used dataset list
subjectsUsedFile = '/home/nas/Desktop/dataset-training-sct.pkl' # train_valid_test: 1 for training, 2 for validating, 3 for testing

# Output file
outputFile = '/home/nas/Consulting/ivado-project/Datasets/merged_SCTLARGE_MULTISUBJECT/split_datasets_converted.joblib'




dataUsedOnSct = pd.read_pickle(subjectsUsedFile)

subjectsUsedForTesting = dataUsedOnSct[dataUsedOnSct['train_valid_test'] == 3]['subject'].to_list() # THESE WILL FOR SURE BE USED IN THE TESTING SET, NOT IN THE OTHER TWO




# Load the merged participants.tsv
merged_folder = '/home/nas/Consulting/ivado-project/Datasets/merged_SCTLARGE_MULTISUBJECT/'
df_merged = bids.BIDS(merged_folder).participants.content

# NOW SHUFFLE AVAILABLE SUBJECTS AND MAKE SURE THERE ARE NO SUBJECTS FROM THE SCT_TESTING IN THE TRAINING AND VALIDATION LISTS
percentage_train = 0.6
percentage_validation = 0.2

# Whatever was used in sct testing, will stay in the testing side of the joblib as well
test = df_merged[np.in1d(df_merged['data_id'], subjectsUsedForTesting)]
# Keep only the rest of the subjects for splitting to training/validation/testing sets
df_merged_reduced = df_merged[np.invert(np.in1d(df_merged['data_id'], subjectsUsedForTesting))]


train, validate, test2 = np.split(df_merged_reduced.sample(frac=1), [int(percentage_train*(len(df_merged_reduced)+len(test)/2)), int((percentage_train+percentage_validation)*len(df_merged_reduced)+len(test)/2)])
# Append the testing from sct to the new testing entries
test3 = test.append(test2, ignore_index=1)



# Populate the joblib file
jobdict = {'train': train['participant_id'].to_list(), 'valid': validate['participant_id'].to_list(), 'test': test3['participant_id'].to_list()}


#exampleJobLib = joblib.load('/home/nas/Desktop/logs/logs_NO_FILM_Karo/split_datasets.joblib')
joblib.dump(jobdict, outputFile)
#pd.to_pickle(jobdict, outputFile)
#reReadDumpedJoblib = joblib.load(outputFile)


print('Success')
