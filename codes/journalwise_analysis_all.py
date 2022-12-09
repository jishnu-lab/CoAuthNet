#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 13:24:46 2022

@author: swk25
"""
import pandas as pd
import scipy.stats
import numpy as np
import os
import sys, getopt

def journaltable (year):
    mapauthlist=pd.read_csv("../output/{}/{}_all_malf.txt".format(year,year),sep='\t')
    journals=pd.DataFrame([])
    journals['journals']=mapauthlist['journals'].str.split(',')
    journals['country']=mapauthlist['country']
    journals['continent']=mapauthlist['continent']
    journals['quadrant']=mapauthlist['quadrant']
    # journals['author']=mapauthlist['author']
    journals['HDI']=mapauthlist['HDI Rank']
    journals=journals.explode('journals')
    journals=journals[journals['journals']!=' N.Y.)']
    assert mapauthlist['count'].sum() == len(journals)
    return journals, mapauthlist

def majorjournals (journals,mal):
    nature=journals.loc[(journals['journals'].str.contains('Nature'))]
    science=journals.loc[(journals['journals'].str.contains('Science'))]
    cell=journals.loc[(journals['journals'].str.contains('Cell'))]
    plos=journals.loc[(journals['journals'].str.contains('PLoS'))]
    assert mal['count'].sum() == len(nature)+len(cell)+len(science)+len(plos)
    qwfrac=(pd.concat([nature['quadrant'].value_counts(),\
                       science['quadrant'].value_counts(),\
                           cell['quadrant'].value_counts(),\
                               plos['quadrant'].value_counts()],\
                      axis=1,ignore_index=True))
    qwfrac=qwfrac.rename(columns={0:'nature',1:'science',2:'cell',3:'plos'})
    return nature, science, cell, plos,qwfrac

def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv,"p:",["path="])
    except getopt.GetoptError:
        print("Recheck the format of input arguments given")
        sys.exit(2)
    for opt, arg in opts:
        path1 = arg
    return path1 
#%% Developing the journal table and reading the count quadrant table as mal
path = parse_args(sys.argv[1:])
print(path)
os.chdir(path)
j_18,mal_18=journaltable(2018)
j_19,mal_19=journaltable(2019)
j_20,mal_20=journaltable(2020)
j_21,mal_21=journaltable(2021)
#%% splitting the journals in major journals category
n_18,s_18,c_18,p_18,qf_18=majorjournals(j_18,mal_18)
n_19,s_19,c_19,p_19,qf_19=majorjournals(j_19,mal_19)
n_20,s_20,c_20,p_20,qf_20=majorjournals(j_20,mal_20)
n_21,s_21,c_21,p_21,qf_21=majorjournals(j_21,mal_21)
#%% lor for journals
color = ['#e15759','#76b7b2','#4e79a7']
for journal in list(['nature','science','cell','plos']):
    fraction=pd.concat([qf_18[journal],qf_19[journal],qf_20[journal],qf_21[journal]],axis=1)
    fraction=fraction.T.reset_index(drop=True).T
    fracden=fraction.loc[:,0:3].sum()-fraction.loc[:,0:3]
    aor=fraction/fracden
    aer=(1/fraction + 1/fracden)
    
    alor=pd.DataFrame()
    alor['19/18']=aor[1]/aor[0]
    alor['20/19']=aor[2]/aor[1]
    alor['21/20']=aor[3]/aor[2]
    alor=np.log(alor)
    
    aler=pd.DataFrame()
    aler['19/18']=aer[1]+aer[0]
    aler['20/19']=aer[2]+aer[1]
    aler['21/20']=aer[3]+aer[2]
    aler=np.sqrt(aler)
    
    significance = (alor/aler).abs()
    pvalue=scipy.stats.norm.sf(significance)
    plot=alor.plot.bar(yerr=aler,color=color,xlabel=None,legend=False,capsize=4).axhline(y=0, color= 'black',linewidth=1)
    plot.figure.savefig('../output/Final_Figures/Figure4/'+str(journal)+'_all_barplot.svg', format='svg',dpi=1200)