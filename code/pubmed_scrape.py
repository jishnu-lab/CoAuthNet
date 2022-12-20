import numpy as np
import sys, getopt
import pandas as pd
import re
from Bio import Entrez
import scipy.sparse as sparse


'''
Coauthorship Network Project
Author: Eunseo Sung

Pubmed Scrape code (using Bio Entrez package)
https://biopython.org/docs/1.76/api/Bio.Entrez.html

Input: final_journals.txt
Output: [year]_all_journal_unfiltered.csv

Command Line: pubmed_scrape.py -y <year>
'''


# Creates Entrez search query in appropriate format
# Input: search query, range of dates, search start and end index
# Output: Entrez search query
def search(query, min_date, max_date, ret_start, ret_max):
    Entrez.email = 'anyemailaddress@gmail.com'
    handle = Entrez.esearch(db='pubmed',
                            sort ='Pub Date',
                            datetype = "PDAT", 
                            mindate = min_date,
                            maxdate = max_date,
                            retstart = str(ret_start), 
                            retmax = str(ret_max),
                            retmode = 'xml',
                            term = query)
    results = Entrez.read(handle)
    return results


# Fetches list of paper ids with efetch function
# Input: Part of output from search function
# Output: Papers
def fetch_details(id_list):
    ids = ','.join(id_list)
    Entrez.email = 'anyemailaddress@gmail.com'
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results


# Takes whole paper data and extracts necessary metadata
# Input: search query, date range (min and max), starting and ending index of search
# Output: dataframe containing author info from search
def fetch_data(query, min_date, max_date, ret_start, ret_max):
    results = search(query, min_date, max_date, ret_start, ret_max)
    id_list = results['IdList']
    papers = fetch_details(id_list)
    record = Entrez.parse(papers)

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", \
        "Sep", "Oct", "Nov", "Dec"]

    paper_df = pd.DataFrame(columns = ["pub_year", "pub_month", \
            "journal_name", "paper_title", "author"])

    # Parsing paper metadata dictionary
    # If any data (title, journal name, publication year/month, authors missing, skip paper)
    for i,paper in enumerate(papers['PubmedArticle']):
        try:
            paper_title = (paper['MedlineCitation']['Article']['ArticleTitle'])[:-1]
        except:
            continue
        try:
            journal_name = paper['MedlineCitation']['Article']['Journal']['Title']
        except:
            continue
        try:
            pub_year = paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year']
        except:
            continue
        try:
            pub_month = paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month']
            if pub_month in months:
                pub_month = str(months.index(pub_month) + 1)
        except:
            continue

        # Get author affiliation info, clean author name strings
        author_info = []
        if ('AuthorList' in paper['MedlineCitation']['Article']):
            authors = paper['MedlineCitation']['Article']['AuthorList']
        else:
            continue
        for j in range(len(authors)):
            if (len(authors[j]['AffiliationInfo']) > 0):
                affiliation = authors[j]['AffiliationInfo'][0]['Affiliation']
            else:
                affiliation = None
            if ('LastName' in authors[j]) and ('ForeName' in authors[j]):
                last_name = re.sub('[^a-zA-Z0-9 \n\.]', '', authors[j]['LastName'])
                first_name = re.sub('[^a-zA-Z0-9 \n\.]', '', authors[j]['ForeName'])
            else:
                last_name = None
                first_name = None
            a_str = "$".join([str(first_name), str(last_name), str(affiliation)])
            author_info.append(a_str)

        paper_info = {"pub_year":pub_year, "pub_month":pub_month, \
                    "journal_name":journal_name, "paper_title":paper_title, \
                    "author":"#".join(author_info)}

        paper_df = paper_df.append(paper_info, ignore_index = True)
    return paper_df


# Call search in increments of ret_max papers
# Iteration i of loop returns papers of index i*ret_max to (i+1)*ret_max
def paper_loop(query, min_date, max_date, est_max, ret_max):
    total_df = pd.DataFrame(columns = ["pub_year", "pub_month", \
                "journal_name", "paper_title", "author"])
    num_loop = int(est_max / ret_max)
    start_i = 0
    for i in range(num_loop):
        print(i)
        try:
            paper_df = fetch_data(query, min_date, max_date, start_i, ret_max)
            total_df = total_df.append(paper_df, ignore_index = True)
            start_i += ret_max
        except:
            break
    return total_df


# Write final dataframe to output path
def combine_df(paths, dest_path):
    combined_df = pd.concat(paths)
    combined_df.to_csv(dest_path)
    return combined_df


# Create query string from list of journals
def get_queries(path):
    with open(path, "rt") as f:
        j_list_str = f.read()
    j_list = j_list_str.splitlines()
    j_list = [i for i in j_list if i]
    query_str = ""
    for i in range(len(j_list)):
        if i == (len(j_list) - 1):
            query_str += '\"' + j_list[i] + '\"' + "[journal]"
        else:
            query_str += '\"' + j_list[i] + '\"' + "[journal] OR "
    return query_str


def search_pubmed(queries, min_date, max_date, ret_max):
    max_count = 70000
    journal_dfs = []
    for query in queries:
        journal_dfs.append(paper_loop(query, min_date, max_date, max_count, ret_max))
    return journal_dfs    


def parse_args(argv):
    year = None
    try:
        opts, args = getopt.getopt(argv,"hy:",["help", "year="])
    except getopt.GetoptError:
        print("pubmed_scrape.py -y <year>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("pubmed_scrape.py -y <year>")
            sys.exit()
        elif opt in ("-y", "--year"):
            year = arg
        else:
            assert False, "unhandled option"
    if year == None:
        year = 2017
    return year


def main(argv, query_path):
    year = str(parse_args(argv))
    query_str = get_queries(query_path)
    save_path = f"{year}_all_journal_unfiltered.csv"
    min_date = f"{year}/01/01"
    max_date = f"{year}/12/31"
    ret_max = 10000
    journal_dfs = paper_loop(query_str, min_date, max_date, 60000, ret_max)
    journal_dfs.to_csv(save_path)


if __name__ == '__main__':
    main(sys.argv[1:], "final_journals.txt")

