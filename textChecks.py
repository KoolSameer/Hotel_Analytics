# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 12:41:52 2018

@author: SAMEER KULKARNI
"""


def getTxt(strName):
    
    remList = ["a", "al", "asia", "australia", "auto", "autoparts", "autos", "automotive", "automotives", "bank", "bharat", "bio", "centre", "company", "continental", "corporation", "e", "electric", "electrical", "electronic", "electronics", "engineering", "entertainment", "fluid", "general", "global", "group", "high", "hindustan", "india", "industries", "industry", "international", "knowledge", "logistics", "management", "media", "medical", "music", "national", "power", "seed", "seeds", "service", "services", "solution", "solutions", "system", "systems", "technical", "technologies", "technology", "telecom", "telecoms", "telecommunication", "trading", "unimedia", "united", "universal", "g", "h", "q", "middle", "east", "private", "hotel", "bin", "consulate", "general", "consul"]
    
    sTxt = strName
    txt  = sTxt.split()    
    
    lst  = [name for index, name in enumerate(txt) if name in remList and index > 1]
    
    if len(lst)>0 :
        txt.remove(lst[0])                
    mytxt = ' '.join([w for w in txt])    
    return mytxt


def clusterByName(srcName, trgName, txtPos):
    
#list of words to be ignored while clustering    
    remList = ["a", "al", "asia", "australia", "auto", "autopart", "bank", "bharat", "bio", "centre", "company", "continent", "corp", "corpor", "e", "electr", "engin", "entertainment", "europe", "foundat", "fluid", "general", "global", "group", "high", "hindustan", "india", "industry", "intern", "japan",  "kabi", "knowledge", "logistics", "management", "medic", "metal", "metgla", "music", "national", "power", "seed", "servic", "solut", "system", "tech", "technolg", "technolog", "telecom", "tool", "tower", "trading", "travel", "unimedia", "united", "univers", "world", "worldwid", "zosen", "middl", "east", "hotel","ministri", "nation", "abu", "dhabi","dubai","consulate", "general", "consul"]
        
    sName = srcName.split() #Searching corporate name phrase
    tName = trgName.split() #values from the dataframe
                        
    if len(sName)>1 :
        tPos  = int(txtPos)
    else :
        tPos  =  0



#Some of the words to be added back to the list of ignored words based on the occurance of such words
    adTxt = ["automot", "citi", "private","central", "general"] 
    
#Some of the words to be removed from the list of ignored words based on the occurance of such words    
    xTxt= ["a", "continent", "bio", "metal", "travel", "intern", "world","electr","dubai"] 

    adStr = []
    xStr  = []
    try:
        adStr = [name for name in adTxt if name == sName[tPos]] 
    except:
        print(adTxt,sName)
    
    try:    
        xStr = [name for name in xTxt if name == sName[tPos]]
    except:
        print(xTxt,sName)
   
    if len(adStr)>0:
        if tPos == 0 and  sName[tPos] == adStr[0]:
            remList = remList + adStr[0].split()

    if len(xStr)>0:
        if tPos == 0 and  sName[tPos] == xStr[0]:
            del remList[remList.index(xStr[0])]
    
    txtLst  = []
    try:
        txtLst  = [name for name in tName if name == sName[tPos]]
    except:
        print(tName,sName)
   
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
    
    remList = ["a", "al", "asia", "australia", "auto", "autopart", "bank", "bharat", "bio", "centre", "company", "continent", "corp", "corpor", "e", "electr", "engin", "entertainment", "europe", "foundat", "fluid", "general", "global", "group", "high", "hindustan", "india", "industry", "intern", "japan",  "kabi", "knowledge", "logistics", "management", "medic", "metal", "metgla", "music", "national", "power", "seed", "servic", "solut", "system", "tech", "technolg", "technolog", "telecom", "tool", "tower", "trading", "travel", "unimedia", "united", "univers", "world", "worldwid", "zosen"]
        
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


