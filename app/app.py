import datetime
from flask import Flask, jsonify, request
import psycopg2
import os
import time
from datetime import datetime
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

@app.route('/monitors', methods=['POST', 'GET'])
def getMonitors():
    conn = connectDB()
    print("connected db")
    cur = conn.cursor()
    print("cursor created")
    if request.method == 'GET':
        query = "SELECT * FROM monitors"
        cur.execute(query)
        print("query executed")
        config = cur.fetchall()
        print("results fetched")
        cur.close()
    elif request.method == 'POST':
        data = request.get_json()
        #name, url, interval, expected response
        if not data or 'name' not in data or 'url' not in data or 'interval' not in data or 'expected_response' not in data:
            return jsonify({"error": "name, url, interval and value are required"}), 400
        name = data['name']
        url = data['url']
        interval = data['interval']
        expected_response = data['expected_response']
        try:
            query = """
                    INSERT INTO monitors 
                    (name, url, interval, expected_response) VALUES (%s, %s, %s, %s)
                    RETURNING monitor_id
                """
            cur.execute(query, (name, url, interval, expected_response))
            result = cur.fetchone()
            monitor_id = result[0] if result else None
            conn.commit()

            if monitor_id:
                cur.close()
                return jsonify({"success": True, "monitor_id": monitor_id, "message": "Monitor created successfully"}), 200
            else:
                cur.close()
                return jsonify({"error": f"Failed to add monitor"}), 404
        except Exception as e:
            conn.rollback()  # Rollback on error
            cur.close()
            return jsonify({"error": str(e)}), 500
    return config
    return True

#GET config or PUT/POST
#add sanitization, 
@app.route('/config', methods=['POST', 'GET'])
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
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({"error": "key and value are required"}), 400
        key = data['key']
        value = data['value']
        try:
            query = """
                    UPDATE config 
                    SET value = %s, updated_at = %s 
                    WHERE key = %s
                """
            cur.execute(query, (value, datetime.now(), key))
            conn.commit()
            if cur.rowcount == 0:
                    return jsonify({"error": f"Config key '{key}' not found. Use PUT to create new."}), 404
            conn.commit()
            cur.close()
            return jsonify({"success": True, "key": key, "value": value}), 200
        except Exception as e:
            conn.rollback()  # Rollback on error
            cur.close()
            return jsonify({"error": str(e)}), 500
    return config

#TODO
#Multiple Monitors, timeframe, sanitizing variables
@app.route('/data')
def getData():
    data = request.get_json()
    if not data or 'monitor' not in data or 'number' not in data:
        return jsonify({"error": "monitor and number are required"}), 400
    monitor = data['monitor']
    number = data['number']
    
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


def queryDB(query, params):
    conn = connectDB()
    print("qdb connected db")
    cur = conn.cursor()
    print("qdb cursor created")
    cur.execute(query(params))
    print("qdb query executed")
    data = cur.fetchall()
    print("qdb results fetched")
    cur.close()
    return data


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5100)