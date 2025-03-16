from tkinter import *
import tkinter
from tkcalendar import Calendar,DateEntry
import datetime
root = Tk()
import sqlite3
conn = sqlite3.connect('alarminfo.db')
c = conn.cursor()
from kasa import Discover, SmartBulb, SmartPlug
import asyncio

count = 0

async def discoverdevices():
    device = []
    devicedescription = []
    devices = await Discover.discover()
    for addr, dev in devices.items():
        #await dev.update()
        #print(f"{addr} >> {dev}")
        device.append(f"{addr}")
        devicedescription.append(f"{dev}")
    return device, devicedescription

def create_tables():
    c.execute("CREATE TABLE IF NOT EXISTS alarm(time TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS task(taskname TEXT, triggertype TEXT, date TEXT, time TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS apptrigger(taskname TEXT, triggerinfo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS webtrigger(taskname TEXT, triggerinfo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS calltrigger(taskname TEXT, triggerinfo TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS envtrigger(deviceip TEXT, upperbound TEXT, lowerbound TEXT, type TEXT)")


def deleteoperation():
    msg = selectitem()
    c.execute("DELETE FROM task WHERE taskname = (?)",(msg,))
    conn.commit() 
    listbox.delete(ANCHOR)

def selectitem():
    selected_indices = listbox.curselection()#gets selected items
    selected_langs = ",".join([listbox.get(i) for i in selected_indices])
    msg = f'{selected_langs}'
    msg = formatdata(msg)
    examiningsection = msg[len(msg)-11: len(msg)]
    if " » " in examiningsection:
        msg = msg.replace(examiningsection,'')

    return msg

def formatdata(content):
    content = str(content)
    for char in "⚪": # when retrieving data from a database, there is extra information e.g. brackets
        content = content.replace(char,'') # which does not need to be printed therefore this subroutine will remove extra unecessary character
    return content

def getcurrentdate():
    x = datetime.datetime.now()
    year = str(x.year)
    fulldate = str(x.month) + "/" + str(x.day) + "/" + year[2] + year[3]
    return fulldate


def loadinitialtasks():
    global count
    today = getcurrentdate()
    
    listbox.delete(0, END)
    c.execute("SELECT taskname FROM task WHERE date = (?)", (today,)) #I will try to order by date here
    currenttasks = c.fetchall()
    currenttasks = formatSQLlistdata(currenttasks)
    for task in currenttasks:
        listbox.insert(count, "⚪" + task)
        count = count + 1

    listbox.insert(count, "--------------------------------")
    count = count + 1

    c.execute("SELECT taskname FROM task WHERE date != (?)", (today,)) #I will try to order by date here
    noncurrenttasks = c.fetchall()
    noncurrenttasks = formatSQLlistdata(noncurrenttasks)
    for task in noncurrenttasks:
        c.execute("SELECT date FROM task WHERE taskname = (?)", (task,))
        taskdate = formatSQLdata(str(formatSQLlistdata(c.fetchall())))
        date = taskdate.split("/")
        if(date[0] != "12"):
            date[0] = "0" + date[0]
        if(len(date[1]) != 2):
            date[1] = "0" + date[1]
        listbox.insert(count, "⚪" + task + " » " + date[0]+ "/" + date[1] + "/" + date[2])
        count = count + 1

def formatSQLdata(content):
    content = str(content)
    for char in ",'()[]": # when retrieving data from a database, there is extra information e.g. brackets
        content = content.replace(char,'') # which does not need to be printed therefore this subroutine will remove extra unecessary character
    return content

def formatSQLlistdata(content):
    content = list(content)
    newcontent = []
    for item in content:
        item = str(item)
        for char in ",'()[]": # when retrieving data from a database, there is extra information e.g. brackets
            item = item.replace(char,'') # which does not need to be printed therefore this subroutine will remove extra unecessary character
        newcontent.append(item)
    newcontent = list(dict.fromkeys(newcontent))# which does not need to be printed therefore this subroutine will remove extra unecessary character
    return newcontent 


def addoperation():
    c.execute("INSERT INTO task(taskname, triggertype, date, time) VALUES (?,?,?,?)",(formatSQLdata(guess.get()), variable3.get(), cal.get(), tasktime.get()))
    conn.commit() 

    if(variable3.get() == "website"):
        c.execute("INSERT INTO webtrigger(taskname, triggerinfo) VALUES (?,?)",(formatSQLdata(guess.get()), triggerinfo.get()))
        conn.commit()
    
    if(variable3.get() == "app"):
        c.execute("INSERT INTO apptrigger(taskname, triggerinfo) VALUES (?,?)",(formatSQLdata(guess.get()), triggerinfo.get()))
        conn.commit()
    
    if(variable3.get() == "whatsapp call"):
        c.execute("INSERT INTO calltrigger(taskname, triggerinfo) VALUES (?,?)",(formatSQLdata(guess.get()), triggerinfo.get()))
        conn.commit()
    
    clearall()
    loadinitialtasks()

