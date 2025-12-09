import datetime
from flask import Flask, jsonify, request, render_template
import psycopg2
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import logging.config
import pathlib
import json 

logger = logging.getLogger("app")

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s"
        },
        "timestamped": {
            "format": "%(levelname)s %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "timestamped",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": [
                "stdout"
            ]
        }
    }
}
#keeping inline logger config for now
def configLogging():
#    config_file = pathlib.Path("config.json")
#    with open(config_file) as f_in:
#        config = json.load(f_in)
    logging.config.dictConfig(logging_config)


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
                logger.info("Connected!")
                return _conn
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Connection failed!")
                    logger.error(f"Error: {e}")
                    exit()
    return _conn

def getMonitors():
    conn = connectDB()
    logger.debug("getMonitors connection opened")
    cur = conn.cursor()
    query = "SELECT * FROM monitors"
    cur.execute(query)
    logger.debug("getMonitors query executed")
    monitors = cur.fetchall()
    logger.debug("getMonitors results fetched")
    cur.close()
    logger.debug("getMonitors connection closed")
    logger.debug("json monitors:")
    logger.debug(jsonify(monitors))
    logger.debug("monitors:")
    logger.debug(str(monitors))
    return monitors

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/status')
def getStatus():
    return True

@app.route('/monitors', methods=['GET'])
def monitors():
    monitors = getMonitors()
    logger.debug("json monitors:")
    logger.debug(jsonify(monitors))
    logger.debug("monitors:")
    logger.debug(str(monitors))
    return render_template("monitors.html", monitors=monitors)

@app.route('/api/v1/monitors', methods=['POST', 'GET', 'PUT', 'DELETE'])
def getMonitors():
    logger.debug(f"Route hit with URL: {request.url}")
    logger.debug(f"Request method: {request.method}")
    if request.method in ['POST', 'PUT', 'DELETE']:
        logger.debug(f"Body received: {request.json}")
    conn = connectDB()
    logger.debug("connected db")
    cur = conn.cursor()
    logger.debug("cursor created")
    if request.method == 'GET':
        query = "SELECT * FROM monitors"
        cur.execute(query)
        logger.debug("query executed")
        result = cur.fetchall()
        logger.debug("results fetched")
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
            logger.debug("create query executed")
            conn.commit()
            logger.debug("create query committed")
            result = cur.fetchone()
            logger.debug("create query fetched")
            monitor_id = result[0] if result else None
            

            if monitor_id:
                cur.close()
                return jsonify({"success": True, "monitor_id": monitor_id, "message": "Monitor created successfully"}), 200
            else:
                cur.close()
                return jsonify({"error": f"Failed to add monitor"}), 404
        except Exception as e:
            conn.rollback()  # Rollback on error
            cur.close()
            return jsonify({"POST error": str(e)}), 500

    elif request.method == 'PUT':
        data = request.get_json()
        if not data or 'name' not in data or 'url' not in data or 'interval' not in data or 'expected_response' not in data or 'monitor_id' not in data:
            logger.error("monitor_id, name, url, interval and value are required")
            return jsonify({"error": "monitor_id, name, url, interval and expected_response are required"}), 400
        name = data['name']
        url = data['url']
        interval = data['interval']
        monitor_id = data['monitor_id']
        expected_response = data['expected_response']
        try:
            query = """
                    UPDATE monitors 
                    SET name = %s, url = %s, interval = %s, expected_response = %s
                    WHERE monitor_id = %s
                    RETURNING monitor_id, name, url, interval, expected_response, last_checked
                    """
            cur.execute(query, (name, url, interval, expected_response, monitor_id))
            logger.debug("update query executed")
            conn.commit()
            logger.debug("update query committed")
            result = cur.fetchone()
            logger.debug("update result fetched")

            if result:
                cur.close()
                return jsonify({
                    "success": True, 
                    "monitor_id": result[0], 
                    "name": result[1], 
                    "url": result[2], 
                    "interval": result[3], 
                    "expected_response": result[4],
                    "last_checked": str(result[5]) if result[5] else None,
                    "message": "Monitor updated successfully"
                }), 200                #error_message = jsonify({"error": f"Config key '{key}' not found. Use PUT to create new."})
                #logger.error(error_message)
                #return error_message, 404
                return jsonify({"error": f"Failed to update monitor"}), 404
            else:
                cur.close()
                return jsonify({"error": f"Failed to update monitor"}), 404
        except Exception as e:
            conn.rollback()  # Rollback on error
            cur.close()
            return jsonify({"PUT error": str(e)}), 500
    #i
    elif request.method == 'DELETE':
        data = request.get_json()
        if not data or 'monitor_id' not in data:
            logger.error("monitor_id is required")
            return jsonify({"error": "monitor_id is required"}), 400
        monitor_id = data['monitor_id']
        try:
            query = """
                    DELETE FROM monitors
                    WHERE monitor_id = %s
                    RETURNING monitor_id, name, url, interval, expected_response, last_checked
                    """
            logger.debug("delete query formatted")       
            cur.execute(query, (monitor_id,))
            logger.debug("delete query executed")
            conn.commit()
            logger.debug("delete query committed")
            result = cur.fetchone()
            logger.debug("delete result fetched")

            if result:
                cur.close()
                return jsonify({
                    "success": True, 
                    "monitor_id": result[0], 
                    "name": result[1], 
                    "url": result[2], 
                    "interval": result[3], 
                    "expected_response": result[4],
                    "last_checked": str(result[5]) if result[5] else None,
                    "message": "Monitor deleted successfully"
                }), 200
            else:
                cur.close()
                return jsonify({"error": f"Monitor not found"}), 404


        except Exception as e:
            conn.rollback()  # Rollback on error
            cur.close()
            return jsonify({"DELETE error": str(e)}), 500
    return result

