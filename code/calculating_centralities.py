#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 13:11:07 2022

@author: swk25
"""

#%% Importing Libraries
import networkx as nx
import pandas as pd
import sys, getopt
import os

def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv,"y:p:",["year=","path="])
    except getopt.GetoptError:
        print("Recheck the format of input arguments given")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-p", "--path"):
            path1 = arg
        elif opt in ("-y", "--year"):
            year1 = arg
    return year1,path1 
#%%
year,path = parse_args(sys.argv[1:])
print(year,path)
os.chdir(path)
edgelist=pd.read_csv('../input/'+year+"_all_mapped_edge_list.txt",sep='\t')
#%% Generating the network
COA=nx.Graph()
edgetuple=list(zip(edgelist['source'],edgelist['target']))
COA.add_edges_from(edgetuple)
#%% Node betweenness centrality
nodebetweeness=nx.betweenness_centrality(COA)
nodebettable=pd.DataFrame.from_dict(nodebetweeness,orient='index')
nodebettable.to_csv('../output/'+year+'_node_betweeness.txt',sep='\t')