#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8 ff=unix ft=python ts=4 sw=4 sts=4 si et :

import sys
import os
import yaml
import json
import time
import datetime
import requests
import paho.mqtt.client as mqtt

os.chdir(os.path.dirname(__file__))

# https://qiita.com/yohm/items/e95950a5d3eba8915e99
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
sys.stdin = os.fdopen(sys.stdin.fileno(), 'r', buffering=1)

import logging
logging.basicConfig(stream=sys.stdout, encoding='utf-8', level=logging.DEBUG, format="%(asctime)s : %(levelname)s : %(message)s")

with open("./config.yaml") as f:
    global config
    config = yaml.safe_load(f)

def on_connect(client, userdata, flag, rc):
    global config
    logging.info(f"on_connect : rc={rc}")
    logging.info("subscribe topic=" + config["mqtt_subscribe_topic"])
    client.subscribe(config["mqtt_subscribe_topic"])

def on_disconnect(client, userdata, rc):
    logging.error(f"on_disconnect : rc={rc}")
    time.sleep(3)
    sys.exit(0)

def on_message(client, userdata, msg):
    global config
    payload_str = msg.payload.decode(encoding='utf-8')

    d = {}
    d["topic"] = config["http2mqtt_topic"]
    d["message"] = config["http2mqtt_message"] + datetime.datetime.now().strftime(" (%H:%M:%S)")
    json_str = json.dumps(d)

    res = requests.post(
            config["http2mqtt_url"],
            headers={'Content-Type': 'application/json'},
            data=json_str
            )
    logging.info("post message to http2mqtt. url="+config["http2mqtt_url"]+", json="+json_str)

mqtt_client = mqtt.Client(client_id=config["mqtt_client_id"], clean_session=True)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message

if config["mqtt_use_auth"] == True:
    mqtt_client.username_pw_set(config["mqtt_username"], config["mqtt_password"])

mqtt_client.connect(config["mqtt_host"], port=config["mqtt_port"], keepalive=60)
mqtt_client.loop_forever()

