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

#import spell_it_right as mySpell



#from autocorrect import spell

from scipy.spatial import distance
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
wnl = WordNetLemmatizer()
psr = nltk.PorterStemmer()


#tst = "automotive technologies"
#
#tst1 = ' '.join(psr.stem(x) for x in tst.split())


#from nltk.PorterStemmer import stems

xWords=set(('a', 'be','ve'))
s=set(stopwords.words('english'))- xWords

s.update(("ab", "ag", "co", "com", "corporate", "corporated", "de", "gmbh", "inc", "incorporated", "incorporation", "limited", "llc", "llp", "ltd", "P", "pacific", "plc", "private", "pvt", "sa", "se"))

#print(s)

xlfile = 'G:\GDrive\RoomTypeYielding_Tool\ListOfCompanies.xlsx'
df_corp = pd.read_excel(xlfile, index_col=None, na_values=['NA'])

#---- 1
#df_corp['CorpSlug'] = df_corp['Company Name'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', x))
#df_corp['CorpSlug'] = df_corp['CorpSlug'].apply(lambda x: re.sub('\d', '', x))
#df_corp['CorpSlug'] = df_corp['CorpSlug'].str.lower()

#---- 2
df_corp['CorpName'] = df_corp['Company Name'].apply(lambda x: re.sub('\([^)]*\)', ' ', x))
df_corp['CorpName'] = df_corp['CorpName'].str.lower()
df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: getTxt(x))

df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: re.sub('[^A-Za-z0-9]+', ' ', x))
df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: re.sub('\d', '', x))
df_corp['CorpName'] = df_corp['CorpName'].apply(lambda x: ' '.join([w for w in x.split() if w.lower() not in s]))

#df_corp['CorpNameSlug'] = df_corp['CorpName'].apply(lambda x: re.sub('[^A-Za-z0-9]+', '', x))
#df_corp['CorpArray']    = df_corp['CorpName'].apply(lambda x: x.split())
#print(wnl.lemmatize('technologies'))

df_corp['Corp2'] = df_corp['CorpName'].apply(lambda x: ' '.join([wnl.lemmatize(name) for index, name in enumerate(x.split()) if  index < 2]))


#df_corp['Corp2'] = df_corp['Corp2'].apply(lambda x: ' '.join([mySpell.correction(name) for name in x.split()]))

df_corp['Corp2'] = df_corp['Corp2'].apply(lambda x: ' '.join([psr.stem(name) for name in x.split()]))

#df_corp.to_csv('G:/GDrive/RoomTypeYielding_Tool/Corp_List_16APR18_test.csv', sep=',', encoding='utf-8')


x = df_corp['Corp2'].to_string(header=False, index=False).split(',')

y= pd.Series(' '.join(x).lower().split()).value_counts()[:100]

y.to_csv('G:/GDrive/RoomTypeYielding_Tool/common_list_new.csv', sep=',', encoding='utf-8')



#print(wnl.lemmatize("automotives"))
#print(df_corp['Corp2'] )
#df_corp['Corp2'] =df_corp['Corp2']
#df_corp['CorpName']=df_corp['CorpName'].apply(str)

df_corp.sort_values(by = 'Corp2', axis=0, ascending = True, inplace=True)
df_corp = df_corp.reset_index(drop=True)

df_corp['Cluster1'] = ""
df_corp['Cluster2'] = ""

for row in range(0,len(df_corp)):
    crpName = df_corp['Corp2'].ix[row]
    for i in range(0,len(df_corp)):    
        if len(df_corp['Cluster1'].ix[i])==0:
            df_corp['Cluster1'].ix[i] = clusterByName(crpName, df_corp['Corp2'].ix[i], 0)            
        if len(df_corp['Cluster2'].ix[i])==0:
            df_corp['Cluster2'].ix[i] = clusterByName(crpName, df_corp['Corp2'].ix[i], 1)

df_corp['Cluster1'] = df_corp['Cluster1'].apply(lambda x: ''.join(x))
df_corp['Cluster2'] = df_corp['Cluster2'].apply(lambda x: ''.join(x))

df_corp.sort_values(by = ['Cluster1','Cluster2'], axis=0, ascending = True, inplace=True)
df_corp = df_corp.reset_index(drop=True)


df_corp['fnlSlug1']  = df_corp['CorpName']
#df_corp['fnlSlug1'] =df_corp['fnlSlug1'].apply(str)

df_corp['fnlSlug2']  = df_corp['CorpName']
#df_corp['fnlSlug2']=df_corp['fnlSlug2'].apply(str)

for i in range(1,len(df_corp)):
    df_corp['fnlSlug1'].ix[i]  = np.where((df_corp['Cluster1'].ix[i]) == "", df_corp['fnlSlug1'].ix[i], np.where((df_corp['Cluster1'].ix[i]) == (df_corp['Cluster1'].ix[i-1]), df_corp['fnlSlug1'].ix[i-1], df_corp['fnlSlug1'].ix[i]))
    df_corp['fnlSlug1']        = df_corp['fnlSlug1'].apply(str)
    
    df_corp['fnlSlug2'].ix[i]  = np.where((df_corp['Cluster2'].ix[i]) == "", df_corp['fnlSlug2'].ix[i], np.where((df_corp['Cluster2'].ix[i]) == (df_corp['Cluster2'].ix[i-1]), df_corp['fnlSlug2'].ix[i-1], df_corp['fnlSlug2'].ix[i]))
    df_corp['fnlSlug2']        = df_corp['fnlSlug2'].apply(str)


