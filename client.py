#!/usr/bin/python
import MySQLdb
import MySQLdb.cursors
import serial
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('socketsql.cfg')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')

import socket
import sys
import threading


class socket_client(threading.Thread):
    TCP_IP = "192.168.1.102"
    TCP_PORT = 23
    BUFFER_SIZE = 1024
    MESSAGE = "Hello, World!"

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.TCP_IP, self.TCP_PORT))
        sys.stdout.write("%s sending data: %s\n" % (self.__class__.__name__, self.MESSAGE))
        s.send(self.MESSAGE)
        while 1:
            buf = s.recv(1024)
            buf = buf.strip()

            if len(buf) > 0:
                print buf
                db = MySQLdb.connect(host=config.get('db','host'),user=dbuser,passwd=dbpass,db=dbdatabase, cursorclass=MySQLdb.cursors.DictCursor)
                cur = db.cursor()

                if len(buf) < 16:
                    cur.execute("insert into barcode set barcode=%s, scanby=%s",(buf,self.TCP_IP))
                else:
                    cur.execute("insert into barcode set barcode=%s, scanby=%s, special=%s, special2=%s, jobid=%s, seq=%s, runcmd=%s",(buf,self.TCP_IP,buf[0],buf[1],buf[2:10],buf[10:15],buf[15]))
                db.commit()
                db.close()
            if not buf:
                break


client = socket_client()

client.start()
