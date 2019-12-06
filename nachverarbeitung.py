# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 22:51:28 2017

@author: netzer

The script takes an xml filename of a file on an ftp server containing
transaction errors as input and - depending on the type of error (error_text)
selected -  it processes the failed items once more in several steps.
1) creating a new working directory
2) searching for the error file on the ftp server
3) zipping and transferring the file to the working directory, and unzipping
4) asking the relevant db for the next processing number
5) creating a new import file and naming it correctly according to the db
6) parsing relevant data from err file and write it to new import file, including
   correct file naming, product count, product meta-data and date
6) zipping and transferring the new import file and sending it to a folder on the
   ftp, unzipping it
7) start script on ftp for importing data into the db
8) start another script on ftp for further processing
"""


import sys
import os, time, zipfile, gzip, shutil
from sftp import sftp
from XMLs import tx_solds
from mytoolbox import selectCountryConnection, db_lookup, increase_consecutive_no
from selects import last_tx_sld_imp



#Achtung: Voraussetzung ist hier, daß die Karten auf STATUS GELIEFERT stehen
#########################INPUT#########INPUT##########################################
tx_sold_file = r'RHWG_tx_sld__20190126__000942.xml' #File Name aus Systemreport
country = 'DEU'
error_text = 'Kartenstatus ist nicht GELIEFERT'
#error_text = 'Unbekannter Produktcode'         #nur Produkte, die mit dieser Fehlermeldung anfangen
#error_text = 'Kartennummer unbekannt' 
#error_text = 'Unbekannter Produktcode (EAN)'
#error_text = 'Transaktion hat falschen Kartenwert'
#error_text = 'keine Provision fur Retail Partner definiert'
#####################################################
#####################################################
corrected_ean = '' #this should be empty if the EAN was correct
corrected_value = '' #zB. 50.00; this should be empty if the crd_value was correct
work_dir = r'R:\IT\Betriebe\Korrekturen' #kann operationalional veraendert werden
#########################INPUT#########INPUT##########################################



current_date = time.strftime("%Y%m%d") #today's date YYYYMMDD
work_dir = os.path.join(work_dir, country, current_date + '_' + tx_sold_file[:-3])
# #eg R:\IT\Betriebe\Korrekturen\DEU\20170320_RLBB_tx_sld__20170317__002403
os.mkdir(work_dir)
print('new working folder created: ' + work_dir + '\n') 

retailer = tx_sold_file[:4]
print('retailer in filename (technical retailer): ' + retailer + '\n')

import_path = '/operational/r_output/' + country + '/archiv/' + retailer + '/in/'
print('path to tx_sold_file on server = ' + import_path + '\n')

file_listing = sftp.listdir(import_path)

i = len(file_listing)-1
while tx_sold_file[:-3] not in file_listing[i]:
    print(file_listing[i])
    i = i - 1
else:
    print('file found \n')
    zipped_tx_sold = file_listing[i] #das gezippte file
    print('full file name = ' + zipped_tx_sold + '\n')
    import_path = import_path + zipped_tx_sold
    print('import_path: ' + import_path + '\n')
    print('copy file to R \n')
    sftp.get(import_path, os.path.join(work_dir, zipped_tx_sold))
    print('done copying ' + zipped_tx_sold + '\n')

#sftp.close()

to_be_unzipped = os.path.join(work_dir, zipped_tx_sold)
zfile = zipfile.ZipFile(to_be_unzipped)
zfile.extractall(work_dir)
zfile.close()
print('zip file successfully decompressed \n')


if tx_sold_file[:-3] + 'err' in os.listdir(work_dir):
    print(tx_sold_file[:-3] + 'err' + ' exists and will be processed now \n')


####Retrieve consecutive number of last tx_sld for RREG###########################
cursor = selectCountryConnection(country)
resultset1 = db_lookup(cursor, last_tx_sld_imp)

print(resultset1[0][:])
ppr_id = resultset1[0][0]
print('ppr_id =' + str(ppr_id))
numbering =  str(resultset1[0][7])
print('Name of last tx_sld Import: ' + str(numbering))
fln = resultset1[0][7][-10:-4]
RREG_filename = 'RREG_tx_sld__' + str(current_date) + '__' + str(increase_consecutive_no(fln, 6)) + '.xml'
print('new filename: ' + str(RREG_filename))
####Retrieve number of last tx_sld for RREG########################### 


##### Parse relevant data from err file and write it to new RREG xml ################################
err_data = os.path.join(work_dir, tx_sold_file[:-3] + 'err')

from xml.etree import ElementTree as ET
tree1 = ET.parse(err_data)
record_count_err = tree1.find('header/processed_err').text


tree2 = ET.ElementTree(ET.fromstring(tx_solds))
file_name = tree2.find('header/file_name')
file_name.text = RREG_filename
print('Insert file name ' + str(RREG_filename))
export_date = tree2.find('header/export_date')
export_date.text = time.strftime("%Y-%m-%d")
print('Insert export date = ' + str(export_date.text))
transactions = tree2.find('transactions')

card_numbers = []
record_count = 0
for i in tree1.findall('./error/err_content'):
    if (i.find('err_desc').text).startswith(error_text):
        
        tx = ET.SubElement(transactions, 'tx')
        
        crd_no = ET.SubElement(tx, 'crd_no')
        crd_no.text = i.find('crd_no').text
        card_numbers.append(crd_no.text)
        
        prt = ET.SubElement(tx, 'prt')
        prt.text = i.find('prt').text
        retailer = i.find('prt').text #retailer is given by real (not technical) retailer abbreviation !!!
        
        type_ = ET.SubElement(tx, 'type')
        type_.text = i.find('type').text
        
        date_ =  ET.SubElement(tx, 'date')
        date_.text = i.find('date').text
        
        pos_ = ET.SubElement(tx, 'pos')
        pos_.text = i.find('pos').text
        
        ean_no = ET.SubElement(tx, 'ean_no')
        ean_no.text = i.find('ean_no').text
        if corrected_ean <> '':
            ean_no.text = corrected_ean
            
        crd_value = ET.SubElement(tx, 'crd_value')
        crd_value.text = i.find('crd_value').text
        if corrected_value <> '':
            crd_value.text = corrected_value

        record_count += 1


print('Note that number of error products in err file = ' + str(record_count_err))
print('and that number of error products written into RREG file = ' + str(record_count) + '\n' )
print('following card numbers will be further processed: ')
for i in card_numbers:
    print(i)

record_count_ = tree2.find('header/record_count')
record_count_.text = str(record_count)

#tree2.write(os.path.join(work_dir, RREG_filename), encoding='utf8', method='xml')
tree2.write(os.path.join(work_dir, RREG_filename), method='xml')
print('done writing RREG file \n')
##### Parse relevant data from err file and write it to new RREG xml ################################


###############zip xml file and send it to sftp-server and unzip########################
RREG_path = os.path.join(work_dir, RREG_filename)   
print(os.access(RREG_path, os.F_OK))

with open(os.path.abspath(RREG_path)) as f_in, gzip.open(os.path.abspath(RREG_path + '.gz'),'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)




sftp.cwd('/operational/ftpdings/ftp_homie/' + str(country) + '/RREG/LIVE/in')

sftp.put(RREG_path + '.gz')
print('directory contents: \n')
print(sftp.listdir())

sftp.execute('gzip -d /operational/ftpdings/ftp_homie/' + str(country) + '/RREG/LIVE/in/' + RREG_filename + '.gz')
print(sftp.listdir())
##############zip xml file and send it to sftp-server and unzip########################  


########################## start scripts ############################################
print('starting the pearl script: ./pearl RREG SOLD admin_name admin_name_pwd \n')
sftp.execute('cd /operational/jboss/prod_server/' + str(country) + '/r-scheduler/; ./pearl RREG SOLD admin_name admin_name_pwd')


print('starting the pearl script: ./pearl ' + retailer + ' PROCESS2 admin_name admin_name_pwd \n')
command_string = './pearl ' + retailer + ' PROCESS2 admin_name admin_name_pwd'
sftp.execute('cd /operational/jboss/prod_server/' + str(country) + '/r-scheduler/;' + command_string)
########################## start scripts ############################################



sftp.close()
cursor.close()

print('done')

