# install_twisted_rector must be called before importing  and using the reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()
from twisted.internet import reactor
from twisted.internet import protocol

import MySQLdb
import MySQLdb.cursors
import ConfigParser
import time

config = ConfigParser.RawConfigParser()
config.read('ls.cfg')
dbhost = config.get('db','host')
dbuser = config.get('db','user')
dbpass = config.get('db','pass')
dbdatabase = config.get('db','database')
myip = config.get('local','myip')

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
r1Pin = 14 # Broadcom pin 14 (P1 pin 8)
r2Pin = 15 # Broadcom pin 15 (P1 pin 10)
GPIO.setup(r1Pin,GPIO.OUT)
GPIO.setup(r2Pin,GPIO.OUT)
GPIO.output(r1Pin, GPIO.HIGH)
GPIO.output(r2Pin, GPIO.HIGH)

class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        response = self.factory.app.handle_message(data, self.transport.getPeer().host)
        #if response:
        #    self.transport.write(response)


class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

    def __init__(self, app):
        self.app = app


from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.widget import Widget
from keyboard import *
import requests

#payload = {'key1': 'value1', 'key2': 'value2'}
#r = requests.post("https://secure.letterstream.com/post", verify=True, data=payload) #verify=True forces ssl verify
#print(r.text)

class Operator:
    def __init__(self):
        self.currentoperator=''
    def changeOperator(self,operator):
        self.currentoperator = operator

    def loggedin(self):
        if len(self.currentoperator)==0:
            GPIO.output(r1Pin, GPIO.LOW)
            self.label.text="Please Scan Operator Badge"
            return False
        else:
            GPIO.output(r1Pin, GPIO.HIGH)
            self.label.text = "Current Operator: " + self.currentoperator
            return True

class Job:
    def __init__(self):
        self.currentjob = ''
        self.lastpiece = ''
        self.currentpiece = ''
    def changeJob(self,job):
        self.currentjob = job

class Status:
    def __init__(self):
        self.currentstatus = ''
    def changeStatus(self,status):
        self.currentstatus = status

class Mode:
    def __init__(self):
        self.currentmode = ''
    def changeMode(self,mode):
        self.currentmode = mode

class MainScreen(GridLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

        #content = Button(text='Close me!')
        #view = ModalView(auto_dismiss=False)
        #view.add_widget(content)
        #content.bind(on_press=view.dismiss)
        #view.open()

        self.myip = myip
        self.mode = Mode()
        self.operator = Operator()
        self.status = Status()
        self.job = Job()

        self.cols = 2
        self.operator.label = Label(text="no operator label", size_hint=(1, 1),markup=True)
        self.add_widget(self.operator.label)
        self.operator.loggedin()

        view = GridLayout(rows=2, row_force_default=True, row_default_height=40)
        self.status.job = Label(text="Current Job\n", size_hint=(1, 1),markup=True)
        view.add_widget(self.status.job)
        self.status.lastpiece = Label(text="Current Pc\n", size_hint=(1, 1),markup=True)
        view.add_widget(self.status.lastpiece)
        self.add_widget(view)

        self.textinput = Label(text="", size_hint=(1, 1),markup=True)
        self.add_widget(self.textinput)

        self.mainlabel = Label(text="", size_hint=(2, 1),markup=True)
        self.add_widget(self.mainlabel)


        #self.ReprintBtn = Button(text='Reprint')
        #self.ReprintBtn.bind(on_press=self.buttonpress)
        #self.add_widget(self.ReprintBtn)

        #view = BoxLayout(orientation='vertical', spacing=10)
        #toolbar = BoxLayout(size_hint=(1.0, None), height=50)
        #label = Label(text='Main', color=[.8, .8, .8, .8], bold=True)
        #toolbar.add_widget(label)
        #button = Button(text='Processes')
        #button.bind(on_press=self.buttonpress)
        #toolbar.add_widget(button)
        #view.add_widget(toolbar)
        #self.add_widget(view)


        reactor.listenTCP(5000, EchoFactory(self))
        MyKeyboardListener(self)
    def buttonpress(self,instance):
        print('The button <%s> is being pressed' % instance.text)

    def handle_message(self, msg, addr):
        msg = msg.strip()
        intlmsg = ''
        badscan = False

        if len(msg) > 0 and msg[0] == "U":
            self.operator.currentoperator = msg[1:]
            self.operator.label.text = "Current Operator: " +  msg[1:]

        if self.operator.loggedin() and len(msg) > 0:

            if msg[0] == "2":
                GPIO.output(r1Pin, GPIO.LOW)
                time.sleep(.1)
                GPIO.output(r1Pin, GPIO.HIGH)
                intlmsg = "\n[b][color=ff3333]******INTERNATIONAL******[/color][/b]\n\n"
            if msg == "ERROR" or msg == "NOREAD":
                GPIO.output(r1Pin, GPIO.LOW)
                time.sleep(.1)
                GPIO.output(r1Pin, GPIO.HIGH)
                intlmsg = "\n[b][color=33ff33]******PULL LAST ITEM AND RESCAN******[/color][/b]\n\n"
            if msg[0] != "U" and msg != "ERROR" and msg != "NOREAD" and len(msg) != 16:
                GPIO.output(r1Pin, GPIO.LOW)
                time.sleep(.1)
                GPIO.output(r1Pin, GPIO.HIGH)
                intlmsg = "\n[b][color=ffff33]******BAD SCAN PLEASE NOTIFY JONATHAN******[/color][/b]\n\n"
                badscan = True

            if len(msg) > 0:
                db = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpass,db=dbdatabase, cursorclass=MySQLdb.cursors.DictCursor)
                cur = db.cursor()

                if msg[0] != "U" and badscan==False and msg != "ERROR" and msg != "NOREAD":
                    cur.execute("select * from barcode where barcode=%s",(msg))

                    if cur.rowcount:
                        GPIO.output(r1Pin, GPIO.LOW)
                        time.sleep(.1)
                        GPIO.output(r1Pin, GPIO.HIGH)
                        intlmsg = "\n[b][color=3333ff]******DUPLICATE SCAN******[/color][/b]"

                if len(msg) < 16:
                    cur.execute("insert into barcode set barcode=%s, inserter=%s, operator=%s",(msg,addr,self.operator.currentoperator))
                else:
                    if self.job.currentjob != msg[2:10].strip():
                        self.status.job.text = "[b][color=3333ff]New Job: " + msg[2:10] + "[/color][/b]"
                    else:
                        self.status.job.text = "Current Job: " + msg[2:10]

                    cur.execute("insert into barcode set barcode=%s, inserter=%s, special=%s, special2=%s, jobid=%s, seq=%s, runcmd=%s, operator=%s",
                                    (msg,addr,msg[0],msg[1],msg[2:10],msg[10:15],msg[15],self.operator.currentoperator))

                    self.job.currentjob = msg[2:10].strip()
                    self.job.lastpiece = msg[10:15].strip()
                    self.status.lastpiece.text = "Last Pc: " + self.job.lastpiece
                db.commit()
                db.close()

            if len(intlmsg) > 0:
                msg += intlmsg

            screenmsg = self.mainlabel.text + "\nreceived: %s (%s)\n" % (msg,addr)
            lines = screenmsg.splitlines()
            lines = lines[-10:]
            screenmsg = "\n".join(lines)
            self.mainlabel.text = screenmsg

            return msg

class TwistedServerApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    TwistedServerApp().run()
