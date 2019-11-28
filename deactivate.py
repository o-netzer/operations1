# -*- coding: utf-8 -*-
"""
Created on Wed Mar 07 19:23:18 2018

@author: netzer

The purpose of this script is to provide a handy way for a fast and secure
deactivation of cards belonging to 1 or more products of 1 brand partner. It
outputs finally a sequence of deactivation XMLs which can subsequently be
used to perform the deactivation.

The script takes 5 input parameters including a SQL query for an Oracle data
base ("recherche", see input section). Then it goes on by performing the
following steps:
1) retrieving the data from the database and storing it in a pandas dataframe
2) filtering the data in various ways and checking if only 1 brand partner is
   involved
3) creating a folder in the working directory using key parameters
4) saving an Excel workbook with query results if desired
5) using pandas groupby to display aggregated data in the IPython console
   (how many card numbers by product and status)
6) querying the db again to find out the consecutive number for the next
   deactivation
7) writing the deactivation XMLs product by product and saving the files in
   the working directory under the correct naming
"""

import  sys, time, os
import pandas as pd
from pandas import ExcelWriter
pd.set_option('display.expand_frame_repr', False)
from selects import  last_deact
from mytoolbox import selectCountryConnection, db_lookup, increase_consecutive_no
from XMLs import deactivate
from lxml import etree
from xml.etree import ElementTree as ET



############################# INPUT Parameters ################################
brand_code = 'BHHR'#insert a brand partner abbreviation
country = 'DEU' #insert country abbreviation DEU, CHE or AUT
store_xls_snapshot = 'no'# if this is flagged 'yes', the script stores a db
#snapshot of the products before the deactivation in an excel workbook in
# Z:\ITdep\Betriebe\Korrektur; 'no' is recommended when running the script on
# your local pc
recherche = '''
SELECT ...
'''.encode('utf-8') #insert your query here (outcome must include at least
#'CARDNUMBER' 'EAN', and 'PARTNERCODE'!!!)
#don't include ";" at the end of the query and avoid "order by" statements
# (for performance reasons); best you take Schorsch's Karten-Recherche and edit
work_dir = r'Z:\ITdep\Betriebe\Korrektur' # base path of the location where
# generated files will be stored 
############################# INPUT Parameters ################################


##################STOPWATCH####################################################
import timeit
start_time = timeit.default_timer() #start time of computation
##################STOPWATCH####################################################



############### START: Perform SQL-query and filter result in various ways ####
cursor = selectCountryConnection(country) #set db cursor
recherche_result = db_lookup(cursor, recherche)
print('Spaltennamen: ')
names = [i[0] for i in cursor.description] #retrieve column names from cursor
print(names)
print('\n')

#define data frame from query result:
df = pd.DataFrame(recherche_result, columns=names)
# filter unique brand partners
df_unique_brands = df[['PARTNERCODE']].drop_duplicates()
# (we want to avoid that more than 1 brand partner is involved)
print("involved brand partner: " + df_unique_brands['PARTNERCODE'])
print('\n')
##############check if there is only 1 brand partner involved##################
for b_code in list(df_unique_brands['PARTNERCODE']):
     #if another than input brand_code is involved ...
    if b_code <> brand_code:
        sys.exit("Program ends, because of the involvement of more than 1 brand partner. Don't do that! It might get messy!")
##############check if there is only 1 brand partner involved##################

#create list of unique products
df_unique_products = df[['EAN','PRODUKTCODE']].drop_duplicates()
eans = list(df_unique_products['EAN'])
anzahl_versch_prod = len(df_unique_products) # store number of unique products
############### START: Perform SQL-query and filter result in various ways ####


###################Create Folder in Z:\ITdep\Betriebe\Korrektur\country
# and save query result (without duplicates)#############
work_folder_name = '_' + brand_code + '_Deakt' #will contain brand code and
# Deakt, like e.g. 20180426_THHL_Deakt_THHL16_THHL14

##### if there are less than 3 EANs (products), write brand codes into folder
# name. Otherwise add '---' #####
for prod in list(df_unique_products['PRODUKTCODE'])[:3]:
    work_folder_name += '_' + prod
    

if anzahl_versch_prod > 3:
    work_folder_name += '_ _ _'
    

current_date = time.strftime("%Y%m%d")
work_folder = os.path.join(work_dir, country, current_date + work_folder_name)
os.mkdir(work_folder)
print(work_folder)
print('new working folder created: ' + work_folder + '\n')
##### if there are less than 3 EANs (products), write brand codes into folder
# name. Otherwise add '---' #####


