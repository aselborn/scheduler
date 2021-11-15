import sqlite3
from datetime import date, datetime
import time
from time import sleep
import calendar
import os

from worker import RepeatedTimer

def main():
    print("Python print hello")
    print("Current weekday = " + date.today().strftime('%A'))
    print("Current time : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # runloop()
    # runTimer("Anders")


def runloop():
    starttime = time.time()
    while True:
        print ("Tick, tack")
        time.sleep(60.0 - ((time.time() - starttime)%60))

def runTimer(name):
    print ("Hello %s" % name)


def readDb(database_file):
    # print(os.path.abspath(database_file))
    if not os.path.exists(database_file):
        print("Database file did not exist! => " + database_file)
        return
    else:
        sql = "SELECT d.DeviceId, Timepoint, Action FROM Device d inner join Schema c ON d.deviceId = c.deviceId"
        conn = sqlite3.connect(database_file)
        cur = conn.cursor()
        cur.execute(sql)
        current_devices = cur.fetchall()
        for row in current_devices:
            print(row)
        conn.close()
    
    os.system('dir')


    


if __name__ == '__main__':
    main()
    # rt = RepeatedTimer(1, runTimer, "World")
    # try:
        # sleep(5)
    # finally:
        # rt.stop()
    rt = RepeatedTimer(1, readDb, "db/config.db")
