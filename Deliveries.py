# -*- coding: utf-8 -*-
"""
Created on Fri May 20 17:36:31 2016

@author: netzer

The script fetches the latest transaction data (cumulative) from an Oracle db
and appends it to an Excel workbook. It uses module xlrd for reading Excel and
Mark Hammond's win32com.client to append data to the Excel workbook.
"""

from mytoolbox import selectCountryConnection, db_lookup
from selects import deliveries
import datetime
import sys


file_path = r"Z:\Accounts\Lieferungen.xlsx"
country = 'DEU'


###################Inspecting Excel Workbook#####################################
import xlrd
wb = xlrd.open_workbook(file_path)
x = wb.sheet_by_index(0)
highest_row = x.nrows
print('highest row: ' + str(highest_row ))

highest_row = x.nrows - 1

#last_update = datetime.datetime.strptime(last_update, "%Y%m%d").date()
last_update = x.cell(highest_row-1,4).value #if you take "highest_row", then IndexError: list index out of range
print('last update as stored by Excel: ' + str(last_update))
print(type(last_update))

print('')

#last_update = datetime.datetime.strptime(last_update, "%d.%m.%Y").date()
last_update = xlrd.xldate.xldate_as_datetime(last_update, wb.datemode)
print('last update as read by module xlrd: ' + str(last_update))
print(type(last_update))#<type 'datetime.datetime'>

print('')

year, month, day = last_update.year, last_update.month, last_update.day
last_update = datetime.date(year=year, month=month, day=day)
print('last_update converted: ' + str(last_update))
print(type(last_update))
print('')
current_date = datetime.date.today()
print('today is: ' + str(current_date))
print(type(current_date))

delta = current_date - last_update
print(type(delta))
#sys.exit('halt')


print('Data of how many days is fetched from the DWH? ' + str(delta.days))
if delta.days <= 1:
    sys.exit('There is no new data. Wait until tomorrow!')



#sys.exit('stop')
###################Inspecting Excel Workbook#####################################
date_format = "%d.%m.%Y"
print('...................')
select_from = last_update
print(select_from)
print(type(select_from))

select_from = select_from.strftime(date_format)
print(select_from)
print(type(select_from))

select_to = current_date
print(type(select_to))
select_to = select_to.strftime(date_format)
print(select_to)
print(type(select_to))
print('...................')

print('Start fetching now ...')


##################Fetching Data from an Oracle DB DWH##########################
deliveries = deliveries.replace("(D.XYZ_DATE < to_date(sysdate-1) and D.XYZ_DATE > to_date(sysdate-last_update))",
                                "(D.XYZ_DATE < to_date(sysdate) and D.XYZ_DATE > to_date(sysdate-" + str(delta.days-1) + "))")
print("(D.XYZ_DATE < to_date(sysdate) and D.XYZ_DATE > to_date(sysdate-" + str(delta.days-1) + "))")
print(deliveries)

#sys.exit('stop')

cursor = selectCountryConnection(country)

resultset = db_lookup(cursor, deliveries)

cursor.close()

print('Printing first 3 rows ...')
print(resultset[:3])

num_of_rows = len(resultset) 
##################Fetching Data from an Oracle DB DWH########################## 


##################Write Data into Excel Sheet###################################
import win32com.client
excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False
workbook = excel.Workbooks.Open(file_path)
sheet = workbook.Worksheets(1) #workbook.Sheets('Sheet1').Select(); sheet = xlApp.ActiveSheet
highest_row = highest_row + 1

counter = 0
for i in range(num_of_rows): #of course you can do that in a loop ... but beware of the indexing
    highest_row += 1
    sheet.Cells(highest_row,1).Value = resultset[i][0] #insert CODE
    sheet.Cells(highest_row,2).Value = resultset[i][1] #insert EAN
    sheet.Cells(highest_row,3).Value = resultset[i][2] #insert CDB_CODE
    sheet.Cells(highest_row,4).Value = resultset[i][3] #insert ANZAHL
    #year, month, day = resultset[i][4].year, resultset[i][4].month, resultset[i][4].day
    datum = (resultset[i][4]).date()

    print(datum)

    sheet.Cells(highest_row,5).Value = datum
    sheet.Cells(highest_row,6).Value = resultset[i][5]

#    print('----------------------------------------')
    counter += 1


workbook.Save()
workbook.Close()
excel.Quit()

print('Update is finished. New highest row = ' + str(highest_row))
print('Number of rows fetched from the DB: ' + str(num_of_rows))
print('Number of rows written into Excel: ' + str(counter))
print('All rows written: ' + str(num_of_rows == counter))
print('####################DELIVERIES DONE###############################')
##################Write Data into Excel Sheet###################################
