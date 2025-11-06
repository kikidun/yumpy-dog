import psycopg2
import requests
import time
from datetime import datetime


conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="pwtest"
)


print("connected to DB")

def getConfig():
    cur = conn.cursor()
    query = "SELECT * FROM config"
    cur.execute(query)
    config = cur.fetchall()
    cur.close()
    return config

config = getConfig()

#print out the config, gotta set these better somehow
print("printing configuration:")
for key in config:
    print(key[0] + ": " + key[1])

#Retrieves the entire monitor table to get urls from. 
def getMonitors():
    cur = conn.cursor()
    query = "SELECT * FROM monitors"
    cur.execute(query)
    monitors = cur.fetchall()
    cur.close()
    return monitors

#query the monitor table for entries where last checked + interval is less than now
def getMonitorsForChecking():
    conn.commit()
    cur = conn.cursor()
    cur.execute("SELECT * FROM monitors m WHERE m.last_checked + (m.interval * INTERVAL '1 second') < CURRENT_TIMESTAMP")
    monitorsForChecking = cur.fetchall()
    #print("monitors for checking: "+ str(monitorsForChecking))
    cur.close()
    return monitorsForChecking

#HTTP get of a given URL, return response and timestamp
def checkURL(URL):
    #print("Sending request to "+URL)
    send_timestamp = datetime.now()
    resp = requests.get(URL, verify=False)

    return resp, send_timestamp   

#put the result of the health check in the db, update last checked
def update_DB(monitor, health_check_result, send_time):
    cur = conn.cursor()
    print("Loading the database with a "+ str(health_check_result) +" for "+ monitor[1])
    try:
        cur.execute("INSERT INTO healthcheck_data ( healthcheck_timestamp, monitor_id, response, response_time) VALUES (%s, %s, %s, %s)",
        (send_time, monitor[0], health_check_result.status_code, health_check_result.elapsed))
        cur.execute("UPDATE monitors SET last_checked =%s WHERE monitor_id = %s",(send_time, monitor[0]))
        conn.commit()
        #print("Commit successful!")
    except Exception as e:
        conn.rollback()  # Undo all changes in this transaction
        print("Commit failed!")
        print(f"Error: {e}")
    cur.close()
    return True


def working_logic():
    while True:
        conn.commit()
        enabled = getConfig()[0][1]
        #print(str(datetime.now())+" LOG: enabled is set to " + enabled)
        if enabled.strip() == "True":
            monitors = getMonitorsForChecking()
            #print(monitors)
            if len(monitors) == 0:
                time.sleep(1)
            else:
                for monitor in monitors:
                    health_check_result, send_time = checkURL(monitor[2])
                    #print(health_check_result.status_code)
                    update_DB(monitor, health_check_result, send_time)
            #print(str(datetime.now())+" LOG: Setting 'enabled' to : "+ str(getConfig()[0][1]))    
                time.sleep(1)
        else:
            #print(str(datetime.now())+" LOG: because enabled is set to " + enabled + ", Sleep for 10s")
            time.sleep(1)


working_logic()

conn.close()
