import sqlite3
from datetime import date, datetime
import time
from time import sleep, strftime
import calendar
import os 
import sys, getopt 
import subprocess
from worker import RepeatedTimer
from ctypes import util
from ctypes import *


def main():
    print("Python print hello")
    print("Current weekday = " + date.today().strftime('%A'))
    print("Current time : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    library = None
    libname = loadlibrary(library)

    if libname == None:
        print("Error cannot find library! Telldus-core must be installed.")
        exit(3)
    else:
        print("Library Loaded, appication Ok.")
    

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
    # read_device(1)
    if not os.path.exists(database_file):
        print("Database file did not exist! => " + database_file)
        return
    else:
        # print("Reading at time : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sql = "SELECT d.DeviceId, Timepoint, Action, DeviceName, LastCommand FROM Device d inner join Schema c ON d.deviceId = c.deviceId"
        conn = sqlite3.connect(database_file)
        cur = conn.cursor()
        cur.execute(sql)
        current_devices = cur.fetchall()
        for row in current_devices:
            now = datetime.now()                                
            date_time_obj = datetime.strptime(row[1], '%H:%M')
            hDiff = date_time_obj.hour - now.hour
            mDiff = date_time_obj.minute - now.minute

            if (hDiff == 0 and mDiff == 0):
                if row[2] == "on":
                    read_device(row[0])
                    send_command("on", database_file, row[0])
                if row[2] == "off":
                    read_device(row[0])
                    send_command("off", database_file, row[0])
                

        conn.close()
    

def send_command(last_command, db, id):
    print("Sending command {}".format(last_command))
    
    cmd = ""
    if last_command == "on":
        cmd = "tdtool -n " + str(id)
    else:
        cmd = "tdtool -f " + str(id)
    
    print(cmd)

    os.system(cmd)

    conn = sqlite3.connect(db)
    # sql = "UPDATE Device SET LastTimePoint = ?, LastCommand = ?, WHERE DeviceId = ?";
    sql = "UPDATE Device SET LastCommand = ?, LastTimePoint=? WHERE DeviceId = ?"
    cur = conn.cursor()
    
    # cur.execute(sql,  (datetime.now(), last_command, id))
    cur.execute(sql,  (last_command, datetime.now(), id))
    conn.commit()

def os_info():
    print ("Os info! " + os.name)
    return False

if __name__ == '__main__':
    main()
    # read_db("db/config.db")
    # rt = RepeatedTimer(1, runTimer, "World")
    # try:
        # sleep(5)
    # finally:
        # rt.stop()

    t = RepeatedTimer(10, read_db, "db/config.db")

    # read_device(1)
    # read_db()
