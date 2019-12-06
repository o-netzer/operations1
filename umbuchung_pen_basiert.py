# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 22:18:27 2016

@author: netzer

With input a set of logistic entities called "PENs" card metadata in these PENs
are rebooked to some other retail partner ("new_retailP". see input section).
Following steps are performed:
1) check if the input set contains other numbers than PENs
2) retrieve card numbers and other metadata belonging to the PENs from db
3) retrieve new import number from db
4) start writing data into XML template (from string) keeping track of count
5) zip xml file and send it to sftp-server and unzip
6) audio signalling ask user if the logisitcs import should be startet
7) starting import script on ftp
8) asking the db for the success of the operation, stopping otherwise
9) checking for rare exceptions, stopping otherwise
10) audio signalling ask user if export of data to new partner should be performed
11) starting script for the export on ftp
12) retrieve results o fthe operation from db
13) audio signalling the end of the script  
"""

import os, time, sys, gzip, shutil
from selects import pen_abfrage, last_pcl_import, last_card_export
from mytoolbox import selectCountryConnection, db_lookup, increase_consecutive_no
from XMLs import rrem_xml
from xml.etree import ElementTree as ET
from sftp import sftp
import winsound




#####################input########################################
#es können auch doppelte PENs hier eingegeben werden- kein Problem!!!
pens = set(['9206022467213940200414001435111111', '8206022467213940200414001435111111'])
brand = 'TLLL' #'VerschBrands' kann auch mit einem anderen Namen ersetzt werden.
#unter diesem Namen wird das RREM.xml auf Z:\UV\Betriebe\Korrekturen\.. abgelegt
new_retailP = 'NETZ' #new retail Partner to which data is to be sent
country = 'DEU'
pos_ = 'KW13' #kann durch etwas anderes ersetzt werden
######################input########################################

#################PEN check#########################################
not_a_pen = []
for pen in pens:
    if not pen.startswith('999'):
        not_a_pen.append(pen)

if not_a_pen <> []:
    print('The following numbers are NOT valid PENs:')
    print(not_a_pen)
    sys.exit('Please review your list of PENs!')
else:
    print('PENs OK!')
#################PEN check#########################################

#################################Retrieve card numbers and other metadata from db #####
string_of_pens = ''

for i in pens:
    string_of_pens += ("'"+str(i)+"',")

string_of_pens = string_of_pens[:len(string_of_pens)-1]


query_overall = pen_abfrage.replace("chd.chd_pen in ()",
                                   "chd.chd_pen in (" + string_of_pens + ")")

print(query_overall)


cursor = selectCountryConnection(country)
overall = db_lookup(cursor, query_overall)
headers = []
for i in cursor.description:
    headers.append(i[0])
print('result column names:')
print(headers)
print(overall)
    
print("starting to write PCL xml ...")

resultset5 = db_lookup(cursor, last_pcl_import)
numbering =  str(resultset5[0][7])
print('Name of last PCL-Import: ' + str(numbering))
fln = resultset5[0][7][-10:-4]



current_date = time.strftime("%Y%m%d")
rrem_filename = 'RNET_pcl_imp__' + str(current_date) + '__' + str(increase_consecutive_no(fln, 6)) + '.xml'
print('new filename: ' + str(rrem_filename))


tree = ET.ElementTree(ET.fromstring(rrem_xml))
file_name = tree.find('header/file_name')
file_name.text = rrem_filename
print('Insert file name' + str(rrem_filename))
export_date = tree.find('header/export_date')
export_date.text = time.strftime("%Y-%m-%d")
print('Insert export date = ' + str(export_date.text))
p_units = tree.find('packing_units')



num_lines = len(overall)
counter = 0
for i in range(num_lines):
    packing_unit = ET.SubElement(p_units, 'packing_unit')

    ven = ET.SubElement(packing_unit, 'ven')
    ven.text = overall[i][0]
    
    ean = ET.SubElement(packing_unit, 'ean_no')
    ean.text = overall[i][1]
    
    prt = ET.SubElement(packing_unit, 'prt')
    prt.text = new_retailP
    
    pos = ET.SubElement(packing_unit, 'pos')
    pos.text = pos_

    counter = counter + 1
#
#
#
record_count = tree.find('header/record_count')
if counter == num_lines:
    record_count.text = str(num_lines)
else:
    sys.exit('not each VEN written into XML')

production_path = r"Z:\UV\Betriebe\Korrekturen"
current_year = current_date[:4]
rrem_path = os.path.join(production_path, country, current_date +  '_'+ brand + '_' + new_retailP)
if not os.path.exists(rrem_path):
    os.makedirs(rrem_path)
print(rrem_path + ' angelegt')

rrem_path = os.path.join(rrem_path, rrem_filename)
tree.write(rrem_path)
#
#
#
#
# ###############zip xml file and send it to sftp-server and unzip########################   
print(os.access(rrem_path, os.F_OK))

with open(os.path.abspath(rrem_path)) as f_in, gzip.open(os.path.abspath(rrem_path + '.gz'),'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)




sftp.cwd('/oop/ftpshoot/homecoming/' + str(country) + '/RXXX/PRODUKTION/IN')

sftp.put(rrem_path + '.gz')
print(sftp.listdir())

sftp.execute('gzip -d /oop/ftpshoot/homecoming/' + str(country) + '/RXXX/PRODUKTION/IN/' + rrem_filename + '.gz')
print(sftp.listdir())
 ###############zip xml file and send it to sftp-server and unzip########################   

##################################AUDIO SIGNAL###############################################
winsound.PlaySound('C:\Users\Public\Music\Sample Music\Music_Censor.wav', winsound.SND_FILENAME)
##################################AUDIO SIGNAL###############################################


 ###############start pcl-import and/or card data export################################# 

start_pcl = raw_input('Do you want to start the PCL-Import? yes/no: ')
if start_pcl == 'yes':
    print('PCL-Import started ...')
#    logging.info('PCL-Import started ...')
    sftp.execute('cd /oop/poss/live_server/' + str(country) + '/r_scheduler/; ./start_perlscript RNET PICKLISTIMPORT user userpwd')
    print('./start_perlscript RNET PICKLISTIMPORT user userpwd')

else:
    sys.exit('Program terminated by user before PCL-Import.')
#    logging.info('Program terminated by user before PCL-Import.')
    

cursor = selectCountryConnection(country)
resultset4 = db_lookup(cursor, last_pcl_import)
#logging.info(resultset4)
if resultset4[0][6] == 'SUCCESS':
    print('The products have been picklisted successfully. No Errors!')
    print(str(resultset4[0][8]) + ' VENs!')
else:
    print('NOT SUCCESSFUL. Please check manually and restart this procedure!')
    sys.exit('Good bye!')


##################################AUDIO SIGNAL###############################################
winsound.PlaySound('C:\Users\Public\Music\Sample Music\Music_Censor.wav', winsound.SND_FILENAME)
##################################AUDIO SIGNAL###############################################

##################Ausnahme bei RKAM und RPCC###########################################
if new_retailP in ('RPCC','RKAM'):
    sys.exit('Unfortunately data to  ' + new_retailP + ' should not be exported by this Python program. Please proceed the last step manually!')
##################Ausnahme bei RKAM und RPCC###########################################

start_export = raw_input('Do you want to start the Card Data Export? yes/no: ')
if start_export == 'yes':
    print('Card Data Export started ...')
#    logging.info('Card Data Export started ...')
    command_string = './start_perlscript ' + new_retailP + ' CARDDATAEXPORT user userpwd'
    print(command_string)
    sftp.execute('cd /oop/poss/live_server/' + str(country) + '/r_scheduler/;' + command_string)

else:
    sys.exit('Program terminated by user before Card Data Export.')
#    logging.info('Program terminated by user before Card Data Export.')

last_card_export = last_card_export.replace('RetailP', new_retailP)
print(last_card_export)
resultset5 = db_lookup(cursor, last_card_export)
#logging.info(resultset5)
if resultset5[0][6] == 'SUCCESS':
    print('The products have been exported successfully. No Errors!')
    print(str(resultset5[0][8]) + ' cards!')
else:
    print('NOT SUCCESSFUL. Please check manually and restart this procedure!')
    sys.exit('Good bye!')
cursor.close()  
 ###############start pcl-import and/or card data export#################################   
sftp.close()

##################################AUDIO SIGNAL###############################################
winsound.PlaySound('C:\Users\Public\Music\Sample Music\Music_Censor.wav', winsound.SND_FILENAME)
##################################AUDIO SIGNAL###############################################

        
