# -*- coding: utf-8 -*-
"""
Created on Sat May 27 23:34:27 2017

@author: netzer


This script takes a standard card import xml together with brand partner
abbreviation, country abbreviation and a split limit as input parameters
and splits the input xml according to the limit (max no. of products) into
n xmls:

    n = int((total no. of products in input xml) / limit) if 
    (total no. of products in input xml) / limit is an integer
    n + 1 otherwise

The splitted xmls are stored in the same location "local_test_path"
as the given xml.
"""


from XMLs import card_import_xml
from mytoolbox import padding_number
import os
import time
from math import ceil
import sys
from xml.etree import ElementTree as ET


#
# 
#
#
#
##################INPUT###############################################################
local_test_path = r"Z:\UV\Betriebe\Kartennummern_Erstellung\DEU\Prod 2019\In_Arbeit\original"

outer_filename = r'THUL_crd_imp__20190425__000069.xml' #insert filename

brandp = 'THUL' #Insert name of Brand Parnter, e.g. 'AMAL', 'GOLG'
country = 'DEU' #retailer country abbreviation (DEU,CHE,AUT)
limit = 45000 # maximum number of products in a split xml (except the last splitted file)
##################INPUT###############################################################


##################STOPWATCH###############################################################
import timeit
start_time = timeit.default_timer() #start time of computation
##################STOPWATCH###############################################################

xml_file = os.path.join(local_test_path,outer_filename)

tree = etree.parse(xml_file)
file_name, export_date, record_count = (tree.find('header/file_name')).text, (tree.find('header/export_date')).text,(tree.find('header/record_count')).text
print(file_name)
print(export_date)
print(record_count)


no_of_split_files = int(ceil(int(record_count)/float(limit)))
print('no of splitted XML files: ' + str(no_of_split_files))


     
products = (element for _, element in etree.iterparse(xml_file, tag='card'))


for i in range(1,no_of_split_files+1):

    newxml = etree.fromstring(card_import_xml)
    
    new_file_name = newxml.find('header/file_name').text =  brandp + '_crd_imp_' + time.strftime("%Y%m%d") +'__' + padding_number(i) + '.xml'
    print(new_file_name)

    newxml.find('header/export_date').text = time.strftime("%Y-%m-%d")
    print(newxml.find('header/export_date').text)

    newxml.find('header/record_count').text = str(limit)
    print(newxml.find('header/record_count').text)
    
    cards = newxml.find('cards')

    counter = limit
    
    while counter:
        p = next(products, None) #None is the default value for when the sequence is done
        if p is None:
            newxml.find('header/record_count').text = str(int(record_count)-limit*(no_of_split_files-1))
            print(newxml.find('header/record_count').text)
            break
        
        card = etree.SubElement(cards, 'card')    
        
        crd_no = etree.SubElement(card, 'crd_no')
        crd_no.text = p.findtext('crd_no')
        
        
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
        
        counter = counter - 1
        

    tree = ET.ElementTree(newxml)
    tree.write(os.path.join(local_test_path, new_file_name), encoding='utf-8', method='xml')

    


##################STOPWATCH###############################################################
print('duration: ' + str((timeit.default_timer() - start_time)/60.0) + ' min')
##################STOPWATCH###############################################################