#GET config or PUT/POST
@app.route('/api/v1/config', methods=['POST', 'GET'])
def config():
    conn = connectDB()
    logger.debug("connected db")
    cur = conn.cursor()
    logger.debug("cursor created")
    if request.method == 'GET':
        query = "SELECT * FROM config"
        cur.execute(query)
        logger.debug("query executed")
        config = cur.fetchall()
        logger.debug("results fetched")
        cur.close()
    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'key' not in data or 'value' not in data:
            logger.error("error: key and value are required")
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
                error_message = jsonify({"error": f"Config key '{key}' not found. Use PUT to create new."})
                logger.error(error_message)
                return error_message, 404
            cur.close()
            return jsonify({"success": True, "key": key, "value": value}), 200
        except Exception as e:
            conn.rollback()  # Rollback on error
            cur.close()
            return jsonify({"error": str(e)}), 500
    return config

#TODO
#Multiple Monitors, timeframe, sanitizing variables
@app.route('/api/v1/data')
def getData():
    data = request.get_json()
    if not data or 'monitor' not in data or 'number' not in data:
        logger.error("monitor and number are required")
        return jsonify({"error": "monitor and number are required"}), 400
    monitor = data['monitor']
    number = data['number']

    conn = connectDB()
    logger.debug("data connected db")
    cur = conn.cursor()
    logger.debug("data cursor created")
    query = """
        SELECT * FROM healthcheck_data 
        WHERE monitor_id = %s 
        ORDER BY healthcheck_timestamp DESC 
        LIMIT %s
    """
    data = cur.execute(query, (monitor, number))
    logger.debug("data query executed")
    data = cur.fetchall()
   
    result = []
    logger.debug("printing healthcheck data")
    logger.debug(str(data))
    
    for row in data:
        result.append({
            "id": row[0],
            "timestamp": str(row[1]) if row[1] else None,
            "monitor_id": row[2],
            "response": row[3],
            "response_time": str(row[4]) if row[4] else None  # Convert timedelta to string
        })
        logger.debug(f"Result: {result}")
    return jsonify(result)


#def queryDB(query, params):
#    conn = connectDB()
#    logger.debug("qdb connected db")
#    cur = conn.cursor()
#    logger.debug("qdb cursor created")
#    cur.execute(query(params))
#    logger.debug("qdb query executed")
#    data = cur.fetchall()
#    logger.debug("qdb results fetched")
#    cur.close()
#    return data

def main():
    configLogging()
    app.run(debug=True,host='0.0.0.0', port=5100)


if __name__ == "__main__":
    main()