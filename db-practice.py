import psycopg2
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="pwtest"
)

cur = conn.cursor()
print("connected to DB")

def getConfig():
    query = "SELECT * FROM config"
    cur.execute(query)
    config = cur.fetchall()
    return config

config = getConfig()

#print out the config, gotta set these better somehow
print("printing configuration:")
for key in config:
    print(key[0] + ": " + key[1])


test = getConfig()[0][1]
print("test")
print(test)

#Retrieves the entire monitor table to get urls from. 
#todo: look at refining
def getMonitors():
    query = "SELECT * FROM monitors"
    cur.execute(query)
    monitors = cur.fetchall()

    return monitors

#HTTP get of a given URL, return response and timestamp
def checkURL(URL):
    print("Sending request to "+URL)
    send_timestamp = datetime.now()
    resp = requests.get(URL, verify=False)

    return resp, send_timestamp   

#put the result of the health check in the db, update last checked
def update_DB(monitor, health_check_result, send_time):
    print("Loading the database with a "+ str(health_check_result) +" for "+ monitor[1])
    try:
        cur.execute("INSERT INTO healthcheck_data ( healthcheck_timestamp, monitor_id, response, response_time) VALUES (%s, %s, %s, %s)",
        (send_time, monitor[0], health_check_result.status_code, health_check_result.elapsed))
        cur.execute("UPDATE monitors SET last_checked =%s WHERE monitor_id = %s",(send_time, monitor[0]))
        conn.commit()
        print("Commit successful!")
    except Exception as e:
        conn.rollback()  # Undo all changes in this transaction
        print("Commit failed!")
        print(f"Error: {e}")
    return True





#every X number of seconds, query the monitor table for entries where last checked + interval is less than now
#check those monitors

#for every entry in monitors, check the url, and put the result in the db
#todo: the loop isn't quite working, its going too fast

def working_logic(monitors):
    #if worker_enabled true
    enabled = config[0][1] 
    while True:
        enabled = getConfig()[0][1]
        print(str(datetime.now())+" LOG: enabled is set to " + enabled)
        if enabled:
            print(str(datetime.now())+" printing monitors")
            for row in monitors:
                print(row[1])
            print("")
            for monitor in monitors:
                health_check_result, send_time = checkURL(monitor[2])
                print(health_check_result.status_code)
                db_resp = update_DB(monitor, health_check_result, send_time)
            print(str(datetime.now())+" LOG: Setting 'enabled' to : "+ str(getConfig()[0][1]))    
            time.sleep(10)
        else:
            print(str(datetime.now())+" LOG: because enabled is set to " + enabled + ", Sleep for 30s")
            time.sleep(10)






monitors = getMonitors()
working_logic(monitors)

cur.close()
conn.close()

# Insert data
#cur.execute(
#    "INSERT INTO users (name, email) VALUES (%s, %s)",
#    ("Alice", "alice@example.com")
#)

#print("Sending to DB")
#print( send_timestamp, resp.status_code, resp.elapsed)
#cur.execute(
#    "INSERT INTO healthcheck_data ( healthcheck_timestamp, monitor_id, response, response_time) VALUES (%s, %s, %s, %s)",
#    (send_timestamp, 1, resp.status_code, resp.elapsed)
#)

# Commit changes
#conn.commit()