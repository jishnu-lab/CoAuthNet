import re

'''
Coauthorship Network Project
Author: Eunseo Sung

Extract and save list of PubMed Journals of interest
(Regex Query: Nature*, Science*, PLoS*, Cell*)

Input: J_Medline.txt
    List of all journals from pubmed
    https://www.nlm.nih.gov/bsd/serfile_addedinfo.html
Output: filtered_journals.txt
'''

def get_journal(path, dest_path, queries):
    with open(path, "rt") as f:
        j_raw = f.read()
    j_list = j_raw.split("--------------------------------------------------------")
    j_list = j_list[1:]
    j_filtered = []
    for journal in j_list:
        journal_title_line = (journal.strip().splitlines())[1]
        journal_title = ((journal_title_line.split(": "))[1]).strip()
        for query in queries:
            journal_check = bool(re.match(query, journal_title.lower()))
            if journal_check:
                j_filtered.append(journal_title)
    with open(dest_path, "wt") as f:
        f.write("\n".join(j_filtered))
    return j_filtered


if __name__ == "__main__":
    queries = ["nature*", "science*", "cell*", "plos*"]
    journals = get_journal("J_Medline.txt", "filtered_journals.txt", queries)
    print(len(journals))

