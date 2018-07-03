# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 14:24:20 2018

@author: sameer kulkarni
"""

import pandas as pd
import numpy  as np
import datetime as dt

import getData as gd

#connection = pymysql.connect(host='localhost', user='root', password='admin', db='ihg_phase2', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

#xlfile = 'G:\GDrive\RoomTypeYielding_Tool\CPG_2017.xlsx'
#df_ob = pd.read_excel(xlfile, index_col=None, na_values=['NA'])
#, parse_cols = "A:D"

rmDict = {'PF':'PM','PI':'PM','PX':'PM'}
DowDict= {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}

outPath = 'G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE'
inPath = 'G:/Revnomix_backup/GDrive/MAF/Kempinsky/'

#Run date and month Start Date
#runDate = dt.date.today().strftime("%Y-%m-%d")

strDate = dt.datetime.strptime('2018-07-01',"%Y-%m-%d")
runDate = strDate.date().strftime("%Y-%m-%d")
start_date = str(dt.datetime.today().strftime("%Y-%m-%d"))

#Date to calculate Same Time Last year values
lyDate = gd.addYears(dt.datetime.strptime(start_date,"%Y-%m-%d"),-1)
lyDate = str(lyDate.date().strftime("%Y-%m-%d"))

#Corporate Cluster 
#G:\Revnomix_backup\GDrive\MAF\Kempinsky\Final_Cluster.xlsx'
xlfile = inPath + 'Final_Cluster.xlsx'
df_fnl_clst = pd.read_excel(xlfile, index_col=None, na_values=['NA'])
df_fnl_clst['CompanyName'] = df_fnl_clst['CompanyName'].str.lower()

#Room Type Mapping
xlfile = inPath + 'RM_Type_ETL.xlsx'
#'G:\Revnomix_backup\GDrive\MAF\Kempinsky\RM_Type_ETL.xlsx'
df_rm_type = pd.read_excel(xlfile, index_col=None, na_values=['NA'])

#Market Segment Mapping
xlfile = inPath + 'MS_Mapping_ETL.xlsx'
#'G:\Revnomix_backup\GDrive\MAF\Kempinsky\MS_Mapping_ETL.xlsx'
df_ms_type = pd.read_excel(xlfile, index_col=None, na_values=['NA'],usecols = "A:C")

#List of Fields from OSR
rptFileds = inPath + 'List_Of_Fields_For_OSR.xlsx'
#'G:\Revnomix_backup\GDrive\MAF\Kempinsky\List_Of_Fields_For_OSR.xlsx'

#Name of files with transaction data
#"01.01.15-31.12.15.txt" , "01.01.16-31.12.16.txt" , 
rawFiles = ["01.01.17-31.12.17.txt" , "01.01.18-31.12.18.txt" ]

flPath = 'G:/Revnomix_backup/GDrive/MAF/Kempinsky/'

for index, fl in enumerate(rawFiles):
    df_getData = gd.getData(flPath+fl, rptFileds)
    if index == 0 : 
        df_ob_all = pd.DataFrame(df_getData)
    else:
        df_ob_all = df_ob_all.append(df_getData, ignore_index=True)

df_ob = pd.DataFrame(df_ob_all.drop_duplicates())

#df_ob =  getData(myquery=myquery, pid=hid, rhost=rhost, ruser=ruser, rpwd=rpwd, rdb=rdb, dbtype = dbtype)

df_date=pd.concat([pd.DataFrame({
        'occupancydate' : pd.date_range(row.ArrivalDate, row.DepartureDate), 
        'ReservationID' : row.ConfNumber,
        'CreationDate'  : row.CreationDate,
        'ArrivalDate'   : row.ArrivalDate,
        'DepartureDate' : row.DepartureDate,
        'RoomOccupied'  : row.RoomType,
        'RoomPaid'      : row.RTC,
        'Revenue'       : row.RoomRevenue,
        'MarketCode'    : row.MarketCode,
        'MarketSegment' : row.MarketCodeDesc,
        'CorporateName' : row.CompanyName,
        'Rooms'         : row.NoofRooms,
        'Rate'          : row.RateAmount,
        'RateCode'      : row.RateCode,
        'Status'        : row.ResvStatus,
        'RoomClass'     : row.RoomClass,
        'ShareID'       : row.ShareID,
        'SourceCode'    : row.SourceCode,
        'CancellationDate' :row.CancellationDate
        },  
columns=['occupancydate', 'ReservationID', 'CreationDate', 'ArrivalDate', 'DepartureDate', 'RoomOccupied', 'RoomPaid', 'Revenue', 'MarketCode', 'MarketSegment', 'CorporateName', 'Rooms', 'Rate', 'RateCode', 'Status', 'RoomClass', 'ShareID', 'SourceCode', 'CancellationDate']) for i, row in df_ob.iterrows()], ignore_index=True)

#Setting date format
df_date['CreationDate'] = pd.to_datetime(df_date['CreationDate'], format="%Y-%m-%d")
df_date['ArrivalDate'] = pd.to_datetime(df_date['ArrivalDate'], format="%Y-%m-%d")
df_date['DepartureDate'] = pd.to_datetime(df_date['DepartureDate'], format="%Y-%m-%d")
df_date['CancellationDate'] = pd.to_datetime(df_date['CancellationDate'], format="%Y-%m-%d")

#removing unwanted entries after exlosion    
df_date['dtDif'] = (df_date['DepartureDate']-df_date['occupancydate']).apply(lambda x: x/np.timedelta64(1,'D'))
#Adding Day Use Room to the count
df_date['dtDif'] = np.where((df_date['ArrivalDate']==df_date['DepartureDate']), 1 , df_date['dtDif'])

#Setting Day Use Room count to ZERO
df_date['Rooms'] = np.where((df_date['ArrivalDate']==df_date['DepartureDate']), 0 , df_date['Rooms'])
df_date2 =pd.DataFrame(df_date.query('(dtDif > 0)'))

df_date2['Arrivals'] = np.where((df_date2['ArrivalDate']==df_date2['occupancydate']), 1 , 0)
df_date2['LOS'] = (df_date2['DepartureDate']-df_date2['ArrivalDate']).apply(lambda x: x/np.timedelta64(1,'D'))

# Calculating Revenue for the future transactions
df_date2['clcRev'] = np.where((df_date2['ArrivalDate']>=runDate), 1,0)
df_date2['clcRate'] = (df_date2['Rate']*df_date2['clcRev'])
df_date2['Revenue'] = df_date2['Revenue'].fillna(df_date2['LOS'] * df_date2['clcRate'])

# Identifying the Room Types based on Paid for room types
df_date2['RoomOccupied'].replace(rmDict, inplace=True)
df_date2['RoomOccupied'] = df_date2['RoomOccupied'].fillna(df_date2['RoomPaid'])
df_date2['RoomPaid'].replace(rmDict, inplace=True)
df_date2['RoomPaid'] = df_date2['RoomPaid'].fillna(df_date2['RoomOccupied'])
df_date2['RmType'] = np.where((df_date2['RoomPaid']!="PM"), df_date2['RoomPaid'], np.where((df_date2['RoomOccupied']!="PM"), df_date2['RoomOccupied'], df_date2['RoomPaid']))
#df_date2['RmType'] = df_date2['RmType'].fillna('Standard Room')

#RateCode
df_date2['RateCode'] = df_date2['RateCode'].fillna(df_date2['MarketCode'])

#Calculate Lead and Sharer details
df_date2['AvgLead'] =  (df_date2['ArrivalDate']-df_date2['CreationDate']).apply(lambda x: x/np.timedelta64(1,'D'))
df_date2['isSharer'] = np.where((df_date2['RateCode']=="SHARER"), 1, 0) 

#Calculate Arrival and Stayovers
df_date2['Arrivals'] = df_date2['Arrivals'] * df_date2['Rooms']
df_date2['StayOvers'] = np.where((df_date2['Arrivals']==0), 1, 0) 
df_date2['StayOvers'] = df_date2['StayOvers'] * df_date2['Rooms']

df_date2['DOW'] = df_date2['occupancydate'].dt.dayofweek
df_date2['DOW'].replace(DowDict, inplace=True)
df_date2['Month'] = df_date2['occupancydate'].apply(lambda x: dt.datetime.strftime(x,"%b"))
df_date2['Year'] = df_date2['occupancydate'].apply(lambda x: dt.datetime.strftime(x,"%Y"))

df_corp_db0 = df_date2.merge(df_rm_type, on='RmType', how='left')
df_corp_db0['RoomType'] = df_corp_db0['RoomType'].fillna('Standard Room')        
df_corp_db1 = df_corp_db0.merge(df_ms_type, on='MarketCode', how='left')        

# =============================================================================
# this step needs to be validated for all the hotels as this could be 
# the hotel specific practice. might be Dubai specific practice as well
# =============================================================================
#df_corp_db1['grpRev'] = np.where((df_corp_db1['MS_Type']=='Group'),  1, 0)

#np.where((df_corp_db1['RoomType']!='PM'), np.where((df_corp_db1['Revenue']==0),  df_corp_db1['Rate']

df_corp_db1['Revenue'] = np.where((df_corp_db1['Revenue']==0), np.where((df_corp_db1['RoomType']!='PM'), np.where((df_corp_db1['MS_Type']=='Group'), (df_corp_db1['Rate'] * df_corp_db1['LOS']), df_corp_db1['Revenue']), df_corp_db1['Revenue']), df_corp_db1['Revenue'])
# =============================================================================

df_corp_db1['CompanyName'] = df_corp_db1['CorporateName'].str.lower()
df_corp_db = df_corp_db1.merge(df_fnl_clst, on='CompanyName', how='left')        
df_corp_db['CompanyName'].replace(np.nan, "Non Corp", inplace=True)
df_corp_db['Cluster'].replace(np.nan, "Non Corporate", inplace=True)

#df_corp_db['CompanyName'].replace('', "Non Corporate", inplace=True)
#df_corp_db['Cluster'].replace('', "Non Corporate", inplace=True)

#df_corp_db['RevPD'] = df_corp_db['Revenue']/df_corp_db['LOS']
df_corp_db['RevPD'] = np.where(df_corp_db['LOS']>0, df_corp_db['Revenue']/df_corp_db['LOS'], df_corp_db['Revenue'])

# =============================================================================
# delcols = ['Revenue']
# df_corp_db = df_corp_db.drop(delcols,axis = 1)
# =============================================================================

df_corp_db2 = pd.DataFrame(df_corp_db.query('(occupancydate >= "2017-01-01" and occupancydate <= "2018-12-31")'))

#df_etl_data0 = pd.DataFrame(df_corp_db2.query('(Status != "CANCELLED" and Status != "NO SHOW")'))

df_corp_db2['Status']=np.where(df_corp_db2['Status'] == "CANCELLED", 0, np.where(df_corp_db2['Status']=="NO SHOW",0,1))

df_etl_data0 = pd.DataFrame(df_corp_db2)
#CancellationDate
df_etl_data0['spitLY'] = np.where(df_etl_data0['CreationDate']<=lyDate, 1, 0)
#
df_etl_data0['spitLY'] = np.where(df_etl_data0['CancellationDate']<=lyDate, 0, df_etl_data0['spitLY'])


# =============================================================================
# Group by with Corporate Cluster as well
# =============================================================================

df_grp_by_sum = df_etl_data0.groupby(['occupancydate', 'MarketSegment', 'MS_Cluster', 'MS_Type', 'RoomType', 'Cluster', 'DOW', 'Month', 'Year', 'isSharer', 'SourceCode', 'spitLY', 'Status', 'RateCode', 'CompanyName', 'ArrivalDate', 'DepartureDate'])[['Rooms', 'RevPD', 'Arrivals','StayOvers']].sum()

#df_grp_by_sum.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_SUM_'+ start_date +'.csv', sep=',', encoding='utf-8')

df_grp_by_avg = df_etl_data0.groupby(['occupancydate', 'MarketSegment', 'MS_Cluster', 'MS_Type', 'RoomType', 'Cluster', 'DOW', 'Month', 'Year', 'isSharer', 'SourceCode', 'spitLY', 'Status', 'RateCode', 'CompanyName', 'ArrivalDate', 'DepartureDate'])[['LOS', 'AvgLead']].mean()

#df_grp_by_avg.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_AVG_'+ start_date +'.csv', sep=',', encoding='utf-8')

df_etl_data1 = df_grp_by_sum.merge(df_grp_by_avg, on=['occupancydate', 'MarketSegment', 'MS_Cluster', 'MS_Type', 'RoomType', 'Cluster', 'DOW', 'Month', 'Year', 'isSharer', 'SourceCode', 'spitLY', 'Status', 'RateCode', 'CompanyName', 'ArrivalDate', 'DepartureDate'], how='left')

df_etl_data1.to_csv(outPath+'_Corp_'+ start_date +'.csv', sep=',', encoding='utf-8')

#df_etl_data = pd.DataFrame(df_etl_data1[['occupancydate', 'MarketSegment', 'RmType', 'Rooms', 'RevPD', 'Arrivals', 'LOS', 'AvgLead', 'isSharer', 'StayOvers', 'DOW', 'Month', 'Year', 'CompanyName', 'Cluster', 'RoomType', 'MS_Cluster', 'MS_Type']])

#df_etl_data.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_ETL_'+ start_date +'.csv', sep=',', encoding='utf-8')

# =============================================================================
# End of the Group by
# =============================================================================


# =============================================================================
# Group by without Corporate Cluster
# =============================================================================

#df_ypr_by_sum = df_etl_data0.groupby(['occupancydate', 'MarketSegment', 'MS_Cluster', 'MS_Type', 'RoomType', 'DOW', 'Month', 'Year', 'isSharer', 'spitLY',  'SourceCode','Status'])[['Rooms', 'RevPD', 'Arrivals','StayOvers']].sum()
#
#df_ypr_by_avg = df_etl_data0.groupby(['occupancydate', 'MarketSegment', 'MS_Cluster', 'MS_Type', 'RoomType', 'DOW', 'Month', 'Year', 'isSharer', 'spitLY',  'SourceCode', 'Status'])[['LOS', 'AvgLead']].mean()
#
#df_etl_ypr = df_ypr_by_sum.merge(df_ypr_by_avg, on=['occupancydate', 'MarketSegment', 'MS_Cluster', 'MS_Type', 'RoomType', 'DOW', 'Month', 'Year', 'isSharer', 'spitLY',  'SourceCode', 'Status'], how='left')
#
#df_etl_ypr.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_FOR_YPR_'+ start_date +'.csv', sep=',', encoding='utf-8')

# =============================================================================
# End of the Group by without corp
# =============================================================================





# =============================================================================
# Group by for Validation Report
# =============================================================================


#df_LY = pd.DataFrame(df_etl_data0.query('(occupancydate >= "2017-01-01" and occupancydate <= "2017-12-31")'))
#df_LY['date_LY'] = df_LY['occupancydate'] 
#
#df_TY = pd.DataFrame(df_etl_data0.query('(occupancydate >= "2018-01-01" and occupancydate <= "2018-12-31")'))
#df_TY['date_LY'] =   df_TY['occupancydate'].apply(lambda x: addYears(x, -1))
#
#
##df_TY[['date_LY','occupancydate']].head()
#
##df_TY.groupby([df_TY['occupancydate'].dt.month, df_TY['occupancydate'].dt.day])['Value'].shift()
#
#df_LY_sum = pd.DataFrame(df_LY.groupby(['date_LY', 'MarketSegment', 'MS_Cluster', 'RoomType', 'DOW', 'Month', 'Year', 'isSharer'])[['Rooms', 'RevPD', 'Arrivals','StayOvers']].sum())
#
#df_TY_sum = pd.DataFrame(df_TY.groupby(['occupancydate', 'date_LY', 'MarketSegment', 'MS_Cluster', 'RoomType', 'DOW', 'Month', 'Year', 'isSharer'])[['Rooms', 'RevPD', 'Arrivals','StayOvers']].sum())
#
#


#df_TY_LY= df_TY_sum.merge( df_LY_sum, on=['date_LY', 'MarketSegment', 'MS_Cluster', 'RoomType', 'DOW', 'Month', 'Year', 'isSharer'], how='left')
#
#df_TY_LY.head()
#
#df_TY_LY.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_Valid_'+ start_date +'.csv', sep=',', encoding='utf-8')











# =============================================================================


 
# =============================================================================

#
#df_corp_db= pd.DataFrame(df_etl_data)
#
## Room Nights Calculation
#df_Nights= pd.DataFrame(df_corp_db.query("RateCode not in  ('HOUSE','SHARER','ZERO')"))
#df_Nights.dropna(subset=['CompanyName'], inplace=True)
#df_Nights = df_Nights.reset_index(drop=True)
#df_Nights['Month'] = df_Nights['occupancydate'].dt.month
#df_Nights['Year'] = df_Nights['occupancydate'].dt.year
#df_Nights1 = pd.DataFrame(df_Nights,columns=['Year', 'Month', 'Cluster', 'CompanyName','Rooms'])
#sum_nights = df_Nights1.groupby(['Cluster', 'CompanyName', 'Year', 'Month'])
#sum_nights1 = sum_nights.sum().reset_index()
#total_sum_nights = pd.DataFrame(sum_nights1)
#total_sum_nights.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_sum_Nights_25JUN18.csv', sep=',', encoding='utf-8')
#
## Room Revenue Calculation
#df_Revs= pd.DataFrame(df_corp_db)
#df_Revs.dropna(subset=['CompanyName'], inplace=True)
#df_Revs = df_Revs.reset_index(drop=True)
#df_Revs['Month'] = df_Revs['occupancydate'].dt.month
#df_Revs['Year'] = df_Revs['occupancydate'].dt.year
#df_Revs1 = pd.DataFrame(df_Revs,columns=['Year', 'Month', 'Cluster', 'CompanyName','RevPD'])
#sum_Revs = df_Revs1.groupby(['Cluster', 'CompanyName', 'Year', 'Month'])
#sum_Revs1 = sum_Revs.sum().reset_index()
#total_sum_Revs = pd.DataFrame(sum_Revs1)
#total_sum_Revs.to_csv('G:/Revnomix_backup/GDrive/MAF/Kempinsky/KMOE_sum_Revs_25JUN18.csv', sep=',', encoding='utf-8')
#
#
#df_corp_prod = total_sum_nights.merge(total_sum_Revs, on=['Cluster', 'CompanyName', 'Year', 'Month'], how='left')        
#
#df_corp_prod.to_csv('G:/GDrive/RoomTypeYielding_Tool/CPG_2017_Corp_Prod_19APR18.csv', sep=',', encoding='utf-8')
#

#sum_nights = df_Nights1.groupby(['Cluster', 'CompanyName', 'Year', 'Month']).Rooms.apply(lambda x: x.iat[0].sum())







    
#delcols = ['StrDt','EndDt', 'dtDif']
#df_date3 = df_date2.drop(delcols,axis = 1)

#df2.groupby(['A', 'B']).numbers.apply(lambda x: x.iat[0].sum())
#df['day_of_week'] = df['my_dates'].dt.dayofweek
#days = {0:'Mon',1:'Tues',2:'Weds',3:'Thurs',4:'Fri',5:'Sat',6:'Sun'}
#df['day_of_week'] = df['day_of_week'].apply(lambda x: days[x])

"""
Remove 
1. Cancelled Bookings
2. Remove Sharer from counting Room Nights but
3. Include Sharer in counting Revenue
4. Remove PM/PF from counting Room Nights but
5. Include PM/PF in counting Revenue


"""


