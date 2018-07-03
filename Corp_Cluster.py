# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 11:34:35 2018

@author: sameer kulkarni
"""

import pandas as pd
import numpy  as np
import sklearn.cluster
import difflib
import re
import nltk

import textChecks as tc


#import spell_it_right as mySpell



#from autocorrect import spell

from scipy.spatial import distance
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
psr = nltk.PorterStemmer()

xWords=set(('a', 'be','ve'))
s=set(stopwords.words('english'))- xWords

s.update(("ab", "ag", "co", "com", "corporate", "corporated", "de", "gmbh", "inc", "incorporated", "incorporation", "limited", "llc", "llp", "ltd", "P", "pacific", "plc", "pvt", "sa", "se", "ghq", "fze", "fz", "fzco","mbh", "pty", "l", "lc", "c", "f", "z"))

#print(s)
fldrPath = "G:/Revnomix_backup/GDrive/MAF/Sheraton/"
#"G:/Revnomix_backup/GDrive/MAF/Kempinsky/"

xlfile = fldrPath + 'ListOfCompanies.xlsx'

df_corp = pd.read_excel(xlfile, index_col=None, na_values=['NA'])

df_corp['CorpName'] = df_corp['Company Name'].apply(lambda x: re.sub('\([^)]*\)', ' ', x))
df_corp['CorpName'] = df_corp['CorpName'].str.lower()
df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: tc.getTxt(x))

df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: re.sub('[^A-Za-z0-9]+', ' ', x))
df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: re.sub('\d', '', x))
df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: ' '.join([w for w in x.split() if w.lower() not in s]))

df_corp['Corp1'] = df_corp['CorpName'].apply(lambda x: ' '.join([wnl.lemmatize(name) for name in x.split()]))
df_corp['Corp1'] = df_corp['Corp1'].apply(lambda x: ' '.join([psr.stem(name) for name in x.split()]))
df_corp['Corp2'] = df_corp['Corp1'].apply(lambda x: ' '.join([w for index, w in enumerate(x.split()) if  index < 2]))

# =============================================================================
# x = df_corp['Corp2'].to_string(header=False, index=False).split(',')
# 
# y= pd.Series(' '.join(x).lower().split()).value_counts()[:100]
# 
# y.to_csv(fldrPath + 'common_list_new.csv', sep=',', encoding='utf-8')
# 
# =============================================================================


df_corp.sort_values(by = 'Corp2', axis=0, ascending = True, inplace=True)
df_corp = df_corp.reset_index(drop=True)

df_corp['Cluster1'] = ""
df_corp['Cluster2'] = ""

for row in range(0,len(df_corp)):
    crpName = df_corp['Corp2'].iloc[row]
    for i in range(0,len(df_corp)):    
        if len(df_corp['Cluster1'].iloc[i])==0:
            df_corp['Cluster1'].iloc[i] = tc.clusterByName(crpName, df_corp['Corp2'].iloc[i], 0)            
        if len(df_corp['Cluster2'].iloc[i])==0:
            df_corp['Cluster2'].iloc[i] = tc.clusterByName(crpName, df_corp['Corp2'].iloc[i], 1)

df_corp['Cluster1'] = df_corp['Cluster1'].apply(lambda x: ''.join(x))
df_corp['Cluster2'] = df_corp['Cluster2'].apply(lambda x: ''.join(x))

df_corp.sort_values(by = ['Cluster1','Cluster2'], axis=0, ascending = True, inplace=True)
df_corp = df_corp.reset_index(drop=True)

df_corp['fnlSlug1']  = df_corp['Corp2']
df_corp['fnlSlug2']  = df_corp['Corp2']

for i in range(1,len(df_corp)):
    df_corp['fnlSlug1'].iloc[i]  = np.where((df_corp['Cluster1'].iloc[i]) == "", df_corp['fnlSlug1'].iloc[i], np.where((df_corp['Cluster1'].iloc[i]) == (df_corp['Cluster1'].iloc[i-1]), df_corp['fnlSlug1'].iloc[i-1], df_corp['fnlSlug1'].iloc[i]))
    df_corp['fnlSlug1']        = df_corp['fnlSlug1'].apply(str)
    
    df_corp['fnlSlug2'].iloc[i]  = np.where((df_corp['Cluster2'].iloc[i]) == "", df_corp['fnlSlug2'].iloc[i], np.where((df_corp['Cluster2'].iloc[i]) == (df_corp['Cluster2'].iloc[i-1]), df_corp['fnlSlug2'].iloc[i-1], df_corp['fnlSlug2'].iloc[i]))
    df_corp['fnlSlug2']        = df_corp['fnlSlug2'].apply(str)
	

df_corp.to_csv(fldrPath + 'Corp_List_15JUN18.csv', sep=',', encoding='utf-8')






