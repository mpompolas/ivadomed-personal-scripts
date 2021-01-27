# This script gathers the derivatives from the files/subjects that were used in the testing set
# Then the sct_deepseg will be used on each folder to create a evaluation_3Dmetrics within each folder for
# comparison with the newly created models


import os
import pandas as pd
from shutil import copyfile


# Consider generalizing to have only the logs folder as the input

BIDS_path = "/home/nas/Consulting/ivado-project/Datasets/sct-testing-large"

output_Folder = "/home/nas/PycharmProjects/ivadomed-personal-scripts/ResultsNewModel"

suffix = '_seg-manual'





# These are the scores that each new model achieved
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

all_subject_modalities = [t1w_subjects, t2w_subjects, t2star_subjects]


## CREATE NECESSARY FOLDERS
modalities = ["T1w", "T2w", "T2star"]

for modality in modalities:
    if not os.path.exists(os.path.join(output_Folder, modality)):
        os.mkdir(os.path.join(output_Folder, modality))
        os.mkdir(os.path.join(output_Folder, modality, "derivatives"))



## COPY FILES WITHIN THE APPROPRIATE FOLDERS - THIS STEP SHOULD ULTIMATELY BE SKIPPED AND JUST COLLECT A LIST OF THE FILES

files_to_run_sct_deepseg_on = []
gt_to_run_dice_score_T1w = []
gt_to_run_dice_score_T2w = []
gt_to_run_dice_score_T2s = []
contrast_on_file = []

copy_files = 1
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
                contrast_on_file.append(modality[0:3].lower())

            # Copy the derivatives
            derivative_filename = subject + '_' + modality + suffix + '.nii.gz'
            if os.path.exists(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename)):
                copyfile(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename),
                         os.path.join(output_Folder, modality, "derivatives", derivative_filename))

                if modality == "T1w":
                    gt_to_run_dice_score_T1w.append(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename))
                elif modality == "T2w":
                    gt_to_run_dice_score_T2w.append(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename))
                elif modality == "T2star":
                    gt_to_run_dice_score_T2s.append(os.path.join(BIDS_path, 'derivatives', 'labels', subject, 'anat', derivative_filename))


########################################################################################################################
## Now run sct_deep_seg_sc on each file - already computed segmentations will be skipped

sct_deepseg_folder = os.path.join(output_Folder, 'sct_deepseg')

if not os.path.exists(sct_deepseg_folder):
    os.mkdir(sct_deepseg_folder)

sct_segmented_files_to_run_dice_scores_on = []


run_segmentation = 0
if run_segmentation:
    for i in range(len(files_to_run_sct_deepseg_on)):

        contrast = contrast_on_file[i]
        FileFullPath = files_to_run_sct_deepseg_on[i]
        filename = os.path.basename(FileFullPath)
        filename = filename.replace(".nii.gz", "") + '_seg-sct.nii.gz'

        # Do the segmentation if not already done it before
        if not os.path.exists(os.path.join(sct_deepseg_folder, filename)):
            os.system('/home/nas/PycharmProjects/spinalcordtoolbox/bin/sct_deepseg_sc -i ' + FileFullPath
                      + " -c " + contrast.lower() + " -o " + os.path.join(sct_deepseg_folder, filename))
        else:
            print('Already segmented: ' + os.path.join(sct_deepseg_folder, filename))
        sct_segmented_files_to_run_dice_scores_on.append(os.path.join(sct_deepseg_folder, filename))



## Now compute the dice_scores between the sct-segmentation and the ground-truth
# and collect the values in a .csv file
all_gt_to_run_dice_scores = [gt_to_run_dice_score_T1w, gt_to_run_dice_score_T2w, gt_to_run_dice_score_T2s]


for iModality in range(len(all_gt_to_run_dice_scores)):
    subject_labels = []
    diceScores = []

    single_modality_gts = all_gt_to_run_dice_scores[iModality]
    for File in single_modality_gts:

        basename = os.path.basename(File.replace(suffix + ".nii.gz", ""))

        sct_file_fullpath = os.path.join(output_Folder, "sct_deepseg", basename + "_seg-sct.nii.gz")

        if os.path.exists(sct_file_fullpath):
            diceScoreFile = os.path.join(output_Folder, "dice_score.txt")

            os.system("/home/nas/PycharmProjects/spinalcordtoolbox/bin/sct_dice_coefficient -i " + File + " -d " +
                      sct_file_fullpath + " -o " + diceScoreFile)

            with open(diceScoreFile) as f:
                text = f.read()
                try:
                    diceScore = float(text.replace('3D Dice coefficient = ', ''))
                except:
                    diceScore = 0


            # Append results
            subject_labels.append(basename)
            diceScores.append(diceScore)


    # Export all results to a .csv file
    df = pd.DataFrame({'image_id': subject_labels,
                       'dice_class0': diceScores})
    df.to_csv(os.path.join(output_Folder, modalities[iModality], 'evaluation_3Dmetrics.csv'))