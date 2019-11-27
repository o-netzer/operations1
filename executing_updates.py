# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 09:25:12 2017

@author: netzer

This is a start script for a series of update scripts each of which fetches the
latest data from either some Oracle or a MySQL data base and saves it in some
output file (for details see the given paths below in the input section).
The script can be started at any time as often as you like - it will either
process the data if available or do no harm otherwise.
"""

##################### Input ##################################################
paths = [r'C:\Users\netzer\Meins\PythonScripts\operations\CHE_Auswertung.py',
         r'C:\Users\netzer\Meins\PythonScripts\operations\AUT_Auswertung.py',
         r'C:\Users\netzer\Meins\PythonScripts\operations\Deliveries.py',
         r'C:\Users\netzer\Meins\PythonScripts\operations\bereits_aktiviert.py']
##################### Input ##################################################


for update in paths:
    try:
        exec(open(update).read(), globals())
    except SystemExit:
        print('No new data')
        print('-----------------------------------------------------')
        print('')
        continue
