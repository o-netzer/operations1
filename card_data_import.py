# -*- coding: utf-8 -*-
"""
Created on Thu May 17 16:39:52 2018

@author: netzer

Assuming that the source xml is stored in a certain position of a Windows file system
this interactive script performs various steps according to the input of the user:

1) check file name correctness syntactically
2) check file name semantically and file path correctness
3) retrieve new consecutive import number from database and integrate it into file name
4) overwrite tags in header of source xml with correct data
5) if ready for import play audio signal and ask user if he wants to start the import
6) zip xml file and send it to sftp-server and unzip
7) start script on the ftp to import data into database
8) check result of the import in db and perform audio signal; if successful, ask the
   user if he wants to continue; terminate otherwise
9) ask the db for the next number for logistics (log.) import and create new log. import XML
   with correct file naming
10) ask the db for log. items to be imported (taken from the previous import) and
    write them into the log. import XML
11) audio signal if log. import is ready and ask user to continue
12) zip xml file and send it to sftp-server and unzip
13) start script on the ftp to import log. data into database
14) ask the db if log. import was successful; if successful, audio signal; terminate otherwise
15) ask the user if an export of data should be performed
16) start export script on ftp
17) retrieve results from the db and display them with audio signal 
"""

#additional imports are given in below sections
from selects import last_crd_imp_of_brandp, last_pcl_import, last_card_export, pcl_fetch, spec_crd_imp
from mytoolbox import increase_consecutive_no, db_lookup, selectCountryConnection
import winsound, os, time, shutil, sys, re, timeit
from XMLs import rrem_xml
#additional imports are given in below sections


#################INPUT###############################################################
sourcexml = r'MAND_crd_imp__20190529__000234.xml' # file name of source
retailer = 'RPSS' #retailer name abbreviation if delivery is required, empty string otherwise (2of5)
country = 'CHE' #retailer country abbreviation (DEU,CHE,AUT)
#################INPUT###############################################################

start_time = timeit.default_timer() #start time of computation

#############analyzing filename######################################################

m = re.match('[A-Z]{4}_crd_imp[_]+[\d]{8}__[\d]{6}.xml', sourcexml)
if m == None:
    sys.exit("Something's wrong with the filename. It's unusual or problematic.")
else:
    print('Filename ' + str(m.string[m.start():m.end()]) + ' is correct.')
    
#############analyzing filename######################################################


############check path and file naming#################################
production_path = r"Z:\ITdep\Betreiber\Kartennummern"
brandp = sourcexml[:4]
current_date = time.strftime("%Y%m%d") #retrieve current date
current_year = current_date[:4] #retrieve current year
external_cons_no = sourcexml[-10:-4] #retrieve import number provided by external source


sourcexml_path = os.path.join(production_path, country, 'Produktion '+ current_year, 'tbd', sourcexml)
print("sourcexml_path: " + sourcexml_path)

if os.access(sourcexml_path, os.F_OK):
    print(sourcexml_path)
    print('Path and file naming of the source xml are OK.')
else:
    print('\n')
    print('Path to source xml not found. Please arrange things as usual. Check filenaming!')
    print('\n')
    sys.exit('Come back and try once more.')
############check path and file naming#################################

##################create new filename and rename sourcexml###################################
old_sourcexml_path = sourcexml_path
cursor = selectCountryConnection(country)
print(cursor)
adopted_select = last_crd_imp_of_brandp.replace('brandp',brandp)
print(adopted_select)


resultset1 = db_lookup(cursor, adopted_select)
print(resultset1)

try:
    internal_cons_no = resultset1[0][7][-10:-4]
    print(internal_cons_no)
except IndexError:
        internal_cons_no = '000000'
        print(internal_cons_no)
    
new_internal_no = str(increase_consecutive_no(internal_cons_no , limit=6))
print('new internal number: ' + new_internal_no)

try:
    print('status of last import: ' + resultset1[0][5])
    if resultset1[0][5] in ('SUCCESS', 'ERROR', 'NOT_FOUND'):
        sourcexml = sourcexml[:4] + '_crd_imp__' + str(current_date) + '__' + new_internal_no + '.xml'
        print(sourcexml)
    else:
        print(internal_cons_no)
        sourcexml = sourcexml[:4] + '_crd_imp__' + str(current_date) + '__' + internal_cons_no + '.xml'
        print(sourcexml)
except IndexError:
    sourcexml = sourcexml[:4] + '_crd_imp__' + str(current_date) + '__' + new_internal_no + '.xml'

new_sourcexml_path = os.path.join(production_path, country, 'Produktion '+ current_year, 'tbd', sourcexml)
##################create new filename and rename sourcexml###################################


###############check XML contents and update tags inside; rename sourcexml############################
from xml.etree import ElementTree as ET
tree = ET.parse(sourcexml_path)
try:
    file_name = tree.find('header/file_name')
    export_date = tree.find('header/export_date')
    print(file_name.text)
    print(export_date.text)
    file_name.text = sourcexml
    export_date.text = time.strftime("%Y-%m-%d")
except AttributeError:
    sys.exit('Please open XML and substitute "xmlns=" by "xmlns:xsi=". Then restart this program.')


