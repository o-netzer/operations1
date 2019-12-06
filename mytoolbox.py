# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 21:07:58 2016

@author: netzer

This .py file is a module for the operations1 project and contains
helper functions used in various scripts of that project.
"""

import cx_Oracle
import hashlib, sys


def db_connect_eService_Deu(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1521, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor
    
def db_connect_eService_AUT(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1522, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor

def db_connect_eService_CHE(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1521, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor
    
def db_connect_AUT(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1522, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor
    
def db_connect_DEU(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1521, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor

def db_connect_CHE(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1523, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor
    
def db_connect_eKonto(passwort):
    # Build a DSN (can be subsitited for a TNS name)
    dsn = cx_Oracle.makedsn("ip", 1522, "dbname")
    db = cx_Oracle.connect("user",passwort, dsn)
    cursor = db.cursor()
    return cursor


    
def db_lookup(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    return (rows)
    
def db_lookup_many(cursor, query, arraysize=1000):
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result

def increase_consecutive_no(no, limit):
    '''Given a number "no" as string consisting of less than "limit" digits
    this function returns the string "increased by 1" and left-side padded with leading
    zeros as long as the limit is not exceeded; otherwise it returns None
    Examples:
    >>> increase_consecutive_no('11111',6)
    '011112'
    >>> increase_consecutive_no('11111',5)
    '11112'
    >>> increase_consecutive_no('11111', 4)
    None
    >>> increase_consecutive_no('000001',6)
    '000002'
    >>> increase_consecutive_no('000001',10)
    '0000000002'
    >>> increase_consecutive_no('999999',6)
    None
    '''
    number = int(no) + 1
    number = str(number)
    if len(number) > limit:
        return None
    else:
        while len(number) < limit:
            number = '0'+ number
    return number


def padding_number(n):
    n = str(n)
    length = len(n)
    remaining = 6-length
    return (remaining*'0')+n


import os
def find_file_path(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

import MySQLdb
#def dwh_connect():
#    db = MySQLdb.connect(host="   .   .   . ",    # ip of your host, sometimes localhost
#                     user="...",         # your username
#                     passwd="...",  # your password
#                     db=...) #DB schema name
#    cursor = db.cursor()
#    return cursor


######################## DWH Verbindung ################################################
def melde_dich_an():
    #s_pwd = input('Anmeldung zur DWH: ')
    #s_pwd = r'schnitzler_traumnovelle_1926.txt'
    s_pwd = r'tastatur_deutsch.txt'

    with open(s_pwd, 'r') as f:
        s = f.read()
        host = s[1633]+s[1064]+s[2320]+s[672]+s[1832]+s[1946]+s[672]+s[1632]+s[1060]+s[2175]+s[866]+s[866]
#        host = s[59145]+s[82717]+s[30792]+s[172523]+s[168015]+s[171849]+s[4164]+s[36346]+s[21260]+s[85334]+s[84022]+s[41810]+s[118228]
        user = s[1471]+s[152]+s[125]+s[1133]+s[1464]+s[1849]
        passwd = s[770]+s[330]+s[536]+s[1085]+s[1709]+s[504]+s[1465]+s[1632]+s[872]+s[1631]+s[100]+s[1450]
        db = s[1841]+s[1490]+s[503]+s[533]+s[1726]+s[698]+s[312]+s[913]+s[1850]
        #print(host,user,passwd,db)
        return dwh_connect(host,user,passwd,db)
        
def melde_dich_an_neu():
    #s_pwd = input('Anmeldung zur DWH: ')
    #s_pwd = r'schnitzler_traumnovelle_1926.txt'
    s_pwd = r'tastatur_deutsch.txt'

    with open(s_pwd , 'r') as f:
        s = f.read()
        host = s[1635]+s[1064]+s[2320]+s[672]+s[1832]+s[1946]+s[672]+s[1632]+s[1060]+s[2175]+s[866]+s[866]
        user = s[1473]+s[152]+s[125]+s[1133]+s[1464]+s[1849]
        passwd = s[777]+s[330]+s[536]+s[1085]+s[1709]+s[504]+s[1465]+s[1632]+s[872]+s[1631]+s[100]+s[1450]
        db = s[1841]+s[1490]+s[503]+s[533]+s[1726]+s[698]+s[312]+s[913]+s[1850]
        #print(host,user,passwd,db)
        return dwh_connect(host,user,passwd,db)


def dwh_connect(host,user,passwd,db):
    db = MySQLdb.connect(host,user,passwd,db)
#                     user=...,         # your username
#                     passwd="...,  # your password
#                     db=...) #DB schema name
    cursor = db.cursor()
    return cursor
######################## DWH Verbindung ################################################

    
######################## Magento ################################################
def magento_anmeldung():
    s_pwd = r'tastatur_deutsch.txt'
    with open(s_pwd, 'r') as m:
        s = m.read()
        host = s[670]+s[488]+s[1011]+s[867]+s[1640]+s[1199]+s[1439]+s[104]+s[872]+s[1023]+s[1823]+s[1064]+s[101]

        user = s[915]+s[696]+s[152]+s[504]+s[1900]+s[1658]

        passw = s[322]+s[490]+s[1303]+s[1515]+s[1252]+s[1118]+s[914]+s[382]+s[506]+s[490]+s[155]+s[757]+s[141]+s[141]

        db = s[1101]+s[1495]+s[695]+s[1150]+s[536]+s[701]+s[557]+s[504]
        
        port = 3306

        return magento_connect(host, user, passw, db, port)

def magento_connect(host, user, passw, db, port):
    db = MySQLdb.connect(host,user,passw,db,port)
    cursor = db.cursor()
    return cursor
######################## Magento ################################################


#################### eGutschein Verbindung ###################################################
def selectCountryConnection(country):
    s_ = r'schnitzler_traumnovelle_1926.txt'
    with open(s_, 'r') as f:
        s = f.read()

    if country == 'AUT':
            cursor = db_connect_AUT(s[146492]+s[16056]+s[37096]+s[172615]+s[74859]+s[172606]+s[136496]+s[111913]+s[158493]+s[96510]+s[1355]+s[103017])
            print('connection established \n')

    if country == 'DEU':
            cursor = db_connect_DEU(s[154871]+s[75094]+s[89054]+s[172596]+s[99063]+s[143836]+s[86161]+s[138283]+s[143120]+s[168158]+s[140993]+s[73876])
            print('connection established \n')

    if country == 'CHE':
            cursor = db_connect_CHE(s[85575]+s[131554]+s[136603]+s[161312]+s[138351]+s[143835]+s[22078]+s[163771]+s[19088]+s[138528]+s[42108]+s[146708])
            print('connection established \n')

    return cursor
#################### eGutschein Verbindung ###################################################
    

    
#################### eService Verbindung ###################################################
def select_online_CountryConnection(country):
    s_ = r'tastatur_deutsch.txt'
    with open(s_, 'r') as f:
        s = f.read()

    if country == 'AUT':
            cursor = db_connect_eService_AUT(s[1901]+s[125]+s[145]+s[382]+s[863]+s[1342]+s[144]+s[1688]+s[1274]+s[1849]+s[1488]+s[751])
            print('connection established \n')

    if country == 'DEU':
            cursor = db_connect_eService_Deu(s[551]+s[1469]+s[1489]+s[190]+s[872]+s[1534]+s[144]+s[344]+s[1850]+s[505]+s[1296]+s[559])
            print('connection established \n')

    if country == 'CHE':
            cursor = db_connect_eService_CHE(s[1321]+s[701]+s[337]+s[382]+s[96]+s[958]+s[1296]+s[920]+s[1466]+s[1273]+s[1296]+s[175])
            print('connection established \n')

    return cursor    
#################### eService Verbindung ###################################################
    
#################### eKonto Verbindung ###################################################
def eKonto_connect(country):
    s_ = r'tastatur_deutsch.txt'
    with open(s_, 'r') as f:
        s = f.read()
        
        if country == 'DEU':
            cursor = db_connect_eKonto(s[946]+s[1851]+s[337]+s[1534]+s[95]+s[190]+s[1872]+s[1112]+s[314]+s[505]+s[720]+s[1135])
            print('connection established \n')
            return cursor
        else:
            return False
#################### eKonto Verbindung ###################################################

    
def ResultIter(cursor, arraysize=1000):
    'An iterator that uses fetchmany to keep memory usage down'
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result
            

def lst_as_row(lst,betw='\t',end='\n'):
    '''
    This function is desigend for writing the elements of a list 'lst' as one output string
    with given characters between the list elements ('betw') and a given special character
    at the end ('end').
    A typical application would be writing a list into a .txt file with tabs in between and
    a newline at the end of the row.
    
    Its input arguments are:
    'lst' designates a list (of whatever types of values)
    'betw'  (keyword-argument) designates any type convertible into a string
    'end'  (keyword-argument) designates any type convertible into a string but is put at the
    end of the output string.
    The function will return an empty line if lst is an empty list.
    
    Examples:
    x = ['ADLE04', 'AMAZ18', 'AMAZ23']
    y = []
    
    >>> print(lst_as_row(x,betw='\t',end='\n'))
    >>> ADLE04  AMAZ18  AMAZ23
    
    >>> print(lst_as_row(y,betw='\t',end='\n'))
    >>> 
    
    >>> print(lst_as_row(x,1,2))
    >>> ADLE041AMAZ181AMAZ2312
    
    >>> print(lst_as_row(x))
    >>> ADLE04  AMAZ18  AMAZ23    
    '''
    row = ''
    for i in range(len(lst)):
        row = row + str(lst[i]) + str(betw)
    return row + str(end)
    
    

import datetime
def conv_datetime2iso(source):
    '''Given any list or tuple of data (source) this function searches for datetime objects and
    replaces those objects by isoformat strings for better readability; it leaves the source
    unchanged if empty or not containing any datetime objects.
    '''
    import datetime
    counter = -1
    if len(source) == 0:
        pass
    else:
        not_list = ''
        if type(source) == tuple:
            not_list = 'yes'
            source = list(source)
        for i in source:
            counter = counter + 1
            if type(i) == datetime.datetime:
                source[counter] = (source[counter]).isoformat()
        if not_list == 'yes':
            source = tuple(source)
    return source




