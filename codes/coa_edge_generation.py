import numpy as np
import pandas as pd
import sys, getopt
import itertools
import copy

'''
Coauthorship Network Project
Author: Eunseo Sung

Creating edge list and author list from dataframe of papers (contains cleaned author info)

Input: [year]_split_journals_clean (directory)
Output: [year]_author_list.csv
        [year]_edge_list.csv
'''


# Input: dataframe of all paper info 
#   pub_year  pub_month  journal_name  paper_title  author
# Count number of papers for each author
# Remove any edges with authors < 2 papers
# Output: Dataframe with all paper edges
def get_edges(comb_df):
    # Dict with format: {author : [num_papers, [journals], [papers]]}
    authors_dict = dict()
    # Dict with format: {(a1, a2):[weight, [journals], [papers]]}
    edges_dict = dict()
    # Loop over every paper in df
    for index, row in comb_df.iterrows():
        authors = row['author'].split(",")
        # Get list of all pairwise author combinations
        edges = list(itertools.combinations(authors, 2))
        # For every pair(edge) save count(weight), journals, and paper titles
        for e in edges:
            if tuple(e) not in edges_dict:
                if e[::-1] not in edges_dict:
                    edges_dict[tuple(e)] = [0, [], []]
                else:
                    e = e[::-1]
            (edges_dict[tuple(e)])[0] += 1
            (edges_dict[tuple(e)])[1].append(row['journal_name'])
            (edges_dict[tuple(e)])[2].append(row['paper_title'])
        # For every individual author, save count, journals, and paper titles
        for a in authors:
            if a not in authors_dict:
                authors_dict[a] = [0, [], []]
            (authors_dict[a])[0] += 1
            (authors_dict[a])[1].append(row['journal_name'])
            (authors_dict[a])[2].append(row['paper_title'])
    
    # Make edge list into rowwise list for edge dataframe
    edges_final = []
    for a_pair in edges_dict:
        edge_entry = [a_pair[0], a_pair[1], (edges_dict[a_pair])[0]]
        edge_entry.append(",".join((edges_dict[a_pair])[1]))
        edge_entry.append(",".join((edges_dict[a_pair])[2]))
        edges_final.append(edge_entry)
    edge_df = pd.DataFrame(edges_final, columns = ['author1', 'author2', 'weight', 'journals', 'papers'])

    authors_dict_clean = copy.deepcopy(authors_dict)

    # Make author list into rowwise list for authors dataframe
    authors_final = []
    for a in authors_dict_clean:
        authors_entry = [a, (authors_dict_clean[a])[0]]
        authors_entry.append(",".join((authors_dict_clean[a])[1]))
        authors_entry.append(",".join((authors_dict_clean[a])[2]))
        authors_final.append(authors_entry)    
    authors_df = pd.DataFrame(authors_final, columns = ['author', 'count', 'journals', 'papers'])
    
    return edge_df, authors_df


# Input: year
# Output: Combined df of split dfs with cleaned locations
def combine_journal_data(year):
    root_file = f"{year}_split_journals_clean/{year}_journals_clean_"
    journal_df_list = []
    for i in range(10):
        in_path = f"{root_file}{i}.csv"
        df = pd.read_csv(in_path, index_col = False)
        df.drop(df.columns[[0, 1]], axis = 1, inplace = True)
        journal_df_list.append(df)
    all_journals = pd.concat(journal_df_list)
    all_journals.drop(all_journals.columns[[0]], axis = 1, inplace = True)
    all_journals = all_journals.set_axis([i for i in range(all_journals.shape[0])], axis=0)
    return all_journals


def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv,"hy:",["year="])
    except getopt.GetoptError:
        print("test.py -y <year>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("test.py -y <year>")
            sys.exit()
        elif opt in ("-y", "--year"):
            year = arg
    return year


def main(argv):
    year = parse_args(argv)
    comb_df = combine_journal_data(year)
    edges_df, authors_df = get_edges(comb_df)
    edge_out_path = f"{year}_edge_list.csv"
    authors_out_path = f"{year}_author_list.csv"
    edges_df.to_csv(edge_out_path)
    authors_df.to_csv(authors_out_path)


if __name__ == "__main__":
    main(sys.argv[1:])