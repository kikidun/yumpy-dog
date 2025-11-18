from flask import Flask, jsonify
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

_conn = None

def connectDB():
    global _conn
    if _conn is None or _conn.closed:
        max_retries = 5
        for attempt in range(max_retries):
            try:
                _conn = psycopg2.connect(
                    host=os.getenv("PG_HOST", "db"),
                    dbname=os.getenv("PG_DATABASE", "yump_db"),
                    user=os.getenv("PG_USER", "yumpy"),
                    password=os.getenv("DB_PASSWORD")
                )
                print("Connected!")
                return _conn
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print("Connection failed!")
                    print(f"Error: {e}")
                    exit()
    return _conn


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/status')
def getStatus():
    return True

@app.route('/monitors')
def getMonitors():
    return True

@app.route('/config')
def getConfig():
    conn = connectDB()
    print("connected db")
    cur = conn.cursor()
    print("cursor created")
    query = "SELECT * FROM config"
    cur.execute(query)
    print("query executed")
    config = cur.fetchall()
    print("results fetched")
    cur.close()
    return config

config = getConfig()
print("printing configuration:")
for key in config:
    print(key[0] + ": " + key[1])
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')