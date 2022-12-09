#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 09:16:07 2022

@author: swk25
"""

import pandas as pd
import scipy.stats
import numpy as np
import os
import sys, getopt


def read_merge_data(year):
    mapauthlist=pd.read_csv("../output/{}/{}_all_mapped_author_list.txt".format(year,year),sep='\t')
    return mapauthlist

def process_country(df):
    df=df.rename(columns={0:"first",1:"last",2:"country",3:"city"})
    df['country']=df['country'].str.replace('_',' ')
    df["country"]=df["country"].replace('usa', 'united states')
    df["country"]=df["country"].replace('taiwan', 'china')
    return df

def commmon_auth(mal,commonauthors,year,degree_all,count_all,column):
    year=str(year)
    malf = mal[mal['author'].isin(commonauthors)]
    malf['dq'] = [1 if x > degree_all else 0 for x in malf['DEGREE']]
    malf['cq'] = [2 if x > count_all else 0 for x in malf[column]]
    malf['quadrant']=malf['dq']+malf['cq']
    cntq=(malf.groupby(['continent','quadrant']).count()['author'])
    # To make count vs degree plot in tableau
    malf.to_csv('../output/'+year+'/'+year+'_all_'+column+'quadranttable.txt',sep='\t',index=False)
    return malf,cntq

def country_net(malf,year):
    # Reading the data
    year =str(year)
    edgelist=pd.read_csv("../output/"+year+"/"+year+"_all_mapped_edge_list.txt",sep='\t')
    countrycontinent=pd.read_csv("../input/countryContinentMapping.csv",header=0,sep=',')
    countrycontinent["country"]=countrycontinent["country"].str.lower() 
    countrycontinent["continent"]=countrycontinent["continent"].str.lower()

    # Writing the edge table
    edlst=pd.DataFrame()
    edlst['Source']=edgelist['country']
    edlst['Target']=edgelist['country1']
    edlst['Id']=edlst.index
    edlst.to_csv('../output/'+year+"/"+year+'_all_countrynet_edge.csv',sep=',',index=False)
    
    # Writing the node table
    ndlst=pd.DataFrame()
    ndlst['country']=pd.concat([edgelist['country'],edgelist['country1']]).unique()
    ndlst=(pd.merge(ndlst, countrycontinent, on='country'))
    ndlst['Id']=ndlst['country']
    ndlst['Label']=ndlst['country']
    ndlst.to_csv('../output/'+year+"/"+year+'_all_countrynet_auth.csv',sep=',',index=False)
    return

def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv,"p:",["path="])
    except getopt.GetoptError:
        print("Recheck the format of input arguments given")
        sys.exit(2)
    for opt, arg in opts:
        path1 = arg
    return path1 
#%% Reading the data for year wise
path = parse_args(sys.argv[1:])
print(path)
os.chdir(path)
mal_18=read_merge_data(str(2018))
mal_19=read_merge_data(str(2019))
mal_20=read_merge_data(str(2020))
mal_21=read_merge_data(str(2021))
#%% Finding the author list which is common across years
'''
Analysis now done for the common authors across the years
We only have to generate the sankey plot from this
Hence it requires common authors across the years
'''
commonauthors=list(set(mal_18['author'])&set(mal_19['author'])& set (mal_20['author'])& set(mal_21['author']))
degree_all = mal_18['DEGREE'].append(mal_19['DEGREE']).append(mal_20['DEGREE']).append(mal_21['DEGREE']).quantile(0.95)
count_all = 3
#%% Defining and writing the quadrant table for filtered network
malf_18,cntq_18=commmon_auth(mal_18,commonauthors,2018,degree_all,count_all,'count')
malf_19,cntq_19=commmon_auth(mal_19,commonauthors,2019,degree_all,count_all,'count')
malf_20,cntq_20=commmon_auth(mal_20,commonauthors,2020,degree_all,count_all,'count')
malf_21,cntq_21=commmon_auth(mal_21,commonauthors,2021,degree_all,count_all,'count')
#%% writing the filtered author list for journal counts
malf_18.to_csv('../output/2018/2018_all_malf.txt',sep='\t',index=False)
malf_19.to_csv('../output/2019/2019_all_malf.txt',sep='\t',index=False)
malf_20.to_csv('../output/2020/2020_all_malf.txt',sep='\t',index=False)
malf_21.to_csv('../output/2021/2021_all_malf.txt',sep='\t',index=False)
#%% counting the fractions for making the sankey diagram
malf_18.set_index('author', inplace=True)
malf_19.set_index('author', inplace=True)
malf_20.set_index('author', inplace=True)
malf_21.set_index('author', inplace=True)
#%%
malf_allq=(pd.concat([malf_18['quadrant'],malf_19['quadrant'],malf_20['quadrant'],malf_21['quadrant']],axis=1,ignore_index=True))
malf_allq['quadmerged1819']=malf_allq[0].astype('str')+malf_allq[1].astype('str')
malf_allq['quadmerged1920']=malf_allq[1].astype('str')+malf_allq[2].astype('str')
malf_allq['quadmerged2021']=malf_allq[2].astype('str')+malf_allq[3].astype('str')
#%%
print(malf_allq.groupby(['quadmerged1819']).count()[0]/len(malf_allq))
print(malf_allq.groupby(['quadmerged1920']).count()[0]/len(malf_allq))
print(malf_allq.groupby(['quadmerged2021']).count()[0]/len(malf_allq))
#%% Doing analysis on complete network
'''
Analysis now done for complete author list
We will do quadrant wise plot and the logsOR
Further the country wise collaboration network
'''
commonauthors=list(set(mal_18['author']).union(set(mal_19['author']) , set (mal_20['author']) , set(mal_21['author'])))
#%%
mal_18,cntq_18=commmon_auth(mal_18,commonauthors,2018,degree_all,count_all,'count')
mal_19,cntq_19=commmon_auth(mal_19,commonauthors,2019,degree_all,count_all,'count')
mal_20,cntq_20=commmon_auth(mal_20,commonauthors,2020,degree_all,count_all,'count')
mal_21,cntq_21=commmon_auth(mal_21,commonauthors,2021,degree_all,count_all,'count')
cntq_all=pd.concat([cntq_18,cntq_19,cntq_20,cntq_21],axis=1).fillna(0)
#%% Generate continent wise quadrant fractions for the figure 2 panel b
cntq_all=cntq_all.reset_index()
cntq_all.continent=cntq_all.continent.replace(['africa','oceania','south america'],'ocafsf')
cntq_all=(cntq_all.groupby(['continent','quadrant']).sum()['author'])
cntq_all=cntq_all.T.reset_index(drop=True).T
#%%
logor=cntq_all.reset_index()
color = ['#e15759','#76b7b2','#4e79a7']
for continent in list(set(logor.continent)):
    asia=logor[logor.continent==continent].drop(columns=['continent','quadrant'])
    asiaden=asia.loc[:,0:3].sum()-asia.loc[:,0:3]
    aor=asia/asiaden
    aer=(1/asia + 1/asiaden)
    
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
    plot.figure.savefig('../output/Final_Figures/Figure2/'+str(continent)+'_barplot.svg', format='svg',dpi=1200)
### Uncomment to savecontinent wise quadrant distribution
# cntq_all.to_csv('../output/all_cntquad_mal.txt',sep='\t')
#%% Plotting LOR for all the data
asia=logor.groupby('quadrant').sum()
asiaden=asia.loc[:,0:3].sum()-asia.loc[:,0:3]
aor=asia/asiaden
aer=(1/asia + 1/asiaden)

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
plot=alor.plot.bar(yerr=aler,xticks=[0,1,2,3],color=color,capsize=4).axhline(y=0, color= 'black',linewidth=1)
plot.figure.savefig('../output/Final_Figures/Figure2/overall_barplot.svg', format='svg',dpi=1200)
#%% Making the country-wise network for gephi Figure 2 last panels
#Writes country wise edge and node table
country_net(mal_18,2018)
country_net(mal_19,2019)
country_net(mal_20,2020)
country_net(mal_21,2021)
print("Comparative analysis for overall data done !!")