############### go to newly created folder and save Excel workbook with query
# result ##################
os.chdir(work_folder) #following activities take place in work folder

df_unique = df.drop_duplicates(subset=['CARDNUMBER','EAN','PRODUKTCODE', 'STATUS'])

if store_xls_snapshot == 'yes':
    writer = ExcelWriter(brand_code + '_Total'+'.xlsx', engine='xlsxwriter')
    df_unique.to_excel(writer, sheet_name='Sheet1', na_rep='',
                       float_format=None, header=True, index=True,
                       index_label=None, startrow=0, startcol=0,
                       encoding='utf-8', verbose=True)
    writer.save()
############### go to newly created folder and save Excel workbook with query
# result ##################


###################Create Folder in Z:\ITdep\Betriebe\Korrektur\country
# and save query result (without duplicates)#############


##################### Show aggregated Data in console output ##################################################
print(4*'XXXXXXXXXXXXXXX')
df_summary = (df[['CARDNUMBER','EAN','PRODUKTCODE', 'STATUS', 'DELIVERY_PARTNER']].drop_duplicates(subset=['CARDNUMBER','EAN']).fillna('None'))
#print(df_summary)
#print(df.describe)
print(df_summary[['CARDNUMBER','EAN', 'STATUS', 'DELIVERY_PARTNER']].groupby(['EAN','STATUS','DELIVERY_PARTNER']).agg(['count']))

print((4*'XXXXXXXXXXXXXXX') + '\n')
##################### Show aggregated Data in console output ##################################################

#sys.exit()
print('\n')
####Retrieve consecutive number of last tx_sld for GGEM and set new ###########################
resultset1 = db_lookup(cursor, last_deact)

try:
    print(resultset1[0][:])
    print('\n')
    numbering =  str(resultset1[0][9]) #retrieve filename of last RRRT deactivation (PPR_INTERFACE_FILE_NAME)
    fln = resultset1[0][9][-10:-4] #retrieve last consecutive number of PPR_INTERFACE_FILE_NAME
    print('Name of last tx_sld Import: ' + str(numbering) + '\n')
    if resultset1[0][6] in ('SUCCESS', 'ERROR', 'NOT_FOUND'):
        neue_fln = increase_consecutive_no(fln, 6)
        print('New consecutive number will be: ' + neue_fln + '\n')
    else:
        neue_fln = fln
        print('New consecutive number will be equal to the old: ' + fln + '\n' )
except IndexError:
    neue_fln = '000001'
####Retrieve consecutive number of last tx_sld for GGEM and set new ###########################


################## WRITE DEACTIVATION XMLS, Product By Product#################
print('--------------------------')
for i in eans:
    print('creating xml with ean= ' + i + '\n')
    df3 = df_summary[['CARDNUMBER','EAN', 'STATUS']][df_summary['EAN'] == i]
    df4 = df3[(df3['STATUS'] == 'ON_STOCK') | (df3['STATUS'] == 'DELIVERED')]
    #df4 is dataframe containing only lines with status = 'DELIVERD' or 'ON_STOCK' - which are to be deactivated
#
    newxml = etree.fromstring(deactivate) #read in the deactivation XML template
    new_file_name = newxml.find('header/file_name').text =  'RRRT_tx_deact__' + time.strftime("%Y%m%d") +'__' + neue_fln +  '.xml'
    print(new_file_name)

    newxml.find('header/export_date').text = time.strftime("%Y-%m-%d")
    print(newxml.find('header/export_date').text + '\n')
    transactions = newxml.find('transactions')
    
    counter = 0    
    for line in df4.iterrows():

        tx = etree.SubElement(transactions, 'tx')
        
        typ = etree.SubElement(tx, 'type') #use German 'typ' instead of Python key-word 'type'
        typ.text = 'DEACTIVATED'
                
        card_no = etree.SubElement(tx, 'crd_no')
        card_no.text = line[1][0]
        
        ean = etree.SubElement(tx, 'ean_no')
        ean.text = i
        
        counter = counter + 1
#        print(counter)
        
    newxml.find('header/record_count').text = str(counter)
#    print(newxml.find('header/record_count').text)
    tree = ET.ElementTree(newxml)
    tree.write(os.path.join(work_folder, new_file_name), encoding='utf-8', method='xml')
    neue_fln = increase_consecutive_no(neue_fln, 6)
    print('done' + '\n')

print('done writing XMLs' + '\n')
################## WRITE DEACTIVATION XMLS, Product By Product#################

##################STOPWATCH###############################################################
print('duration: ' + str((timeit.default_timer() - start_time)/60.0) + ' min')
##################STOPWATCH###############################################################




