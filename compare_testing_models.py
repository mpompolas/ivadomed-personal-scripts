import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
import itertools
import seaborn as sns
from scipy.stats import ks_2samp


logFoldersToCompare = ['/home/nas/Desktop/logs/logs_NO_FILM_Karo/', '/home/nas/Desktop/logs/logs_NO_FILM_sctUsers/', '/home/nas/Desktop/logs/logs_onlyT1w']

if len(logFoldersToCompare)<2:
    print('Less than two folders were selected - Nothing to compare')
    STOP

columnNames = ["Folder", 'dice_class0']
df = pd.DataFrame([], columns=columnNames)

for folder in logFoldersToCompare:
    result = pd.read_csv(os.path.join(folder, 'results_eval', 'evaluation_3Dmetrics.csv'))
    diceScores = result['dice_class0']
    folders = [os.path.basename(os.path.normpath(folder))]*len(diceScores)
    combined = np.column_stack((folders, diceScores.astype(np.object, folders))).T
    singleFolderDF = pd.DataFrame(combined, columnNames).T
    df = df.append(singleFolderDF, ignore_index=True)


nFolders = len(logFoldersToCompare)
combinedNumbers = list(itertools.combinations(range(nFolders), 2))
combinedFolders = list(itertools.combinations(logFoldersToCompare, 2))


# Pandas annoying issues
df['dice_class0'] = df['dice_class0'].astype('float64')


# Plot all violinplots
sns.violinplot(x="Folder", y="dice_class0", data=df, color="0.8", inner='quartile')
sns.stripplot(x="Folder", y="dice_class0", data=df, jitter=True, zorder=1)


# Perform a Kolmogorov-Smirnoff test for every every combination of results
for i in range(len(combinedNumbers)):
    dataX = df['dice_class0'][df['Folder'] == os.path.basename(os.path.normpath(combinedFolders[i][0]))]
    dataY = df['dice_class0'][df['Folder'] == os.path.basename(os.path.normpath(combinedFolders[i][1]))]

    temp = df['dice_class0'][df['Folder'] == os.path.basename(os.path.normpath(logFoldersToCompare[i]))]

    KStest = ks_2samp(dataX, dataY)
    print(KStest.pvalue)
    print(combinedFolders[i])

    x1, x2 = combinedNumbers[i]

    y, h, col = df['dice_class0'].min() - 0.06 - 0.03*i, -0.01, 'k'
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
    plt.text(i, df['dice_class0'].max()+0.07, str((100*temp.mean()).round()/100), ha='center', va='top', color='r')

    if KStest.pvalue>=0.5:
        plt.text((x1+x2)*.5, y+h, "ns", ha='center', va='bottom', color=col)
    elif KStest.pvalue<0.5 and KStest.pvalue>=0.01:
        plt.text((x1+x2)*.5, y+h, "*", ha='center', va='bottom', color=col)
    elif KStest.pvalue<0.01 and KStest.pvalue:
        plt.text((x1+x2)*.5, y+h, "***", ha='center', va='bottom', color=col)

plt.grid()
plt.show()


print('success')




