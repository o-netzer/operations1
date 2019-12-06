# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 21:29:44 2017

@author: netzer

Given several input parameters (see USER INPUT section, the variable "pins" can
be left empty) this script produces a standard card import xml which is ready
to be imported into the db. The following steps are performed:
    
1) consistency check: length of card numbers and pin codes equal?
2) consistency check: does retail commission exist in db?
3) store value from retail commission
4) retrieve next valid number for card import
5) build xml from string variable and edit header with correct values
6) for each card number: write respective data into xml-string
7) store file on file system
"""


import sys, time, os
from XMLs import card_import_xml
from selects import retailer_provision, last_crd_imp_of_brandp
from mytoolbox import db_lookup, selectCountryConnection, increase_consecutive_no
from xml.etree import ElementTree as ET



########################USER INPUT#############################################
prefix = '011'#kann beliebig verändert werden, falls nötig
midfix = '21'#kann beliebig verändert werden, falls nötig
country = 'CHE'
brandP = 'XXXX' #ad netzer: könnte man weglassen und brandP in retailer_provision query neu schreiben
retailer = 'RXXX'# ist hier nur notwendig wegen Check der Retailer Provision!
vens_mit_erster_crd = 1 #1: alle vens mit erster Kartennummer der Liste bilden, sonst 0
vens_mit_letzter_crd = 0 #1: alle vens mit letzter Kartennummer der Liste bilden, sonst 0
#beide 0: alle vens mit jeweiliger Kartennummer bilden
ean = '4049206029404'

card_nos = '''
1000000561507930
1000000561508027
1000000561508124
1000000561508221
1000000561508318
1000000561508415
1000000561508512
1000000561508609
1000000561508706
1000000561508803
'''
pins = '''
2ZK4U26555XXXXXX
2Z6A233555XXXXXX
2ZY3H6Z555XXXXXX
2ZX3DUN555XXXXXX
2ZZW7FD555XXXXXX
2ZW2X3L555XXXXXX
2ZU7AMJ555XXXXXX
2ZEV6VS555XXXXXX
2ZRM461555XXXXXX
2ZDLF45555XXXXXX

'''
########################USER INPUT#############################################


card_nos_list = card_nos.split()
print(card_import_xml)

pin_list = pins.split()
print(pin_list)

if len(card_nos_list) <> len(pin_list):
    if len(pin_list) <> 0:
        sys.exit('''WARNING: Number of cards does not match number of pins!!!
    Please check input data! Program is terminated.
    ''')
else:
    pass

first_cardno = card_nos_list[0]
last_cardno = card_nos_list[-1]


#this is how it should looke like:
#<card><crd_no>6376500243653718</crd_no><pin></pin><crd_value>25</crd_value><prt>ZXXX</prt><brand>ZXXX12</brand><ven>0114049206025109210006500243653718</ven><year>2017</year><week>30</week><pen></pen></card>
cursor = selectCountryConnection(country)
print(cursor)
adopted_select = (retailer_provision.replace('retailer',retailer)).replace('produktean',ean)
print(adopted_select)


provision_details = db_lookup(cursor, adopted_select)

#################Retailer Commission exists?#########################
#example
#[('RROX', 'CUAX21', 'C&B 25-150 EUR', 5.0, '1111101111011', 0.0, datetime.datetime(2099, 12, 31, 23, 59, 59))]
if len(provision_details) <> 1:
    sys.exit("There is someting wrong with the retailer commission! Either it doesn't exist, or it is not unique. Please check!" )
#################Retailer Commission exists?#########################

prod_short, prod_long, prod_val = provision_details[0][1], provision_details[0][2], provision_details[0][5]
print(brandP)
print(prod_short)
print(prod_long)
print(prod_val)


adopted_select = last_crd_imp_of_brandp.replace("brandp",brandP)
print(adopted_select)
last_import_details = db_lookup(cursor, adopted_select)
cursor.close()
print(last_import_details)

try:
    numbering =  str(last_import_details[0][7])
    print('Name of last BrandP-Import: ' + str(numbering))
    fln = last_import_details[0][7][-10:-4]
except IndexError:
    print('No card import of ' + brandP + ' yet.' )
    fln = '000000'

   

current_date = time.strftime("%Y%m%d")
import_filename = brandP + '_crd_imp__' + str(current_date) + '__' + str(increase_consecutive_no(fln, 6)) + '.xml'
print('new filename: ' + str(import_filename))

tree = ET.ElementTree(ET.fromstring(card_import_xml))
file_name = tree.find('header/file_name')
file_name.text = import_filename
print('Insert file name' + str(import_filename))
export_date = tree.find('header/export_date')
export_date.text = time.strftime("%Y-%m-%d")
print('Insert export date = ' + str(export_date.text))
cards = tree.find('cards')
#


current_week = time.strftime("%W") #retrieve current week
print("current week: " + str(current_week))
num_lines = len(card_nos_list)
counter = 0
for i in range(num_lines):
    card = ET.SubElement(cards, 'card')
    
    card_no = ET.SubElement(card, 'crd_no')
    card_no.text = card_nos_list[i]
    print(card_no.text)
    
    pin = ET.SubElement(card, 'pin')
    try:
        pin.text = pin_list[i]
    except IndexError:
        pin.text = ''

    card_value = ET.SubElement(card, 'crd_value')
    card_value.text = str(prod_val)
    
    prt = ET.SubElement(card, 'prt')
    prt.text = brandP
    
    brand = ET.SubElement(card, 'brand')
    brand.text = prod_short
    
    ven = ET.SubElement(card, 'ven')
    if vens_mit_erster_crd == 1:
        ven.text = prefix + ean + midfix + first_cardno
    elif vens_mit_letzter_crd == 1:
        ven.text = prefix + ean + midfix + last_cardno
    else:
        ven.text = prefix + ean + midfix + card_nos_list[i]
    
    jahr = ET.SubElement(card, 'year')
    jahr.text = current_date[0:4]
    
    woche = ET.SubElement(card, 'week')
    woche.text = current_week
    
    counter = counter + 1



record_count = tree.find('header/record_count')
record_count.text = str(num_lines)

production_path = r"Z:\ITdep\Betriebe\Kartennummern_Erstellungen"
import_path = os.path.join(production_path, country, 'Produktion ' + current_date[0:4], 'In_Arbeit')
if not os.path.exists(import_path):
    os.makedirs(import_path)
    print(import_path + ' angelegt')

import_path = os.path.join(import_path, import_filename)

tree.write(import_path, encoding='utf8', method='xml')
print('done')



