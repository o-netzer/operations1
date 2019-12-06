# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 16:42:29 2019

@author: netzer

Sometimes IT-operations work is hard, especially if the amount of information
provided to solve a problem is minimal.

This script takes a card number (and optionally country) as only input information.
It then searches for all the information available in each of the relevant databases
and displays the information in the console window.
It was designed as the basis for the project called "The Matrix" - the endeavour to
analyze all available information in the entire system given 1 card number - and
present it nicely.

The script is highly repetitive, thus not in accordance with Python's DRY principle
This is partly desired to be so because it enables the user to control the information
displayed in the Spyder console window by simply commenting out unwanted lines of code.
"""



from mytoolbox import selectCountryConnection, select_online_CountryConnection, \
ekonto_connect, db_lookup, Maggenta_anmeldung
from selects import cards2, eServ_protoc, eGs_transactions, eGs_transaktfehler, \
eKo_single_crd, eKobewegung, eGs_det, prod_det, Maggenta_cardact, ekontocheckout_ekontopayment
import sys

################# I N P U T ##############################################
card_no = '009024000180938000' #Kartenlaenge egal
countries = ['DEU'] #e.g. ['DEU','AUT'] kann mehrere Elemente beinhalten
################# I N P U T ##############################################

print(3*'\n')

laenge = len(card_no)
print('card length = ' + str(laenge))

print(3*'\n')

print((30*'#') + ' eCoupon cards Tabelle ' + (30*'#'))
#####################eCoupon cards########################################
query = cards2.replace("k_num", card_no)
ean_liste = []

for c in countries:
    cursor = selectCountryConnection(c)  #<type 'OracleCursor'>
    eGs = db_lookup(cursor, query)
    print('eCoupon ' + c)
    if eGs <> []:
        # get column names from cursor description
        col_names = [x[0] for x in cursor.description]
        for entry in range(len(eGs)):
            d = dict(zip(col_names, [val for val in eGs[entry]] ))
    
            print('card number found:   ' + str(d['KRT_CARD_NO']))
            print('EAN                  ' + str(d['KRT_EAN']))
            ean_liste.append(d['KRT_EAN'])
            print('Status               ' + str(d['STATUS']))
            print('')
        if len(eGs) > 1:
            print('WARNING: There is more than 1 (card_no,EAN) pair in the DB !!!!')
            print(ean_liste)
            print('This means that the following results must be read very CAREFULLY!!!')
            print('')
        
        print((30*'#') + ' eCoupon cards Details ' + (30*'#'))
        ###################### eGs_Details #############################

        for e in ean_liste:
            query = (eGs_det.replace('euro_pro', e)).replace('k_num', card_no)
            eGs = db_lookup(cursor, query)
            col_names = [x[0] for x in cursor.description]
            d = dict(zip(col_names, [val for val in eGs[0]] ))
            
            print('KART_ID:       			' + str(d['CARD_ID']))
            print('LAOD_ID:       			' + str(d['LAOD_ID']))
            print('CARDNUMBER:      		' + str(d['CARDNUMBER']))
            print('PIN:				' + str(d['PIN']))
            print('STATUS:       			' + str(d['STATUS']))
            print('DII_UPD_TIME:    		' + str(d['DII_UPD_TIME']))
            print('CARD_UPDATE_TIME:		' + str(d['CARD_UPDATE_TIME']))
            print('DII_DELIVERY_NO: 		' + str(d['DII_DELIVERY_NO']))
            print('DLJ_INS_DATE:    		' + str(d['DLJ_INS_DATE']))
            print('DLJ_CANCELLED:   		' + str(d['DLJ_CANCELLED']))
            print('DII_UPD_DATE:    		' + str(d['DII_UPD_DATE']))
            print('VEN:				' + str(d['VEN']))
            print('PACKETNUMMER:    		' + str(d['PACKETNUMMER']))
            print('EAN:				' + str(d['EAN']))
            print('PARTNERCODE:     		' + str(d['PARTNERCODE']))
            print('VALUE:        			' + str(d['VALUE']))
            print('PRODUKTCODE:     		' + str(d['PRODUKTCODE']))
            print('PRODUKTNAME:     		' + str(d['PRODUKTNAME']))
            print('DELIVERY_PARTNER:		' + str(d['DELIVERY_PARTNER']))
            print('DELIVER_POS:     		' + str(d['DELIVER_POS']))
            print('SELLER_POS:      		' + str(d['SELLER_POS']))
            print('MAX_VALUE:       		' + str(d['MAX_VALUE']))
            print('KARTE_WOCHE:     		' + str(d['KARTE_WOCHE']))
            print('KARTE_JAHR:      		' + str(d['KARTE_JAHR']))
            print('CARD_INSERT_TIME:		' + str(d['CARD_INSERT_TIME']))
#            print('DELIVERY_LIST_ITEM_ID:          ' + str(d['DELIVERY_LIST_ITEM_ID']))
            print('DLJ_INS_DATE:       		' + str(d['DLJ_INS_DATE']))
#            print('DLJ_DII_ID:       		' + str(d['DLJ_DII_ID']))
            print('DELIVERY_LIST_ID:       	' + str(d['DELIVERY_LIST_ID']))
            print('DII_UPD_DATE:       		' + str(d['DII_UPD_DATE']))
            
            query = prod_det.replace('euro_pro', e)
            eGp = db_lookup(cursor, query)
            col_names = [x[0] for x in cursor.description]
            d = dict(zip(col_names, [val for val in eGp[0]] ))
            print('PARTNERLANGNAME:                     ' + str(d['PARTNERLANGNAME']))
            print('Routing Type:                        ' + str(d['Routing Type']))
            print('Unbekannte Kartennummer erlauben:    ' + str(d['UNKNOWN_ERL']))
            
            print(3*'\n')
               
###################### eGs_Details #############################
        print((30*'#') + ' eCoupon cards Details ' + (30*'#'))              
    else:
        print('card number not found \n')
#cursor.close()
#####################eCoupon cards########################################
print((30*'#') + ' eCoupon cards Tabelle ' + (30*'#'))

print(3*'\n')

print((30*'+') + ' eCoupon transactions Tabelle ' + (30*'+'))
#####################eCoupon transactions########################################

for c in countries:
    query = (eGs_transactions.replace('country', c+'001')).replace('k_num', card_no)
#    cursor = selectCountryConnection(c)
    eGs = db_lookup(cursor, query)
    print('eCoupon transactions ' + c + " (Verkaufte Karten)")
    if eGs <> []:
        # get column names from cursor description
        col_names = [x[0] for x in cursor.description]
        for entry in range(len(eGs)):
            d = dict(zip(col_names, [val for val in eGs[entry]] ))

            print('card number found: ' + str(d['TRNAS_KRT']))
            print('TRNAS_DATE         ' + str(d['TRNAS_DATE']))
            print('TRNAS_POS          ' + str(d['TRNAS_POS']))
            print('TRNAS_RP           ' + str(d['TRNAS_RP']))
            print('TRNAS_BP           ' + str(d['TRNAS_BP']))
            print('TRNAS_BRAND_CODE   ' + str(d['TRNAS_BRAND_CODE']))
            print('TRNAS_BRAND_NAME   ' + str(d['TRNAS_BRAND_NAME']))
            print('TRNAS_EAN          ' + str(d['TRNAS_EAN']))
            print('TRNAS_KRT          ' + str(d['TRNAS_KRT']))
            print('TRNAS_POS_DATE     ' + str(d['TRNAS_POS_DATE']))
            print('TRNAS_VALUE        ' + str(d['TRNAS_VALUE']))
            print('TRNAS_ACT_DATE     ' + str(d['TRNAS_ACT_DATE']))
            print('')
    else:
        print('card number not found \n')



#####################eCoupon transactions########################################
print((30*'+') + ' eCoupon transactions Tabelle ' + (30*'+'))

print(3*'\n')

print((30*':') + ' eCoupon transaction errors ' + (30*':'))
#####################eCoupon transaction errors##################################
for c in countries:
    query = eGs_transaktfehler.replace('k_num', card_no)
#    cursor = selectCountryConnection(c)
    eGs = db_lookup(cursor, query)
    print('eCoupon Transaktionsfehler der Karte ' + c)
    if eGs <> []:
        # get column names from cursor description
        col_names = [x[0] for x in cursor.description]
        for entry in range(len(eGs)):
            d = dict(zip(col_names, [val for val in eGs[entry]] ))

            print('card number found: ' + str(d['TRNAS_KRT']))
            print('TRNAS_DATE         ' + str(d['TRNAS_DATE']))
            print('TRNAS_RP           ' + str(d['TRNAS_RP']))
            print('TRNAS_POS          ' + str(d['TRNAS_POS']))
#            print('TRNAS_BP           ' + str(d['TRNAS_BP']))
            print('TRNAS_BRAND_CODE   ' + str(d['TRNAS_BRAND_CODE']))
            print('TRNAS_BRAND_NAME   ' + str(d['TRNAS_BRAND_NAME']))
            print('TRNAS_EAN          ' + str(d['TRNAS_EAN']))
            print('TRNAS_KRT          ' + str(d['TRNAS_KRT']))
            print('TRNAS_POS_DATE     ' + str(d['TRNAS_POS_DATE']))
            print('TRNAS_VALUE        ' + str(d['TRNAS_VALUE']))
            print('TRNAS_ERROR_CODE   ' + str(d['TRNAS_ERROR_CODE']))
            print('TRNAS_ERROR        ' + str(d['TRNAS_ERROR']))
            print('Unbekannte KN erl  ' + str(d['UNB_KN_ERL']))      
            print('')
    else:
        print('card number not found \n')


cursor.close()
#####################eCoupon transaction errors##################################
print((30*':') + ' eCoupon transaction errors ' + (30*':'))

print(3*'\n')

print((30*'~') + ' eDienst cards table ' + (30*'~'))
#####################eDienst########################################
query = cards2.replace("k_num", card_no)
#print(query)
#sys.exit()
for c in countries:
    cursor = select_online_CountryConnection(c)
    eServ = db_lookup(cursor, query)
    print('eDienst ' + c)
    if eServ <> []:
        # get column names from cursor description
        col_names = [x[0] for x in cursor.description]
        for entry in range(len(eServ)):
            d = dict(zip(col_names, [val for val in eServ[entry]] ))

            print('card number found: ' + str(d['KRT_CARD_NO']))
            print('EAN                ' + str(d['KRT_EAN']))
            print('Status             ' + str(d['STATUS']))
            print('')
            if len(eServ) > 1:
                print('WARNING: There is more than 1 (card_no,EAN) pair in the DB !!!!')
                print('This means that the following results must be read very CAREFULLY!!!')
                print('')
    else:
        print('card number not found \n')
#cursor.close()
#####################eDienst########################################
print((30*'~') + ' eDienst cards table ' + (30*'~'))

print(3*'\n')

print((30*'-') + ' eDienst Verkaufsversuche ' + (30*'-'))
#####################eDienst Protocols##############################
query = eServ_protoc.replace('%%',"%" + card_no + "%")
#print(query)

for c in countries:
    #cursor = select_online_CountryConnection(c)
    eServ_pro = db_lookup(cursor, query)
    print('eDienst protocols ' + c)
    if eServ_pro <> []:
        # get column names from cursor description
        col_names = [x[0] for x in cursor.description]
        for entry in range(len(eServ_pro)):
            d = dict(zip(col_names, [val for val in eServ_pro[entry]] ))
#            print(d)
            print('XXX_ID:              ' + str(d['XXX_ID']))
            print('XXX_DATE:            ' + str(d['XXX_DATE']))
            print('YYY_VALUE:           ' + str(d['YYY_VALUE']))
            print('XXX_DESCRIPTION:     ' + str(d['XXX_DESCRIPTION']))
            print('')
    else:
        print('card number not found \n')

cursor.close()
#####################eDienst Protocols##############################
print((30*'-') + ' eDienst Verkaufsversuche ' + (30*'-'))

print(3*'\n')

print((30*'=') + ' eKorso Karten ' + 30*'=')
##################### eKorso Einzelkartenabfrage ##############################
query = eKo_single_crd.replace('k_num', card_no)

for c in countries:
    try:
        cursor = ekonto_connect(c)
        eKo = db_lookup(cursor, query)
        print('eKorso Einzelkartenabfrage ' + c)
        if eKo <> []:
            # get column names from cursor description
            col_names = [x[0] for x in cursor.description]
            for entry in range(len(eKo)):
                d = dict(zip(col_names, [val for val in eKo[entry]] ))
        
                print('MONDINT_CODE:         ' + str(d['MONDINT_CODE']))
                print('MONDINT_NAME:         ' + str(d['MONDINT_NAME']))
                print('PRODUCT_CODE:         ' + str(d['PRODUCT_CODE']))
                print('PRODUCT_NAME:         ' + str(d['PRODUCT_NAME']))
                print('PRODUCT_VALUE:        ' + str(d['PRODUCT_VALUE']))
                print('PROCUCT_VALUE_MAX:    ' + str(d['PROCUCT_VALUE_MAX']))
                print('EAN:                  ' + str(d['EAN']))
                print('CARDNUMBER:           ' + str(d['CARDNUMBER']))
                print('STATUS:               ' + str(d['STATUS']))
                print('PIN:                  ' + str(d['PIN']))
                print('KRT_PIN_FAILURE_COUNT:' + str(d['KRT_PIN_FAILURE_COUNT']))
                print('KRT_PIN_FAILURE_DATE: ' + str(d['KRT_PIN_FAILURE_DATE']))
                print('KRT_INS_DATE:         ' + str(d['KRT_INS_DATE']))
                print('KRT_UPD_DATE:         ' + str(d['KRT_UPD_DATE']))
                print('')
                if len(eKo) > 1:                    
                    print('WARNING: There is more than 1 (card_no,EAN) pair in the DB !!!!')
                    print('This means that the following results must be read very CAREFULLY!!!')
                    print('')
        else:
            print('card number not found \n')
    except AttributeError:
        print('There is no eKorso DB for country ' + c)
#cursor.close()
##################### eKorso Einzelkartenabfrage ##############################
print((30*'=') + ' eKorso Karten ' + 30*'=')

print(3*'\n')

print((30*'<') + ' eKorso Bewegungen ' + 30*'<')
##################### eKorso Kontenbewegungen ##############################
query = eKobewegung.replace('k_num', card_no)

for c in countries:
    try:
        cursor = ekonto_connect(c)
        eKobew = db_lookup(cursor, query)
        print('eKorso Kontobewegungen ' + c)
        if eKobew <> []:
            # get column names from cursor description
            col_names = [x[0] for x in cursor.description]
            for entry in range(len(eKobew)):
                d = dict(zip(col_names, [val for val in eKobew[entry]] ))
                    
                print('TX_DATE:                      '+ str(d['TX_DATE']))
                print('CLOSING_DATE:                 '+ str(d['CLOSING_DATE']))
                print('MDT_CODE:                     '+ str(d['MDT_CODE']))
                print('KRT_EAN:                      '+ str(d['KRT_EAN']))
                print('KRT_CARD_NO:                  '+ str(d['KRT_CARD_NO']))
                print('Maggenta Order Nr:             '+ str(d['BTR_TX_REFERENCE_TEXT']))
                print('BTR_TX_ORIG_ID:               '+ str(d['BTR_TX_ORIG_ID']))
                print('BTR_POS_CODE:                 '+ str(d['BTR_POS_CODE']))
                print('ACT_DESCRIPTION:              '+ str(d['ACT_DESCRIPTION']))
                print('VALUE:                        '+ str(d['VALUE']))
                print('ACE_VALUE:                    '+ str(d['ACE_VALUE']))
                print('ACB_OPENING_BALANCE_VALUE:    '+ str(d['ACB_OPENING_BALANCE_VALUE']))
                print('ACB_CLOSING_BALANCE_VALUE:    '+ str(d['ACB_CLOSING_BALANCE_VALUE']))
                
                print('')
        else:
            print('card number not found \n')
    except AttributeError:
        print('There is no eKorso DB for country ' + c)
##################### eKorso Kontenbewegungen ##############################
        print((30*'<') + ' eKorso Bewegungen ' + 30*'<')
        
        

print(3*'\n')

if 'DEU' in countries:
    print((30*'°') + ' Maggenta Bestellungen mit dieser Kartennummer ' + 30*'°')
##################### Maggenta Bestellungen mit dieser Kartennummer ###########
    cursor = Maggenta_anmeldung()
    query = Maggenta_cardact.replace('k_num', card_no)

    mag_cardact = db_lookup(cursor,query)
    col_names = [x[0] for x in cursor.description]
    
    for entry in range(len(mag_cardact)):
        d = dict(zip(col_names, [val for val in mag_cardact[entry]] ))
        
        print('activation_id:		 ' + str(d['activation_id']))	
        print('item_id:                 ' + str(d['item_id']))
        print('order_id:                ' + str(d['order_id']))
        print('Maggenta Order ID:        ' + str(d['increment_id']))
        print('store_id:                ' + str(d['store_id']))
        print('user:                    ' + str(d['user']))
        print('aktivierungsdatum:       ' + str(d['aktivierungsdatum']))
        print('status:                  ' + str(d['status']))
        print('shipping_description:	 ' + str(d['shipping_description']))
        print('referenznummer:          ' + str(d['referenznummer']))

##################### Maggenta Bestellungen mit dieser Kartennummer ###########
    print((30*'°') + ' Maggenta Bestellungen mit dieser Kartennummer ' + 30*'°')

    
    
    

    print(3*'\n')
    
    print((15*'%') + ' Info from eKorsocheckout_eKorsopayment - "Alle Bestellungen zu einem UniversalCoupon" ' + 15*'%')
    
    

    query = ekontocheckout_ekontopayment.replace('k-num', card_no)
    
    ekocheckpay = db_lookup(cursor,query)
    col_names = [x[0] for x in cursor.description]
    
    for entry in range(len(ekocheckpay)):
        d = dict(zip(col_names, [val for val in ekocheckpay[entry]] ))
        
        print('Bestellnummer:   ' + str(d['Bestellnummer']))
        print('created_at:      ' + str(d['created_at'])   )
        print('Status:          ' + str(d['Status'])       )
        print('Saldo:           ' + str(d['Saldo'])        )
        print('bezahlt:         ' + str(d['bezahlt'])      )
        print('ausstehend:      ' + str(d['ausstehend'])   )
        print('Kunden-eMail:    ' + str(d['Kunden-eMail']) )
        print('\n')


    print((15*'%') + ' Info from ekontocheckout_ekontopayment - "Alle Bestellungen zu einem UniversalCoupon" ' + 15*'%')
    cursor.close()
print('done searching')

























