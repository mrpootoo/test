#!/usr/bin/python
import MySQLdb
import MySQLdb.cursors
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('socketsql.cfg')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')

import socket
import sys
from thread import *


def clientthread(host,port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket object
    s.connect((host,port))

    while True:
        buf = s.recv(1024)
        buf = buf.strip()

        if len(buf) > 0:
            print buf
            db = MySQLdb.connect(host=config.get('db','host'),user=dbuser,passwd=dbpass,db=dbdatabase, cursorclass=MySQLdb.cursors.DictCursor)
            cur = db.cursor()

            if len(buf) < 16:
                cur.execute("insert into barcode set barcode=%s, inserter=%s",(buf,host))
            else:
                cur.execute("insert into barcode set barcode=%s, inserter=%s, special=%s, special2=%s, jobid=%s, seq=%s, runcmd=%s",(buf,host,buf[0],buf[1],buf[2:10],buf[10:15],buf[15]))
            db.commit()
            db.close()
        if not buf:
            break

    s.close()


host = '192.168.1.123' #Host i.p
port = 23 #Reserve a port for your service
start_new_thread(clientthread,(host,port))

host = '192.168.1.124' #Host i.p
port = 23 #Reserve a port for your service
start_new_thread(clientthread,(host,port))

while 1:
    pass
