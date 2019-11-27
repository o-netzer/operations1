# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 17:17:07 2019

@author: netzer

The script lets you dump a portion of transaction data stored in a MySQL db into
a csv file without getting into troubles with the cache (if the portion is huge).

The input consists of 2 dates ('YYYY-MON-DAY') i.e. the date range of transactions,
a limitation on the number of db lines to be transferred at a time (limit),
the output csv file path and name,
and a csv dialect ('myDialect') determining the format of the ouput
"""

from mytoolbox import melde_dich_an #connection details for a my SQL db called "DWH"
from selects import Deu_ext # SELECT statement based on dates as input
import time, csv, timeit


################################ INPUT ############################################
from_date = '2008-04-23' #min=23-04-2008 
to_date = '2009-01-01'
limit = int(100)
file_path = r"Z:\Accounting\005_Brands\112_Controlling\Reporting\experimental\reservoir\dwh_2008.csv"

csv.register_dialect('myDialect',
quoting=csv.QUOTE_ALL,
lineterminator ='\n',
delimiter=';')
################################ INPUT ############################################

start_time = timeit.default_timer() #start time of overall computation

from_date = from_date + ' 00:00:00'
print(from_date)
to_date = to_date + ' 23:59:59'
print(to_date)


Deu_ext = Deu_ext.replace("BETWEEN 'date1' AND 'date2'",
                                "BETWEEN '" + str(from_date) + "' AND '"  + str(to_date) + "'")
print(Deu_ext)

cursor = melde_dich_an()
print('Mit DWH verbunden.')
cursor.execute(Deu_ext)
columns = [col[0] for col in cursor.description]

######### retrieve data 100 lines at a time and  #################################
with open(file_path, 'a') as f: # 'a' means append-mode (append data)
    writer = csv.writer(f, dialect='myDialect')
    writer.writerow(columns)
    while True:
        rows = cursor.fetchmany(limit)
        for i in rows:
            i = list(i)
            i[0] = i[0].strftime('%d.%m.%Y') #trans_date conversion
            i[8] = str(i[8]).replace(".",",") #
            i[9] = i[9].strftime('%d.%m.%Y')
#            print(i[0].strftime('%d.%m.%Y'), str(i[8]).replace(".",","), i[9].strftime('%d.%m.%Y'))
            writer.writerow(i)
        if not rows:
            break
    #    print(rows)
cursor.close()

    

print('overall duration: ' + str(timeit.default_timer() - start_time))
print('done')
