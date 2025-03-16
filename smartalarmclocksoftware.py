from itertools import filterfalse
import time
from numpy import True_
import serial
import asyncio
import datetime
arduinodata = serial.Serial('com14', 9600)
import threading
import sqlite3
import webbrowser
import os
import pywhatkit
import time
import pyautogui
import keyboard as k

loop = asyncio.get_event_loop()

conn = sqlite3.connect('alarminfo.db')
c = conn.cursor()

from kasa import Discover, SmartBulb, SmartPlug
import asyncio
time.sleep(1)

def formatSQLdata(content):
    content = str(content)
    for char in ",'()[]": # when retrieving data from a database, there is extra information e.g. brackets
        content = content.replace(char,'') # which does not need to be printed therefore this subroutine will remove extra unecessary character
    return content

c.execute("SELECT * FROM alarm")
alarm = c.fetchall()
alarm = formatSQLdata(alarm)

c.execute("SELECT deviceip FROM envtrigger WHERE type = 'temperature'")
selection1 = c.fetchall()
selection1 = formatSQLdata(selection1)

c.execute("SELECT deviceip FROM envtrigger WHERE type = 'humidity'")
selection2 = c.fetchall()
selection2 = formatSQLdata(selection2)

tempplug = ""
humidityplug = ""

stuff = ""

tempupper = 0
templower = 0

humupper = 0
humlower = 0

if(selection1 != "null"):
    tempplug = SmartPlug(selection1)

    c.execute("SELECT upperbound FROM envtrigger WHERE type = 'temperature'")
    stuff = c.fetchall()
    stuff = formatSQLdata(tempupper)
    tempupper = float(stuff)

    c.execute("SELECT lowerbound FROM envtrigger WHERE type = 'temperature'")
    stuff = c.fetchall()
    stuff = formatSQLdata(stuff)
    templower = float(stuff)

if(selection2 != "null"):
    humidityplug = SmartPlug(selection2)

    c.execute("SELECT upperbound FROM envtrigger WHERE type = 'humidity'")
    stuff = c.fetchall()
    stuff = formatSQLdata(stuff)
    humupper = float(stuff)

    c.execute("SELECT lowerbound FROM envtrigger WHERE type = 'humidity'")
    stuff = c.fetchall()
    stuff = formatSQLdata(stuff)
    humlower = float(stuff)

# - writing data will be for
# - sending alarm signal
# - sending time constantly
# - sending task at assigned time

def getcurrentdate():
    x = datetime.datetime.now()
    year = str(x.year)
    fulldate = str(x.month) + "/" + str(x.day) + "/" + year[2] + year[3]
    return fulldate

def openwebsite(weblink):
    webbrowser.open(weblink) 

def openapp(applink):
    os.startfile(applink)

def startcall(number):
    now = datetime.datetime.now()
    hours = int(now.strftime("%H"))
    minutes = int(now.strftime("%M")) + 2
    pywhatkit.sendwhatmsg(number, "Hi, can you call me if I forget to call you", hours, minutes, 30)
    pyautogui.click(1214, 974)

