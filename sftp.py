# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 14:49:16 2016

@author: netzer

This .py file is a module for the operations1 project and only contains
sftp-connection procedures used by some scripts of that project. For security
reasons the procedures was faked.
"""

import pysftp, sys
#import hashlib


##########################################################
s_pwd = r'tastatur_deutsch.txt'
with open(s_pwd , 'r') as f:
    s = f.read()
    sftp = pysftp.Connection('ip',
                         port=22,
                         username='user',
                         password=(s[1111]+s[1651]+s[1475]+s[550]+s[1212]+s[1903]+s[1056]+s[528]))
##########################################################

print(sftp)


##########################################################
s_pwd = r'tastatur_deutsch.txt'
with open(s_pwd , 'r') as f:
    s = f.read()
    sftp_eServ_AUT = pysftp.Connection('ip',
                         port=22,
                         username='user',
                         password=(s[1112]+s[125]+s[1064]+s[455]+s[1212]+s[1709]+s[930]+s[1668]))
##########################################################

