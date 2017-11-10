# -*- coding: utf-8 -*-
'''
Created on 2017/11/02

@author: CSYSBP01
'''

import psycopg2

import thread

# connection = psycopg2.connect("host=127.0.0.1 port=5432 dbname=detection user=postgres password=sysadmin")
# cur = connection.cursor()
# cur.execute("insert into api_count (cnt, created_at) values (%s, current_timestamp)",(1,))
# connection.commit()
w = thread.WriteThread(3)  # @UndefinedVariable
w.start()
w.join()
print("main end")