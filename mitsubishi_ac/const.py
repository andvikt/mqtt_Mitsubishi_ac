from logging import getLogger, config
from importlib.resources import open_text
from . import res

import yaml

with open_text(res, 'logger.yml') as f:
    config.dictConfig(yaml.load(f, yaml.FullLoader))

logger_ac = getLogger('ac_control')
logger_mqtt = getLogger('MQTT')


with open_text(res, 'params.yml') as f:
    params = yaml.load(f, yaml.FullLoader)

EF_POWER = 1
EF_MODE = 2
EF_TEMP = 4
EF_SPEED = 8


MODES = dict(
    MODE_COOL = 3
    , MODE_HEAT = 1
    , MODE_VENT = 7
    , MODE_AUTO = 8
)


url_login = params['url_login']
url_ac = params['url_ac']
url_ac_status = params['url_ac_status']
HEADERS = {x: str(y) for x, y in params['head'].items()}
DATA_LOGIN = params['data_login']
data_ac = params['data_ac']
TOKEN = 'X-MitsContextKey'
FLAGS = {
    'Power': 1
    , 'OperationMode': 2
    , 'SetTemperature': 4
    , 'SetFanSpeed': 8
}
TOKEN_PATH = 'token.data'
TOKEN_EXPIRES_H = 24 * 7