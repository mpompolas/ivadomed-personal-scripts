# This script gathers the derivatives from the files/subjects that were used in the testing set
# It creates 3 folders (T1W, T2w, T2star) corresponding on which model they were used for
# Then the sct_deepseg will be used on each folder to create a evaluation_3Dmetrics within each folder for comparison with the newly created models


import os
import pandas as pd
from shutil import copyfile


BIDS_path = "/home/nas/Consulting/ivado-project/Datasets/sct-testing-large"

output_Folder = "/home/nas/PycharmProjects/ivadomed-personal-scripts/ResultsNewModel"



suffix = '_seg-manual'






t1w_results_file    = '/home/nas/PycharmProjects/ivadomed-personal-scripts/ResultsNewModel/evaluation_3Dmetrics_T1w.csv'
t2w_results_file    = '/home/nas/PycharmProjects/ivadomed-personal-scripts/ResultsNewModel/evaluation_3Dmetrics_T2w.csv'
t2star_results_file = '/home/nas/PycharmProjects/ivadomed-personal-scripts/ResultsNewModel/evaluation_3Dmetrics_T2star.csv'

t1w_results    = pd.read_csv(t1w_results_file)
t2w_results    = pd.read_csv(t2w_results_file)
t2star_results = pd.read_csv(t2star_results_file)

# Get the subjectID in a list
t1w_subjects    = [x.replace("_T1w", "") for x in t1w_results["image_id"].to_list()]
t2w_subjects    = [x.replace("_T2w", "") for x in t2w_results["image_id"].to_list()]
t2star_subjects = [x.replace("_T2star", "") for x in t2star_results["image_id"].to_list()]

modalities = ["T1w", "T2w", "T2star"]
all_subject_modalities = [t1w_subjects, t2w_subjects, t2star_subjects]


files_to_run_sct_deepseg_on = []
gt_to_run_dice_score_with = []
all_contrasts_per_file = []

copy_files = 0
if copy_files:

    for i in range(len(modalities)):
        modality = modalities[i]
        modality_subjects = all_subject_modalities[i]

        for subject in modality_subjects:

            # Copy the files
            filename = subject + '_' + modality + '.nii.gz'
            if os.path.exists(os.path.join(BIDS_path, subject, 'anat', filename)):
                copyfile(os.path.join(BIDS_path, subject, 'anat', filename),
                         os.path.join(output_Folder, modality, filename))
                files_to_run_sct_deepseg_on.append(os.path.join(BIDS_path, subject, 'anat', filename))
                all_contrasts_per_file.append(modality[0:2].lower())

            # Copy the derivatives
            derivative_filename = subject + '_' + modality + suffix + '.nii.gz'
            if os.path.exists(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename)):
                copyfile(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename),
                         os.path.join(output_Folder, modality, "derivatives", derivative_filename))
                gt_to_run_dice_score_with.append(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename))



## Now run sct_deep_seg on each one
sct_deepseg_folder = os.path.join(output_Folder, 'sct_deepseg')

if not os.path.exists(sct_deepseg_folder):
    os.mkdir(sct_deepseg_folder)


sct_segmented_files_to_run_dice_scores_on = []

for i in range(len(files_to_run_sct_deepseg_on)):

    contrast = all_contrasts_per_file[i]
    FileFullPath = files_to_run_sct_deepseg_on[i]
    filename = os.path.basename(FileFullPath)
    filename = filename.replace(".nii.gz", "") + '_seg-sct.nii.gz'

    # Do the segmentation if not already done it before
    if not os.path.exists(os.path.join(sct_deepseg_folder, filename)):
        os.system('/home/nas/PycharmProjects/spinalcordtoolbox/bin/sct_deepseg_sc -i ' + FileFullPath
                  + " -c " + contrast.lower() + " -o " + os.path.join(sct_deepseg_folder, filename))
    sct_segmented_files_to_run_dice_scores_on.append(os.path.join(sct_deepseg_folder, filename))
