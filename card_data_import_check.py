# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 21:07:35 2017

@author: netzer
"""
"""
This card import check script accepts 7 inputs in order to perform a
consistency check between data in the input XML and the data base given by
the input "country". If errors occurr, a WARNING is displayed in the console.
Due to database restrictions regarding the SQL "IN" operator, this script
loops through the whole set of card numbers in the XML as long as the
maximum number of items (max_cards_query) is reached or the "last XML element
reached". Then a query containing these numbers is sent to the database to
determine the card numbers already in the database. Then the loop starts
counting from 0 again. Here is a list of checks:

Check 1: against the ausschlussliste: the run ends immediately if the file
should not be processed (a kind of reminder :-).
Check 2: where the XML itself is inspected, especially the data belonging to
         the first card; warnings are displayed if
         2.1 the card length is not equal to 16 or 19: if so, it is called
         "unusual" but not necessarily wrong - a check against the brand
         settings in the db is done later; if
         2.2 VEN or PEN have wrong length (different to 34, hard coded), if
         2.3 tags are empty;
         2.4 necessary tags are missing (based on input "necessary" tags)
Check 3: 3.1 Based on brand_code and brand_value in the first card (XML), the
         brand commision and configuration details from the db are displayed;
         a WARNING is shown if there is no such entry in the db;
         3.2 Length of first card number is checked against the brand settings.
Check 4: Depending on the input in the 'retailer' variable, the retail
         commission is displayed if available in the db; a WARNING is shown
         otherwise.
Check 5: After the the existence check of cards in the db, the following check
         results are shown in the console:
         5.1 cards already in db
         5.2 doublets in the XML
         5.3 correctness of record count in the XML

