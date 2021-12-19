import sqlite3
from datetime import date, datetime
import time
from time import sleep, strftime
import calendar
import os 
import sys, getopt 

from worker import RepeatedTimer
from ctypes import util
from ctypes import *


def main():
    print("Python print hello")
    print("Current weekday = " + date.today().strftime('%A'))
    print("Current time : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    isOk = os_info()

    if not isOk :
        print("Wrong OS")
        exit(3)

    library = None
    libname = loadlibrary(library)

    if libname == None:
        print("Error cannot find library! Telldus-core must be installed.")
        exit(3)
    else:
        print("Library Loaded.")
    

def loadlibrary(libraryname=None):
    if libraryname == None:
        libraryname="telldus-core"
    
    ret = util.find_library(libraryname)

    if ret == None:
        print("Library, not found")
        return

    
    global libtelldus
    
    libtelldus = cdll.LoadLibrary(ret)
    libtelldus.tdGetName.restype = c_char_p
    libtelldus.tdLastSentValue.restype = c_char_p
    libtelldus.tdGetProtocol.restype = c_char_p
    libtelldus.tdGetModel.restype = c_char_p
    libtelldus.tdGetErrorString.restype = c_char_p
    libtelldus.tdLastSentValue.restype = c_char_p

    return ret, libraryname


def read_device(identity):
    name = libtelldus.tdGetName(identity)
    lastcmd = libtelldus.tdLastSentCommand(identity, 1)

    
    if lastcmd == 1:
        print("Last command was ON.")
    else:
        print ("Last command was OFF!")


def run_loop():
    starttime = time.time()
    while True:
        print ("Tick, tack")
        time.sleep(60.0 - ((time.time() - starttime)%60))

def runTimer(name):
    print ("Hello %s" % name)


def read_db(database_file):
    # print(os.path.abspath(database_file))
    read_device(1)
    if not os.path.exists(database_file):
        print("Database file did not exist! => " + database_file)
        return
    else:
        print("Reading at time : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sql = "SELECT d.DeviceId, Timepoint, Action, DeviceName, LastCommand FROM Device d inner join Schema c ON d.deviceId = c.deviceId"
        conn = sqlite3.connect(database_file)
        cur = conn.cursor()
        cur.execute(sql)
        current_devices = cur.fetchall()
        for row in current_devices:
            now = datetime.now()
            h, m = map(int, row[1].split(':'))
            if (row[2] == "on"):
                if h == now.hour and m == now.minute:
                    print("DeviceId ", row[0], "Is On at ", row[1])
                    send_command("on", database_file, row[0])
        conn.close()
    

def send_command(last_command, db, id):
    print("Sending command", last_command)
    
    conn = sqlite3.connect(db)
    sql = "UPDATE Device SET LastTimePoint = ?, LastCommand = ?, WHERE DeviceId = ?", (datetime.now(), last_command, id)
    cur = conn.cursor()
    
    cur.execute(sql)
    conn.commit()

def os_info():
    print ("Os info! " + os.name)
    return False

if __name__ == '__main__':
    main()
    # rt = RepeatedTimer(1, runTimer, "World")
    # try:
        # sleep(5)
    # finally:
        # rt.stop()
    
    rt = RepeatedTimer(1, read_db, "db/config.db")

    # read_device(1)
    # read_db()