df_corp.to_csv('G:/GDrive/RoomTypeYielding_Tool/Corp_List_17APR18.csv', sep=',', encoding='utf-8')







for i in range(1,len(df_corp)):    
    df_corp['fnlSlug1'].ix[i] = np.where((df_corp['fnlSlug1'].ix[i]) == "",
                                          df_corp['Cluster1'].ix[i],
                                          df_corp['Cluster1'].ix[i-1])
    df_corp['fnlSlug1']=df_corp['fnlSlug1'].apply(str)











def getTxt(strName):
    
    remList = ["a", "asia", "australia", "auto", "autoparts", "autos", "automotive", "automotives", "bank", "bharat", "bio", "centre", "company", "continental", "corporation", "e", "electric", "electrical", "electronic", "electronics", "engineering", "entertainment", "fluid", "general", "global", "group", "high", "hindustan", "india", "industries", "industry", "international", "knowledge", "logistics", "management", "media", "medical", "music", "national", "power", "seed", "seeds", "service", "services", "solution", "solutions", "system", "systems", "technical", "technologies", "technology", "telecom", "telecoms", "telecommunication", "trading", "unimedia", "united", "universal"]
    
    sTxt = strName
    txt  = sTxt.split()    
    
    lst  = [name for index, name in enumerate(txt) if name in remList and index > 1]
    
    if len(lst)>0 :
        txt.remove(lst[0])                
    mytxt = ' '.join([w for w in txt])    
    return mytxt


def clusterByName(srcName, trgName, txtPos):
    
    remList = ["a", "asia", "australia", "auto", "autopart", "bank", "bharat", "bio", "centre", "company", "continent", "corp", "corpor", "e", "electr", "engin", "entertainment", "europe", "foundat", "fluid", "general", "global", "group", "high", "hindustan", "india", "industry", "intern", "japan",  "kabi", "knowledge", "logistics", "management", "medic", "metal", "metgla", "music", "national", "power", "seed", "servic", "solut", "system", "tech", "technolg", "technolog", "telecom", "tool", "tower", "trading", "travel", "unimedia", "united", "univers", "world", "worldwid", "zosen"]
        
    
#    srcName = "continental automotive"
#    txtPos = 1
    sName = srcName.split()
    tName = trgName.split()
                        
    if len(sName)>1 :
        tPos  = int(txtPos)
    else :
        tPos  =  0
#,"continental"
#    adTxt = ["automotive"]
    adTxt = ["automot"]
    xTxt= ["a", "continent", "bio", "metal"]

    adStr = [name for name in adTxt if name == sName[tPos]]
    xStr = [name for name in xTxt if name == sName[tPos]]

    if len(adStr)>0:
        if tPos == 0 and  sName[tPos] == adStr[0]:
            remList = remList + adStr[0].split()

    if len(xStr)>0:
        if tPos == 0 and  sName[tPos] == xStr[0]:
            del remList[remList.index(xStr[0])]
        
    txtLst  = [name for name in tName if name == sName[tPos]]
    
    lst = 0
    
    if len(txtLst)==0:
        txtLst=""
    else :
        if txtLst[0] in remList:
            lst = 1
        
    if lst >0 :
        txtLst=""
        
    return txtLst



def ingnoreName(srcName, trgName, txtPos):
    
    remList = ["a", "asia", "australia", "auto", "autopart", "bank", "bharat", "bio", "centre", "company", "continent", "corp", "corpor", "e", "electr", "engin", "entertainment", "europe", "foundat", "fluid", "general", "global", "group", "high", "hindustan", "india", "industry", "intern", "japan",  "kabi", "knowledge", "logistics", "management", "medic", "metal", "metgla", "music", "national", "power", "seed", "servic", "solut", "system", "tech", "technolg", "technolog", "telecom", "tool", "tower", "trading", "travel", "unimedia", "united", "univers", "world", "worldwid", "zosen"]
        
    
#    srcName = "continental automotive"
#    txtPos = 1
    sName = srcName.split()
    tName = trgName.split()
                        
    if len(sName)>1 :
        tPos  = int(txtPos)
    else :
        tPos  =  0
#,"continental"
#    adTxt = ["automotive"]
    adTxt = ["automot"]
    xTxt= ["a", "continent", "bio", "metal"]

    adStr = [name for name in adTxt if name == sName[tPos]]
    xStr = [name for name in xTxt if name == sName[tPos]]

    if len(adStr)>0:
        if tPos == 0 and  sName[tPos] == adStr[0]:
            remList = remList + adStr[0].split()

    if len(xStr)>0:
        if tPos == 0 and  sName[tPos] == xStr[0]:
            del remList[remList.index(xStr[0])]
        
    txtLst  = [name for name in tName if name == sName[tPos]]
    
    lst = 0
    
    if len(txtLst)==0:
        txtLst=""
    else :
        if txtLst[0] in remList:
            lst = 1
        
    if lst >0 :
        txtLst=""
        
    return txtLst























x = df_corp['CorpName'].to_string(header=False, index=False).split(',')

y= pd.Series(' '.join(x).lower().split()).value_counts()[:100]

y.to_csv('G:/GDrive/RoomTypeYielding_Tool/common_list.csv', sep=',', encoding='utf-8')