def clearall():

    tasktime.delete(0, END) 
    guess.delete(0, END)
    triggerinfo.delete(0, END)

def addtimeoperation():
    c.execute("DROP TABLE IF EXISTS alarm")
    c.execute("CREATE TABLE IF NOT EXISTS alarm(time TEXT)")

    c.execute("INSERT INTO alarm(time) VALUES (?)",(alarmtime.get(),))
    conn.commit()

def addtriggersettings():
    tempbounddata = temptrigger.get()
    humbounddata = humtrigger.get()

    tempbound = tempbounddata.split(",")
    humbound = humbounddata.split(",")

    c.execute("DROP TABLE IF EXISTS envtrigger")
    c.execute("CREATE TABLE IF NOT EXISTS envtrigger(deviceip TEXT, upperbound TEXT, lowerbound TEXT, type TEXT)")

    c.execute("INSERT INTO envtrigger(deviceip, upperbound, lowerbound, type) VALUES(?,?,?,'temperature')",(variable1.get(), tempbound[0], tempbound[1]))
    c.execute("INSERT INTO envtrigger(deviceip, upperbound, lowerbound, type) VALUES(?,?,?,'humidity')",(variable2.get(), humbound[0], humbound[1]))
    
    conn.commit()

langs = []
langs_var = StringVar(value=langs)

device, devicedescription = asyncio.run(discoverdevices())
device.append("null")

#devicelist = ["null", "IPaddress1", "IPaddress2"]
OPTIONS1 = device#etc#etc
OPTIONS2 = ["null",
            "website",
            "app",
            "whatsapp call"]

n = StringVar()

variable1 = StringVar(root)
variable2 = StringVar(root)
variable3 = StringVar(root)

variable1.set(OPTIONS1[0])
variable2.set(OPTIONS1[0])
variable3.set(OPTIONS2[0])

listbox = Listbox(
    root,
    listvariable=langs_var,
    height=12,
    
    width = 50,
    selectmode='extended')

listbox.grid(row = 2, column = 0)


alarmtime = Entry(root, width = 30, borderwidth = 5)
alarmtime.grid(row = 0, column = 1)
addtime = Button(root, text = "Add alarm time", padx = 100, command = addtimeoperation, bg = 'grey', fg = 'white', width = 10)
addtime.grid(row = 0, column = 0)
guess = Entry(root, width = 30 , borderwidth = 5)
guess.grid(row = 5, column = 0)
triggertype = OptionMenu(root, variable3, *OPTIONS2)
triggertype.grid(row = 6, column = 0)
triggerinfo = Entry(root, width = 30, borderwidth = 5)
triggerinfo.grid(row = 7, column = 0)
tasktime = Entry(root, width = 30, borderwidth = 5)
tasktime.grid(row = 8, column = 0)
addbtn = Button(root, text = "Add task", padx = 100, command = addoperation, bg = 'grey', fg = 'white', width = 10)
addbtn.grid(row = 4, column = 0)
deletebtn = Button(root, text = "Complete Task", padx = 100, command = deleteoperation, bg = 'grey', fg = 'white', width = 10)
deletebtn.grid(row = 3, column = 0)
cal = DateEntry(root, width=30, bg="darkblue", fg="white", year=2022)
cal.grid(row = 2, column = 1)
addtriggers = Button(root, text = "Add triggers", padx = 100, command = addtriggersettings, bg = 'grey', fg = 'white', width = 10)
addtriggers.grid(row = 4, column = 1)
temptrigger = Entry(root, width = 30 , borderwidth = 5)
temptrigger.grid(row = 5, column = 1)

showpeople = Label(root, text = str(devicedescription))
showpeople.grid(row = 0, column = 2)

tempdevice = OptionMenu(root, variable1, *OPTIONS1)
tempdevice.grid(row = 6, column = 1)

humtrigger = Entry(root, width = 30 , borderwidth = 5)
humtrigger.grid(row = 7, column = 1)

humdevice = OptionMenu(root, variable2, *OPTIONS1)
humdevice.grid(row = 8, column = 1)

alarmtime.insert(0, "HH:MM")
tasktime.insert(0, "HH:MM")
triggerinfo.insert(0, "phone number, website link or app location")
temptrigger.insert(0, "high temp,low temp (oC)")
humtrigger.insert(0, "high humidity,low humidity (%)")

create_tables()
loadinitialtasks()
root.mainloop()
