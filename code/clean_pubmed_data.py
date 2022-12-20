import numpy as np
import pandas as pd
import affiliation_parser 
    # https://github.com/titipata/affiliation_parser
    # Parses affiliation info from pubmed metadata
import locationtagger 
    # https://pypi.org/project/locationtagger/
    # Identifies geographical locations in string
import sys, getopt
import os

'''
Coauthorship Network Project
Author: Eunseo Sung

Cleaning journal info from pubmed
    - Author affiliation info parsed with affiliation_parser package
    - Countries and cities/states with locationtagger package
        - extracts location related string from input string based on country-state/city pairing
    - Filter for papers with at least 75% of authors with valid location information and more than 2 valid authors

Input: [year]_split_journals (directory)
Output: [year]_split_journals_clean (directory)
'''


# Input: List of author strings from one paper
# - author string list = [firstname1$lastname$affiliation1#firstname2$lastname2$affiliation$...]
# - author string = firstname$lastname$affiliation
# Output: firstname1.lastname1.country1.city1,firstname2.lastname2.country2.city2,...
def get_location(author_lst):
    a_info_list = author_lst.split("#")
    a_clean_list = []

    for author_str in a_info_list:
        try:
            author_comps = author_str.split("$")
            firstname = author_comps[0]
            lastname = author_comps[1]
            aff_raw = author_comps[2]
            aff_parsed = affiliation_parser.parse_affil(aff_raw)
            
            # country info from affiliation parser
            country = aff_parsed["country"]
            # affiliation parser does not return city directly --> gives institution address, etc.
            # use location tagger to extract exact city from affiliation parser output
            loc_str = aff_parsed["location"]

            place_entity = locationtagger.find_locations(text = loc_str)
            # special case for USA to get state instead of city
            if country == "united states of america":
                country = "usa" #reformat country name
                city_1 = place_entity.regions[0].lower() #convert to lowercase
                city = ''.join(filter(str.isalnum, city_1)) #remove non-alphanumerical characters
                if city == "": #don't include authors if no valid city found
                    continue
            elif (len(place_entity.cities) > 0) and (place_entity.cities[0].lower() != country):
                city_1 = place_entity.cities[0].lower()
                city = ''.join(filter(str.isalnum, city_1))
            else:
                continue

            # special case for Singapore to define both country and city
            if city == "singapore":
                country = "singapore"

            # only keep authors with valid city and country info
            if (len(city) == 0) or (len(country) == 0):
                continue

            # replace any spaces with "_"
            firstname = (firstname.replace(" ", "_")).lower()
            lastname = (lastname.replace(" ", "_")).lower()
            country = country.replace(" ", "_")
            city = city.replace(" ", "_")

            # format into firstname.lastname.country.city
            clean_str = ".".join([firstname, lastname, country, city])
            a_clean_list.append(clean_str)
        except:
            continue
    
    # keep paper only if:
    #    1. more than 75% of authors have valid country and city info
    #    2. more than 2 authors total
    if (len(a_clean_list) < 0.75 * len(a_info_list)) or (len(a_clean_list) < 2):
        keep_bool = False
    else:
        keep_bool = True
    # return comma-separated list of authors and their info in given paper
    return ",".join(a_clean_list), keep_bool


# Input: raw dictionary form of df with paper info
# Output: dictionary form of df with location/author info cleaned
def clean_location(df):
    authors = df.loc[:, "author"]
    clean_authors = []
    np_authors = list(authors.to_numpy())
    for author_lst in np_authors:
        author_lst_clean, keep_bool = get_location(author_lst)
        if keep_bool:
            clean_authors.append(author_lst_clean)
        else:
            clean_authors.append("")
    df.loc[:, "author"] = clean_authors
    df = df[df["author"] != ""]
    return df


def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv,"hi:y:",["index=", "year="])
    except getopt.GetoptError:
        print("test.py -i <file index> -y <year>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("clean_pubmed_data_v2.py -y <year> -i <file index>")
            sys.exit()
        elif opt in ("-i", "--index"):
            index = arg
        elif opt in ("-y", "--year"):
            year = arg
    return index, year


# Main function for running cleaning by each separate file (10 files total)
def main(argv):
    file_index, year = parse_args(argv)
    in_path = f"{year}_split_journals/{year}_journals_{file_index}.csv"
    out_path = f"{year}_split_journals_clean/{year}_journals_clean_{file_index}.csv"
    
    print("read initial data")
    df = pd.read_csv(in_path, index_col = 0)
    print("cleaning locations")
    clean_df_dict = clean_location(df)
    clean_df = pd.DataFrame.from_dict(clean_df_dict)
    clean_df.to_csv(out_path)


# Command like arguments -y [year] -i [file index]
if __name__ == "__main__":
    main(sys.argv[1:])