def writedata():
    conn = sqlite3.connect('alarminfo.db')
    c = conn.cursor()
    alarmsent = False
    prevdate = getcurrentdate()
    global alarm
    while True:
        # find alarm time
        now = datetime.datetime.now()
        today = getcurrentdate()

        if(today != prevdate):
            alarmsent = False

        current_time = now.strftime("%H:%M")
        cmd = current_time

        if(alarm == current_time and alarmsent == False):
            alarmsignal = 'al' + '\r'
            arduinodata.write(alarmsignal.encode())
            alarmsent = True

        c.execute("SELECT taskname FROM task WHERE date = (?) and time = (?) ",(today, cmd)) #I will try to order by date here
        currenttask = c.fetchall()
        currenttask = formatSQLdata(currenttask)

        if(currenttask == ""):
            cmd = cmd + '\r'
            arduinodata.write(cmd.encode())
            time.sleep(4)
        else:
            cmd = currenttask + '\r'
            arduinodata.write(cmd.encode())
            c.execute("SELECT triggertype FROM task WHERE taskname = (?) ",(currenttask,))
            triggertype = c.fetchall()
            triggertype = formatSQLdata(triggertype)
            c.execute("DELETE FROM task WHERE taskname = (?)",(currenttask,))
            conn.commit()
            if(triggertype == "website"):
                c.execute("SELECT triggerinfo FROM webtrigger WHERE taskname = (?) ",(currenttask,))
                trigger = c.fetchall()
                trigger = formatSQLdata(trigger)
                openwebsite(trigger)
                c.execute("DELETE FROM webtrigger WHERE taskname = (?)",(currenttask,))
                conn.commit()
            if(triggertype == "app"):
                c.execute("SELECT triggerinfo FROM apptrigger WHERE taskname = (?) ",(currenttask,))
                trigger = c.fetchall()
                trigger = formatSQLdata(trigger)
                openapp(trigger)
                c.execute("DELETE FROM apptrigger WHERE taskname = (?)",(currenttask,))
                conn.commit()
            if(triggertype == "whatsapp call"):
                c.execute("SELECT triggerinfo FROM calltrigger WHERE taskname = (?) ",(currenttask,))
                trigger = c.fetchall()
                trigger = formatSQLdata(trigger)
                startcall(trigger)
                c.execute("DELETE FROM calltrigger WHERE taskname = (?)",(currenttask,))
                conn.commit()
        
        prevdate = today
        # if current time is alarm time then do the above with the associated task of that time
        # select all tasks where time = currentime and date = todays date and encode and send
        # if the data is not equal to nothing send it 
        # else just send through the current time into the arduino

# reading data will be for
# - determining temp trigger to switch fan on and off

def readwritedata():
    global tempupper
    global templower
    global humupper
    global humlower
    global tempplug
    global humidityplug
    message1sent = False
    message2sent = False
    message3sent = False
    message4sent = False
    global loop
    time.sleep(2)
    while True:

        while(arduinodata.inWaiting() == 0):
            pass

        datapacket = arduinodata.readline()
        datapacket = str(datapacket, 'utf-8')
        datapacket = datapacket.strip('\r\n')
        #print(datapacket)
        
        contents = datapacket.split(",")
        temperature = float(contents[0])
        humidity = float(contents[1])

        if(tempplug != ""):

            if(temperature >= tempupper and message1sent == False):
              cmd = 'Th' + '\r'
              arduinodata.write(cmd.encode())

              try:
                loop.run_until_complete(turntempplugon())
              except:
                pass

              message1sent = True
              message2sent = False
        
            elif(temperature <= templower and message2sent == False):
              cmd = 'Tl' + '\r'
              arduinodata.write(cmd.encode())

              try:
                loop.run_until_complete(turntempplugoff())
              except:
                pass

              message1sent = False
              message2sent = True
        
        if(humidityplug != ""):

            if(humidity >= humupper and message3sent == False):
               cmd = 'Hh' + '\r'
               arduinodata.write(cmd.encode())

               try:
                loop.run_until_complete(turnhumplugon())
               except:
                pass

               message3sent = True
               message4sent = False
        
            elif(humidity <= humlower and message4sent == False):
               cmd = 'Hl' + '\r'
               arduinodata.write(cmd.encode())

               try:
                loop.run_until_complete(turnhumplugoff())
               except:
                pass

               message3sent = False
               message4sent = True

        # here we will see if the datapacket is equal to temptrigger
        # if it is we will switch on KASA smart plug

async def turntempplugon():
    global tempplug
    await tempplug.turn_on()
    
  
async def turntempplugoff():
    global tempplug
    await tempplug.turn_off()
    
    
async def turnhumplugon():
    global humidityplug
    await humidityplug.turn_on()

   
async def turnhumplugoff():
    global humidityplug
    await humidityplug.turn_off()
   
    
def formatSQLdata(content):
    content = str(content)
    for char in ",'()[]": # when retrieving data from a database, there is extra information e.g. brackets
        content = content.replace(char,'') # which does not need to be printed therefore this subroutine will remove extra unecessary character
    return content

sending_thread = threading.Thread(target = writedata) 
sending_thread.start()
recieving_thread = threading.Thread(target = readwritedata)
recieving_thread.start()
