#%%
import requests
import yaml
import json
from paho.mqtt import client as mqtt
from copy import copy
from logging import getLogger, config as logconfig

# logger config
logconfig.fileConfig('logger.conf')
logger_ac = getLogger('ac_control')
logger_mqtt = getLogger('MQTT')

# load params
with open('params.yaml', 'r') as f:
    params = yaml.load(f, yaml.FullLoader)

# params
url_login = params['url_login']
url_ac = params['url_ac']
headers = {x: str(y) for x, y in params['head'].items()}
data_login = params['data_login']
data_ac = params['data_ac']
TOKEN = 'X-MitsContextKey'


# MQTT
def on_connect_mqtt(client, userdata, flags, rc):
    logger_mqtt.info(f'Connected to mqtt with result code {rc}')


def on_message_mqtt(client, userdata, msg):
    logger_mqtt.info(f'New data in topic: {msg.topic}, payload: {msg.payload}')
    try:
        data: dict = copy(data_ac)
        data.update(**json.loads(msg.payload))
        request_ac(url_ac, headers, data)
    except Exception as err:
        logger_mqtt.error(str(err))


client = mqtt.Client()
client.on_connect = on_connect_mqtt
client.on_message = on_message_mqtt


def connect_mqtt():
    logger_mqtt.info(f'Connecting mqtt: {params["mqtt"]}')
    client.connect(**params['mqtt'])
    client.subscribe(params['topic'])
    client.loop_forever()


# communication with AC
def request_ac(url, headers, data):
    logger_ac.info(f'Request {url} with data {data}')
    with requests.request(method='post', url=url, headers=headers, json=data) as req:
        ret = req.json()
        logger_ac.info(f'Response: {ret}')
        return req.json()


def __main__():
    # login to AC
    token = request_ac(url_login, headers, data_login)['LoginData']['ContextKey']
    headers.update(**{TOKEN: token})
    # connect mqtt

