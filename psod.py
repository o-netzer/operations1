# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 17:17:38 2018

@author: netzer

This script takes 2 reports (csv, xml) as input.
It parses the xml for certain reference numbers
and checks each if it is contained in the csv
printing a remark for each number not contained
in the csv.
"""

import xml.etree.ElementTree as ET
import os
import csv


##################### I N P U T #######################################################################

ord_xml_path = r'C:\Users\netzer\Documents\Tagesgeschaeft\20190411\20190404082201_PSOA_txy_order__20190404__006640.xml'

#Report aus AskMySQL: auszuführen vom Datum der Fehlermail bis zum heutigen Tag
report_path = r'C:\Users\netzer\Documents\Tagesgeschaeft\20190411\MaggentaResultSet.csv'

##################### I N P U T #######################################################################


############################ Make dictionary of report, key=reference #################################
report = dict()
with open(report_path, 'r') as f:
    csv_reader = csv.reader(f,delimiter=';')
    for line in csv_reader:
        report[line[1]] = line[:]
############################ Make dictionary of report, key=reference #################################

############################# Open Order XML ##########################################################
print(os.path.dirname(ord_xml_path))


tree = ET.parse(ord_xml_path)
root = tree.getroot()
############################# Open Order XML ##########################################################


counter = 0
refnummern = []

#for i in root.findall('./error/err_content'):   
for i in root.findall('./orders/order'):
    referenznummer = i.find('reference')
    if referenznummer.text in report:
        counter = counter + 1
        print(str(counter) + ': ', referenznummer.text + ' generiert in Maggenta.')
        #print('generated: ', report[referenznummer.text])
        refnummern.append(referenznummer.text)
    else:
        artikel = i.find('order_its/order_it/article_number')
        wert = i.find('order_its/order_it/value')
        qty = i.find('order_its/order_it/quantity')
        print('not generated: ', referenznummer.text, artikel.text, wert.text, qty.text)


