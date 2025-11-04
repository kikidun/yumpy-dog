import psycopg2
import requests
from datetime import datetime



#conn = psycopg2.connect("dbname=yump-test user=postgres password=pwtest")
print("imported stuff")
conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="pwtest"
)
print("Variables set")
cur = conn.cursor()
print("connected to DB")
# Execute a query
#cur.execute("SELECT * FROM my_data")

# Retrieve query results
#records = cur.fetchall()


#make the http request
print("Sending request")
send_timestamp = datetime.now()
resp = requests.get("https://flyfi.com")
print(resp.status_code)
#format it and insert it

# Insert data
#cur.execute(
#    "INSERT INTO users (name, email) VALUES (%s, %s)",
#    ("Alice", "alice@example.com")
#)

print("Sending to DB")
print( send_timestamp, resp.status_code, resp.elapsed)
cur.execute(
    "INSERT INTO healthcheck_data ( healthcheck_timestamp, monitor_id, response, response_time) VALUES (%s, %s, %s, %s)",
    (send_timestamp, 1, resp.status_code, resp.elapsed)
)

# Commit changes
conn.commit()
