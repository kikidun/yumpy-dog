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

#for every entry in monitors, check the url, and put the result in the db
def working_logic(monitors):
    print("printing monitors")
    for row in monitors:
        print(row[1])
    print("")
    for monitor in monitors:
        health_check_result, send_time = checkURL(monitor[2])
        print(health_check_result.status_code)
        db_resp = update_DB(monitor, health_check_result, send_time)
        #print("db response:")
        #print(db_resp)


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