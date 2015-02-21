#!/usr/bin/python
import MySQLdb
import MySQLdb.cursors
import serial
config = {};

db = MySQLdb.connect(host="localhost",user="root",passwd="",db="lsdb", cursorclass=MySQLdb.cursors.DictCursor)
cur = db.cursor() 


cur.execute("SELECT * from config")
result = cur.fetchall()
for row in result:
	config[row['k']] = row['v']

ser = serial.Serial(config['ser_port'], config['ser_baud'])


while True:
  myval = ser.readline()
	print myval
	cur.execute("insert into serial set data=%s",(myval))
	db.commit()
