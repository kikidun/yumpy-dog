import psycopg2
import requests
import time
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv

import logging.config

logger = logging.getLogger("worker")

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
            "level": "INFO",
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
                logger.info("connected to DB")
                return _conn
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.info(f"Connection failed, retrying... ({attempt + 1}/{max_retries})")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Connection failed!")
                    logger.error(f"Error: {e}")
                    exit()
    return _conn

def getConfig():
    conn = connectDB()
    cur = conn.cursor()
    query = "SELECT * FROM config"
    cur.execute(query)
    config = cur.fetchall()
    cur.close()
    return config

#need to make this a fine chill thing to do and not exit worthy
config = getConfig()

#print out the config, gotta set these better somehow
logger.debug("printing configuration:")
for key in config:
    logger.debug(key[0] + ": " + key[1])

#Retrieves the entire monitor table to get urls from. 
def getMonitors():
    conn = connectDB()
    cur = conn.cursor()
    query = "SELECT * FROM monitors"
    cur.execute(query)
    monitors = cur.fetchall()
    cur.close()
    return monitors

#query the monitor table for entries where last checked + interval is less than now
def getMonitorsForChecking():
    conn = connectDB()
    conn.commit()
    cur = conn.cursor()
    cur.execute("SELECT * FROM monitors WHERE last_checked IS NULL OR (last_checked + (interval * INTERVAL '1 second') < CURRENT_TIMESTAMP)")
    monitorsForChecking = cur.fetchall()
    logger.debug("monitors for checking: "+ str(monitorsForChecking))
    cur.close()
    return monitorsForChecking

#HTTP get of a given URL, return response and timestamp
def checkURL(URL):
    logger.debug("Sending request to "+URL)
    send_timestamp = datetime.now()
    try:
        resp = requests.get(URL, verify=False)
    except Exception as e:
        logger.error("Error checking URL")
        logger.error(f"Error: {e}")
    return resp, send_timestamp   

#put the result of the health check in the db, update last checked
def update_DB(monitor, health_check_result, send_time):
    conn = connectDB()
    cur = conn.cursor()
    logger.info("Loading the database with a "+ str(health_check_result) +" for "+ monitor[1])
    try:
        cur.execute("INSERT INTO healthcheck_data ( healthcheck_timestamp, monitor_id, response, response_time) VALUES (%s, %s, %s, %s)",
        (send_time, monitor[0], health_check_result.status_code, health_check_result.elapsed))
        cur.execute("UPDATE monitors SET last_checked =%s WHERE monitor_id = %s",(send_time, monitor[0]))
        conn.commit()
    except Exception as e:
        conn.rollback()  # Undo all changes in this transaction
        logger.error("Commit failed!")
        logger.error(f"Error: {e}")
    cur.close()
    return True


def working_logic():
    configLogging()
    conn = connectDB()
    while True:
        conn.commit()
        enabled = getConfig()[0][1]
        logger.debug(str(datetime.now())+" LOG: enabled is set to " + enabled)
        if enabled.strip() == "True":
            monitors = getMonitorsForChecking()
            logger.debug(monitors)
            if len(monitors) == 0:
                time.sleep(1)
            else:
                for monitor in monitors:
                    health_check_result, send_time = checkURL(monitor[2])
                    logger.debug("health check code was:" + str(health_check_result.status_code))
                    update_DB(monitor, health_check_result, send_time) 
                time.sleep(1)
        else:
            time.sleep(10)


working_logic()

_conn.close()
