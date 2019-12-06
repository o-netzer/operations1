# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:34:04 2018

@author: netzer

Given a text file (or list) containing card numbers which are already present in the
DB (this may be a result of the application of card_data_import_check.py), the products in
a card data import file should be deleted before the import into the db is performed.

This script takes file name, path and the mentioned text file as inputs and deletes
all the products in the xml containing those card numbers and outputs a cleaned
version of the file to be imported.
"""


from XMLs import card_import_xml
import os
import time
from math import ceil
import sys
from xml.etree import ElementTree as ET


##################INPUT###############################################################
xml_path = r"R:\ITdep\Betriebe\Kartennummern\CHE\Productions\Live" #path to file which is to be cleaned
outer_filename = r'ZALL_crd_imp__20190523__000001.xml' #insert name of file to be cleaned
check_results = r'check_result_ZALL_crd_imp__20190523__000001.txt' #insert filename for (new) cleaned file
brandp = 'ZALL' #Insert name of Brand Parnter, e.g. 'AMAA', 'GOGG
country = 'CHE' #retailer country abbreviation (DEU,CHE,AUT)

########################either fill in list OR use check_result file ###################################
f = open(os.path.join(xml_path,check_results), 'r')
cleaning_list =  f.readlines()
cleaning_list = [numbers.strip() for numbers in cleaning_list]
#insert list here if text file containing card numbers does not exist:
#cleaning_list = ['0491699066932000', '0491699066932000', '0491699066932000']
prods_2b_elim = len(cleaning_list) #Anzahl der Produkte, die aus Import File eliminiert werden sollen
########################either fill in list OR use check_result file ###################################
##################INPUT###############################################################

##################STOPWATCH###############################################################
import timeit
start_time = timeit.default_timer() #start time of computation
##################STOPWATCH###############################################################


xml_file = os.path.join(xml_path,outer_filename)


tree = etree.parse(xml_file)
file_name, export_date, record_count = (tree.find('header/file_name')).text, (tree.find('header/export_date')).text,(tree.find('header/record_count')).text
print(file_name)
print(export_date)
print(record_count)

products = (element for _, element in etree.iterparse(xml_file, tag='card'))


######################open new xml and got to "card"-tag###################################################
newxml = etree.fromstring(card_import_xml)

new_file_name = newxml.find('header/file_name').text = outer_filename

#new_file_name = newxml.find('header/file_name').text =  brandp + '_crd_imp_' + time.strftime("%Y%m%d") +'__' + '000000' + '.xml'
print(new_file_name)

newxml.find('header/export_date').text = time.strftime("%Y-%m-%d")
print(newxml.find('header/export_date').text)

new_record_count = int(record_count) - prods_2b_elim
newxml.find('header/record_count').text = str(new_record_count)
print(newxml.find('header/record_count').text)

cards = newxml.find('cards')
######################open new xml and got to "card"-tag###################################################

counter = int(record_count)
    
while counter:
    p = next(products, None) #None is the default value for when the sequence is done
    if p is None:

        break

    else:
        item = p.findtext('crd_no')
        if item not in cleaning_list:
                                   
            card = etree.SubElement(cards, 'card')    
            crd_no = etree.SubElement(card, 'crd_no')
            crd_no.text = item
        
            ven = etree.SubElement(card, 'ven')
            ven.text = p.findtext('ven')
            
            pen = etree.SubElement(card, 'pen')
            pen.text = p.findtext('pen')
            
            prt = etree.SubElement(card, 'prt')
            prt.text = p.findtext('prt')
            
            brand = etree.SubElement(card, 'brand')
            brand.text = p.findtext('brand')
                    
            week = etree.SubElement(card, 'week')
            week.text = time.strftime("%W")
            
            year = etree.SubElement(card, 'year')
            year.text = time.strftime("%Y")
            
            crd_value = etree.SubElement(card, 'crd_value')
            crd_value.text = p.findtext('crd_value')
        
        else:
            print(item + ' eliminated')
            
        counter = counter - 1

no_of_prods = newxml.find('header/record_count').text
print('Number of products written into new import file: ' + str(no_of_prods))
f.close()


tree = ET.ElementTree(newxml)
tree.write(os.path.join(xml_path, '___' + outer_filename), encoding='utf-8', method='xml')


##################STOPWATCH###############################################################
print('duration: ' + str((timeit.default_timer() - start_time)/60.0) + ' min')
##################STOPWATCH###############################################################
print('a new clean version of the xml is available!')