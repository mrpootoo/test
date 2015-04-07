#!/usr/bin/python

import readline,thread,sys
import socket
import time

#TCP_IP = "127.0.0.1"
TCP_IP = "192.168.1.134"
TCP_PORT = 5000
BUFFER_SIZE = 1024
MESSAGE = ""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

def noisy_thread():
    while True:
        time.sleep(3)
        sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())+2)+'\r')
        print 'Interrupting text!'
        sys.stdout.write('Scan: ' + readline.get_line_buffer())
        sys.stdout.flush()

thread.start_new_thread(noisy_thread, ())

while 1:
    scan=raw_input("Scan: ")
    if scan in ["Q","q"]: break
    print 'Manual Scan: ' + scan
    s.send(scan)
s.close()
