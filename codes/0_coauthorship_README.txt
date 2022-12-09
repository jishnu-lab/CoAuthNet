Coauthorship Network Project
Authors: Swapnil Keshari, Eunseo Sung , and Jishnu Das

Info on data files and code
Updated by: Eunseo Sung on 2022/10/25
Updated by: Swapnil Keshari on 2022/12/09

extract_journals.py
    Description:
        Filters all journal names on PubMed for those containing keywords
        - Science, PLoS, Cell, Nature
    Input: 
        J_Medline.txt --> list of all journals on PubMed
        https://www.nlm.nih.gov/bsd/serfile_addedinfo.html
    Output: 
        filtered_journals.txt
        Filtered manually later to get final_journals.txt

pubmed_scrape.py
    Description:
        Scrapes pubmed for journals (uses Bio Entrez Package)
        https://biopython.org/docs/1.76/api/Bio.Entrez.html
    Input: 
        final_journals.txt
        - Takes command line arguments -year [year]
    Output: 
        [year]_all_journal_unfiltered.csv
        - Raw data scraped from PubMed

split_journals.py
    Description:
        Splits [year]_all_journal_unfiltered.csv into 10 separate files (approximately even size)
    Input: 
        [year]_all_journal_unfiltered.csv
    Output: 
        [year]_split_journals (directory)

clean_pubmed_data.py
    Description:
        Clean location info (country/city) of each author
    Input: 
        [year]_split_journals/[year]_journals_[index].csv
        - Takes command line arguments -y [year] -i [file index]
    Output: 
        [year]_split_journals_clean/[year]_journals_clean_[index].csv
        - Outputs list of papers but with locations of all authors cleaned
        - Removes any authors that do not have valid location info
        * Requires installing affiliation_parser and locationtagger packages
        - affiliation_parser
            https://github.com/titipata/affiliation_parser
        - locationtagger
            https://pypi.org/project/locationtagger/

coa_edge_generation.py
    Description:
        Takes cleaned list of papers to generate edge list of graph and list of valid authors
    Input: 
        [year]_split_journals 
        - Takes command like arguments -y [year]
    Output: 
        [year]_edge_list.csv
        [year]_author_list.csv

analyzing_network.py
    Description:
        Maps country to continent, Merges centrality, writes autor and edge list for whole and largest connected component (lcc) of the network
    Input: 
        [year]_edge_list.csv,[year]_author_list.csv and countryContinentMapping.csv
        - Takes command like arguments -y [year] and -p [path/to/codes]
    Output: 
        [year]_all_mapped_author_list.txt, [year]_all_mapped_edge_list.txt
        [year]_lcc_mapped_author_list.txt
        [year]_country_fraction.txt

comparative_analysis_all.py, comparativeanalysis_lcc.py
    Description:
        Performs comparative analysis across years, assigns quadrant to authors, do logOR analysis, write files for common authors across years and generate data for Sankey Plot
    Input:
        [year]_all_mapped_author_list.txt, [year]_all_mapped_edge_list.txt, [year]_lcc_mapped_author_list.txt
        - Takes command like arguments -p [path/to/codes]
    Output:
        [year]_all_countquadranttable.txt, [year]_lcc_nodebetweennessquadranttable.txt
        [continent]_barplot.svg
        [year]_all_countrynet_edge.csv, [year]_all_countrynet_edge.csv
        [year]_all_malf.txt,[year]_lcc_malf.txt
        
journalwise_analysis_all.py, journalwise_analysis_lcc.py
    Description:
        Peforms comparative analysis for commonauthors,generate logOR plots for journal wise analysis
    Input:
        [year]_all_malf.txt,[year]_lcc_malf.txt
        - Takes command like arguments -p [path/to/codes]
    Output:
        [journal]_all_barplot.svg,[journal]_lcc_barplot.svg
