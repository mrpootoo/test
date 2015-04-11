# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor
from twisted.internet import protocol
import MySQLdb
import MySQLdb.cursors
import ConfigParser
import asyncore
import socket
import readline,thread,sys
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
# Pin Definitons:
r1Pin = 14 # Broadcom pin 14 (P1 pin 8)
r2Pin = 15 # Broadcom pin 15 (P1 pin 10)

GPIO.setup(r1Pin,GPIO.OUT)
GPIO.setup(r2Pin,GPIO.OUT)

config = ConfigParser.RawConfigParser()
config.read('lsapp.cfg')
dbhost = config.get('db','host')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')

class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data)
        if response:
            self.transport.write(response)

class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

    def __init__(self, app):
        self.app = app


from kivy.app import App
from kivy.uix.label import Label


class TwistedServerApp(App):
    def build(self):
        self.label = Label(text="server started\n")
        reactor.listenTCP(5000, EchoFactory(self))
        return self.label

    def handle_message(self, msg):
        msg = msg.strip()



        self.label.text = "received:  %s\n" % msg

        if msg == "r1on":
            GPIO.output(r1Pin, GPIO.LOW)
        if msg == "r1off":
            GPIO.output(r1Pin, GPIO.HIGH)
        if msg == "r2on":
            GPIO.output(r2Pin, GPIO.LOW)
        if msg == "r2off":
            GPIO.output(r2Pin, GPIO.HIGH)
        self.label.text += "responded: %s\n" % msg
        return msg


if __name__ == '__main__':
    TwistedServerApp().run()
