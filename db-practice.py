import psycopg2
import requests
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

#Retrieves the entire monitor table to get urls from. 
#todo: look at refining
def getMonitors():
    query = "SELECT * FROM monitors"
    cur.execute(query)
    monitors = cur.fetchall()

    return monitors

#HTTP get of a given URL, return response
#todo: use the timestamp too
def checkURL(URL):
    print("Sending request to "+URL)
    send_timestamp = datetime.now()
    resp = requests.get(URL, verify=False)

    return resp   

#put the result of the health check back in the db
#todo: make this work
def update_DB(monitor_name, health_check_result):
    #this will parse the result and put it in the db
    print("Loading the database with a "+ str(health_check_result) +" for "+ monitor_name)
    return True

#
def working_logic(monitors):
    print("printing monitors")
    for row in monitors:
        print(row[1])
    print("")
    for monitor in monitors:
        hc_result = checkURL(monitor[2])
        print(hc_result.status_code)
        db_resp = update_DB(monitor[1], hc_result.status_code)


monitors = getMonitors()
working_logic(monitors)



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