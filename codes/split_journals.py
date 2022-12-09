import pandas as pd
import numpy as np


'''
Coauthorship Network Project
Author: Eunseo Sung

Split list of journals into 10 for faster cleanup

Input: [year]_all_journal_unfiltered.csv
Output: [year]_split_journals (directory)
'''


def main(path):
    df_all = pd.read_csv(path)
    split_dfs = np.array_split(df_all, 10)
    for i in range(len(split_dfs)):
        split_dfs[i].to_csv("2017_split_journals/2017_journals_" + str(i) + ".csv")


if __name__ == "__main__":
    main("2017_all_journal_unfiltered.csv")
