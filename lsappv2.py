# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor
from twisted.internet import protocol
import MySQLdb
import MySQLdb.cursors
import ConfigParser
import RPi.GPIO as GPIO
import time

config = ConfigParser.RawConfigParser()
config.read('lsapp.cfg')
dbhost = config.get('db','host')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')

GPIO.setmode(GPIO.BCM)
# Pin Definitons:
r1Pin = 14 # Broadcom pin 14 (P1 pin 8)
r2Pin = 15 # Broadcom pin 15 (P1 pin 10)
GPIO.setup(r1Pin,GPIO.OUT)
GPIO.setup(r2Pin,GPIO.OUT)

class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data, self.transport.getPeer().host)
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

    def handle_message(self, msg, addr):
        msg = msg.strip()
        intlmsg = ''

        if msg[0] == "2":
            GPIO.output(r1Pin, GPIO.LOW)
            time.sleep(.5)
            GPIO.output(r1Pin, GPIO.HIGH)
            intlmsg = "******INTERNATIONAL******"
        if msg == "r1off":
            GPIO.output(r1Pin, GPIO.HIGH)
        if msg == "r2on":
            GPIO.output(r2Pin, GPIO.LOW)
        if msg == "r2off":
            GPIO.output(r2Pin, GPIO.HIGH)

        if len(msg) > 0:
            db = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpass,db=dbdatabase, cursorclass=MySQLdb.cursors.DictCursor)
            cur = db.cursor()

            if len(msg) < 16:
                cur.execute("insert into barcode set barcode=%s, inserter=%s",(msg,addr))
            else:
                cur.execute("insert into barcode set barcode=%s, inserter=%s, special=%s, special2=%s, jobid=%s, seq=%s, runcmd=%s",(msg,addr,msg[0],msg[1],msg[2:10],msg[10:15],msg[15]))
            db.commit()
            db.close()

        if len(intlmsg) > 0:
            msg += intlmsg

        screenmsg = self.label.text + "received: %s (%s)\n" % (msg,addr)
        if len(screenmsg) > 300:
            screenmsg = screenmsg[-300:]
        self.label.text = screenmsg

        return msg


if __name__ == '__main__':
    TwistedServerApp().run()
