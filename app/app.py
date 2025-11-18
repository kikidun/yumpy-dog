from flask import Flask, jsonify, request
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

#GET config or PUT/POST
@app.route('/config')
def config():
    conn = connectDB()
    print("connected db")
    cur = conn.cursor()
    print("cursor created")
    if request.method == 'GET':
        query = "SELECT * FROM config"
        cur.execute(query)
        print("query executed")
        config = cur.fetchall()
        print("results fetched")
        cur.close()
    elif request.method == 'PUT':
        return "Add?"
    elif request.method == 'POST':
        return "Update?"
    return config

#GET
@app.route('/data')
def getData():
    monitor, number = request.args.get('monitor'), request.args.get('number')
    conn = connectDB()
    print("data connected db")
    cur = conn.cursor()
    print("data cursor created")
    query = """
        SELECT * FROM healthcheck_data 
        WHERE monitor_id = %s 
        ORDER BY healthcheck_timestamp DESC 
        LIMIT %s
    """
    data = cur.execute(query, (monitor, number))
    print("data query executed")
    data = cur.fetchall()
   
    result = []
    #print(str(data))
    for row in data:
        result.append({
            "id": row[0],
            "timestamp": str(row[1]) if row[1] else None,
            "monitor_id": row[2],
            "response": row[3],
            "response_time": str(row[4]) if row[4] else None  # Convert timedelta to string
        })
        print(jsonify(result))
    return jsonify(result)


def queryDB(query):
    conn = connectDB()
    print("qdb connected db")
    cur = conn.cursor()
    print("qdb cursor created")
    cur.execute(query)
    print("qdb query executed")
    data = cur.fetchall()
    print("qdb results fetched")
    cur.close()
    return data


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5100)