Final remark: the limit of 1000 data points when querying an Oracle DB can be
circumvented by using constructs like e.g. tuples in the following way:
select crd_card_no from cards where (1,crd_card_no) in  (
(1,'0276307000011800'),
(1,'0276307000011800'),
(1,'0276307000011800'), ...)
or clauses like OR. Here we make use of the former method. But this is still
restricted with the current Oracle ... DB. The current limit here is around
65000, certainly less than 70000. In the below imput section the variable 
'max_cards_query' contains this value and can be adopted if necessary. If you
get an Orcale error containing something like "maximum number of expressions
..." you might want to reduce 'max_cards_query'.
"""

import  sys, timeit, time, os
from selects import moreThankCards, retail_comm2, partner_provision
from mytoolbox import selectCountryConnection, db_lookup


############ I N P U T #######################################################
xml_file_name = r'MANN_crd_imp__20190529__000234.xml'
retailer = 'RPCC'#should be empty if it is only 2of5 ("Einspielung ohne Auslieferung")!
country = 'CHE'
show_queries = 'no' # yes/no if you want to see the db-queries in the output console
#DO NOT CHANGE THIS VARIABLE EXCEPT FOR GOOD REASONS
max_cards_query = 60000 #maximum number of cards which may be contained in a SELECT to query the db;
# currently max approximately 65k! Here we set a value of 60000
#DO NOT CHANGE THIS VARIABLE EXCEPT FOR GOOD REASON 
ausschlussliste = [('CHE','SOCA')]#country-brandcode pairs which are not to be processed;
#you can add further pairs or leave the list empty: []
necessary = ['crd_no', 'ven', 'pen', 'prt', 'brand']
############ I N P U T #######################################################

start_time = timeit.default_timer() #start time of overall computation

##################Ausschluss Check########################################
brand_name = xml_file_name[:4]

if (country,xml_file_name[:4]) in ausschlussliste:
    sys.exit('This card import for ' + brand_name + ' is NOT supposed to be ingested' + '\n' 
    'Please ask your WIKI/Outlook for more information!')
##################Ausschluss Check########################################



################## Manage File Paths and Clear Former Check Results ###############################
base_path = os.path.join(r'Z:\ITdep\Betriebe\cardno_prod',
                         country, 'Live ' + time.strftime("%Y%m%d")[:4], 'In_Arbeit')

xml_file_name_path = os.path.join(base_path, xml_file_name)
check_result_file_path = os.path.join(base_path, 'check_result_'+ xml_file_name.replace('.xml','.txt'))

print('to be checked: ' + xml_file_name_path + '\n')
print('for check results see: ' + check_result_file_path + '\n')
open(check_result_file_path, 'w').close() #clear check results before writing again!
################## Manage File Paths and Clear Former Check Results ###############################



###### Parse XML and create & execute a Query possibly containing more than 1000 card numbers ##########################
from lxml import etree as ET

tree = ET.parse(xml_file_name_path)
try:
    record_count = tree.find('header/record_count')
    print('info from XML header and the first card: ')
    print(60*'-')
    print('number of cards given by <record_count>: ' + str(record_count.text))
    brand_code = tree.find('./cards/card/brand').text
    print('product: ' + brand_code)
except AttributeError:
    sys.exit('Please open XML and substitute "xmlns=" by "xmlns:xsi=". Then restart this program.')

############## Display and check data of first card #####################################
print('\n')
print('checking XML data of first card: ')
print(60*'-')

first = tree.find('./cards/card')

cardno_length = 0
for t in first:
    if  t.tag == 'crd_no':
           cardno_length = len(t.text)
    try:
              
        print(str(t.tag) + '\t' + 'Length = ' + str(len(t.text)) + '\t' + t.text)
                
        if t.tag in necessary:
            necessary.remove(t.tag)
            

        elif t.tag == 'crd_no' and len(t.text) not in (16, 19):
            print('WARNING: Length of ' + t.tag + ' is unusual!')
        elif (t.tag == 'ven' or t.tag == 'pen') and len(t.text) <> 34:
            print('WARNING: Length of ' + t.tag + ' is wrong!')
#        elif t.tag == 'brand' and t.text <> brand_code:
#            print('WARNING: product in header is different to product in first card metadata!', (t.text, brand_code))
        elif t.tag == 'crd_value':
            cardval = t.text #save crd_value as string for later comparison
        

        
    except TypeError:
        print('WARNING: There might be empty tags: ' + t.tag)

print('')
if necessary <> []:
    print('WARNING: missing tags in XML:')
    for n in necessary:
        print(n)
    print('\n')
############## Display and check data of first card #####################################

################### Partner Provision Check #############################################
cursor = selectCountryConnection(country)
query = (partner_provision.replace('br-kode', brand_code)).replace('kartenwert', cardval)
if show_queries == 'yes':
    print(query)

print('Querying the database: ')
print(30*'-')

eGs = db_lookup(cursor, query)

cardno_len = []
dictlist = []
print('checking partner (brand) commission and configuration:')
print(60*'-')
if eGs <> []:
    # get column names from cursor description
    col_names = [x[0] for x in cursor.description]
    for entry in range(len(eGs)):
        d = dict(zip(col_names, [val for val in eGs[entry]] ))
        for col_n in d.keys():
            print(col_n + '\t\t' + str(d[col_n]).strip())
        dictlist.append(d)
        print(30*'-')
    
    
    for dic in dictlist:
        if int(dic['CDV_CARDNO_LEN']) == cardno_length:
            cardno_len.append(dic)
            
    
#    cardno_len = [dictlist[l] for l in dictlist if int(dictlist[l]['CDV_CARDNO_LEN']) == int(cardno_length)]
#    print(cardno_len)
    if cardno_len == []:
        print(('WARNING: Length of first card number in XML is not correct!'))
    else:
        print('Length of first card number in XML is correct: ' + str(cardno_len[0]['CDV_CARDNO_LEN']))
    

else:
    print('WARNING: partner commission not available! Discrepancy between brand_code and brand_value? \n')
print(60*'-' + '\n')

################### Partner Provision Check #############################################


################## Retail Commission Check #############################################
if retailer <> '': 
    print('Querying the database for retail commission: ')
    print(30*'-')
    query = retail_comm2.replace('br-kode', brand_code).replace('retailer', retailer).replace('kartenwert',cardval)
    eGs = db_lookup(cursor, query)
    if show_queries == 'yes':
        print(query)
    
    if eGs <> []:
        # get column names from cursor description
        col_names = [x[0] for x in cursor.description]
        for entry in range(len(eGs)):
            d = dict(zip(col_names, [val for val in eGs[entry]] ))
            for col_n in d.keys():
                print(col_n + '\t\t' + str(d[col_n]).strip())
            dictlist.append(d)
            
            print('')
            print('retail commission available!' + '\n')
    
    
    else:
        print('WARNING: retail commission not available! \n')
    print(60*'-' + '\n')
################## Retail Commission Check #############################################
root1 = tree.getroot()
h = ("(1,'"+cardno+"')," for cardno in (i.find('crd_no').text for i in root1.findall('./cards/card') ))
card_count = 0 #counts card numbers in XML, incl. doublets, starting from 0 for each loop to max_cards_query
max_count = 0 #only counting to max_cards_query
cards = [] #card numbers without doublets (different card numbers)
double = [] #card numbers occurring at least twice
template = moreThankCards #
found_counter = 0 #counter for card numbers found in DB
xml_cards_total = 0 # overall counter for card numbers found in XML, including doublets
#
with open(check_result_file_path, 'a') as f: # 'a' means append-mode (append data)
#    
    while h:
        try:
            card = next(h)
#            print(card)
            card_count = card_count + 1
            max_count = max_count + 1
#            print('card_count: ' + str(card_count))
#            print('max_count: ' + str(max_count))
            if card in cards:
                double.append(card)
            else:
                cards.append(card)
            if max_count == max_cards_query:
                template = template.replace('()', "("+''.join(cards)[:-1]+")")
                cards[:] = []
                cursor.execute(template)
                template = moreThankCards
                for found in cursor: #eg ('0465500861082494',)
                    found_counter = found_counter + 1
#                    print('printed: ' + found[0])
                    f.write(found[0] + '\n')
                max_count = 0
                

        except StopIteration:
            print('looping through XML for querying the data base: last XML element reached: ' + str(card_count))
            template = template.replace('()', "("+''.join(cards)[:-1]+")")
            cards[:] = []
            cursor.execute(template)
            template = moreThankCards
            for found in cursor: #eg ('0465500861082494',)
                found_counter = found_counter + 1
#                print('printed: ' + found[0])
                f.write(found[0] + '\n')
            break

print('')
print('DB Check Cards Results:')
print(60*'-')

if found_counter > 0:
    print('WARNING: cards already in DB: ' + str(found_counter))
    print('Please take a look at: ' + str(check_result_file_path) + '\n')
else:
    print('no cards found in DB' + '\n')

dou = len(double)
if dou > 0:
    print('WARNING: Cards occurring more than once in XML: ' + str(dou))
for d in double:
    print(d[3:-2]) #show doublets
print('')

if int(record_count.text) <> card_count:
    print('WARNING: record Count in XML is NOT Correct!')
    print('\t'+ 'record_count = ' + str(record_count.text))
    print('\t' + 'number of card numbers found in XML = ' + str(card_count) + '\n' )

            
print('overall duration: ' + str(timeit.default_timer() - start_time))