tree.write(sourcexml_path)

os.rename(old_sourcexml_path, new_sourcexml_path)
print(new_sourcexml_path + '\n')
print('ready for import' + '\n')

##################################AUDIO SIGNAL###############################################
winsound.PlaySound('C:\Users\Public\Music\Sample Music\Music_Censor.wav', winsound.SND_FILENAME)
##################################AUDIO SIGNAL###############################################

start_import = raw_input('Do you want to start the Card Data Import? yes/no: ')
if start_import == 'yes':
    print('Card Data Import started ...')
else:
    sys.exit('Program terminated by user before Card Data Import.')
#    logging.info('Card Data Export started ...')

##############zip xml file and send it to sftp-server and unzip######################## 
import gzip

print(os.access(new_sourcexml_path, os.F_OK))

with open(os.path.abspath(new_sourcexml_path)) as f_in, gzip.open(os.path.abspath(new_sourcexml_path + '.gz'),'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)

new_sourcexml_path = new_sourcexml_path + '.gz'
print(new_sourcexml_path)
zipped_sourcexml = os.path.basename(os.path.normpath(new_sourcexml_path))
print(zipped_sourcexml)


from sftp import sftp


import_path = '/oop/ftpshoot/ftp_homecoming/' + country + '/' + brandp + '/LIVE/in/'
print(import_path)

sftp.cwd(import_path)

sftp.put(new_sourcexml_path)
print(sftp.listdir())

command_str = 'gzip -d ' + os.path.join(import_path,zipped_sourcexml)
print(command_str)

sftp.execute(command_str)
print(sftp.listdir())
 ###############zip xml file and send it to sftp-server and unzip########################   



################perform Card Data Import if desired###################################### 
command_string = 'cd /oop/poss/live_server/' + country + '/scheduler/; ./start_perlscript ' + brandp + ' CARDDATAIMPORT user pwd'
print(command_string)
sftp.execute(command_string)


#    logging.info('Program terminated by user before Card Data Export.')

adopted_select = spec_crd_imp.replace('import_file_name', sourcexml )
print(adopted_select)

print('Result: ')

resultset2 = db_lookup(cursor, adopted_select)


if resultset2[0][5] == 'SUCCESS':
    print('The products have been inserted into the DB successfully. No Errors!')
    print(str(resultset2[0][8]) + ' cards!')
else:
    print('NOT SUCCESSFUL. Please check manually and restart this procedure!')
    sys.exit('Good bye!')
################perform Card Data Import if desired###################################### 


go_on = ''
if retailer == '':
    print("""This procedure was started as 2of5. Since card data is imported successfully, this
    program ends now, except:
    """ )
    go_on = raw_input('Do you want to continue with picklisting? yes/no ')
    if go_on == 'no':
        sys.exit('Good bye!')
    if go_on == 'yes':
        retailer = raw_input('Please insert the 4-letter retailer name: ')
        if len(retailer) <> 4:
            sys.exit("Program is terminated because you did not enter a valid retailer name.")

#cursor = selectCountryConnection(country)
resultset3 = db_lookup(cursor, adopted_select)
ppr_id = resultset3[0][0]
print('ppr_id =' + str(ppr_id))     

###################################################################################       
#cursor = selectCountryConnection(country)

resultset5 = db_lookup(cursor, last_pcl_import)
numbering =  str(resultset5[0][7])
print('Name of last PCL-Import: ' + str(numbering))
fln = resultset5[0][7][-10:-4]


rrem_filename = 'RREM_pcl_imp__' + str(current_date) + '__' + str(increase_consecutive_no(fln, 6)) + '.xml'
print('new filename: ' + str(rrem_filename))

###################write RREM XML##########################################################################
#cursor = selectCountryConnection(country)
adopted_select = last_crd_imp_of_brandp.replace('brandp',brandp)
resultset3 = db_lookup(cursor, adopted_select)
print(adopted_select)
ppr_id = resultset3[0][0]
print('ppr_id of last card import for ' + str(brandp) + '= ' + str(ppr_id))

pcl_fetch = pcl_fetch.replace('ppr_id',str(ppr_id))
pcl_fetch = pcl_fetch.replace('retailer',str(retailer))

resultset4 = db_lookup(cursor, pcl_fetch)
#cursor.close()

num_lines = len(resultset4)

print('printing top 5 and last 5 lines:')
print(resultset4[:5])
for i in range(3):
    print('...')
print(resultset4[-5:])
print('')
#############################################################################



tree = ET.ElementTree(ET.fromstring(rrem_xml))


file_name = tree.find('header/file_name')
file_name.text = rrem_filename
print('Insert file name' + str(rrem_filename))
export_date = tree.find('header/export_date')
export_date.text = time.strftime("%Y-%m-%d")
print('Insert export date = ' + str(export_date.text))
p_units = tree.find('packing_units')

#<packing_unit><ven>0115051644048349216039536051970000</ven><ean_no>50516440000</ean_no><prt>999760</prt><pos>Zentrale</pos></packing_unit>

counter = 0
for i in range(num_lines):
    packing_unit = ET.SubElement(p_units, 'packing_unit')
    unit = resultset4[i][0]
    #print(unit)

    ven = ET.SubElement(packing_unit, 'ven')
    m = re.search("<ven>(.*?)</ven>",unit)
    ven.text = m.group(1)
    
    ean = ET.SubElement(packing_unit, 'ean_no')
    m = re.search("<ean_no>(.*?)</ean_no>",unit)
    ean.text = m.group(1)
    
    prt = ET.SubElement(packing_unit, 'prt')
    prt.text = retailer
    
    pos = ET.SubElement(packing_unit, 'pos')
    n = re.search("<pos>(.*?)</pos>",unit)
    pos.text = n.group(1)

    counter = counter + 1

##########alternatively##########################################    
#p_units.append(packing_unit)    

#for unit in resultset4:
#    packing_unit = ET.SubElement(p_units, 'packing_unit')
#    unit = unit[0]
#    print(unit)
#
#    ven = ET.SubElement(packing_unit, 'ven')
#    m = re.search("<ven>(.*?)</ven>",unit)
#    ven.text = m.group(1)
#    
#    ean = ET.SubElement(packing_unit, 'ean_no')
#    m = re.search("<ean_no>(.*?)</ean_no>",unit)
#    ean.text = m.group(1)
#    
#    prt = ET.SubElement(packing_unit, 'prt')
#    prt.text = retailer
#    
#    pos = ET.SubElement(packing_unit, 'pos')
#    n = re.search("<pos>(.*?)</pos>",unit)
#    pos.text = n.group(1)
#
#    counter = counter + 1
#    
#    p_units.append(packing_unit)    
##########alternatively##########################################  

print('Number of lines given by DB: ' + str(num_lines))
print('Number of vens written into XML: ' + str(counter))

record_count = tree.find('header/record_count')
record_count.text = str(num_lines)
rrem_path = os.path.join(production_path, country, 'Produktion '+ current_year, 'tbd', str(file_name.text)) #recent update!!!!
tree.write(rrem_path)
if num_lines <> counter:
    sys.exit('Number of lines given by DB does not equal number of vens written into XML.')
###################write RREM XML##########################################################################

print('PCL-import file is written.' + '\n')

##################################AUDIO SIGNAL###############################################
winsound.PlaySound('C:\Users\Public\Music\Sample Music\Music_Censor.wav', winsound.SND_FILENAME)
##################################AUDIO SIGNAL###############################################


 ###############start pcl-import and/or card data export################################# 
start_pcl = raw_input('Do you want to start the PCL-Import? yes/no: ')
if start_pcl == 'yes':
    print('PCL-Import started ...')
#    logging.info('PCL-Import started ...')
else:
    sys.exit('Program terminated by user before PCL-Import.')
#    logging.info('Program terminated by user before PCL-Import.')
    

 ###############zip xml file and send it to sftp-server and unzip########################   

print('path to xml is ok: ' + str(os.access(rrem_path, os.F_OK)) + '\n')

print('zipping xml' + '\n')
with open(os.path.abspath(rrem_path)) as f_in, gzip.open(os.path.abspath(rrem_path + '.gz'),'wb') as f_out:
    shutil.copyfileobj(f_in, f_out)

sftp.cwd('/oop/ftpshoot/ftp_homecoming/' + str(country) + '/RREM/LIVE/in')

sftp.put(rrem_path + '.gz')
print(sftp.listdir())

sftp.execute('gzip -d /oop/ftpshoot/ftp_homecoming/' + str(country) + '/RREM/LIVE/in/' + rrem_filename + '.gz')
print(sftp.listdir())
 ###############zip xml file and send it to sftp-server and unzip########################   

sftp.execute('cd /oop/poss/live_server/' + str(country) + '/scheduler/; ./start_perlscript RREM PICKLISTIMPORT user pwd')
print('./start_perlscript RREM PICKLISTIMPORT user pwd')

#cursor = selectCountryConnection(country)
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

##################Ausnahme bei RCON und RPSC###########################################
if retailer in ('RPSS','RCAM'):
    sys.exit('Unfortunately (due to formatting reasons) data to  ' + retailer + ' should not be exported by this Python program. Please proceed the last step (export) manually!')
##################Ausnahme bei RCON und RPSC###########################################


start_export = raw_input('Do you want to start the Card Data Export? yes/no: ')
if start_export == 'yes':
    print('Card Data Export started ...')
#    logging.info('Card Data Export started ...')
    command_string = './start_perlscript ' + retailer + ' CARDDATAEXPORT user pwd'
    print(command_string)
    sftp.execute('cd /oop/poss/live_server/' + str(country) + '/scheduler/;' + command_string)

else:
    sys.exit('Program terminated by user before Card Data Export.')
#    logging.info('Program terminated by user before Card Data Export.')

last_card_export = last_card_export.replace('RetailP', retailer)
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


print('duration: ' + str((timeit.default_timer() - start_time)/60.0) + ' min')


##################################AUDIO SIGNAL###############################################
winsound.PlaySound('C:\Users\Public\Music\Sample Music\Music_Censor.wav', winsound.SND_FILENAME)
##################################AUDIO SIGNAL###############################################