#%%
import requests
import yaml
from copy import copy
from logging import getLogger, config as logconfig
import click

# logger config
#logconfig.fileConfig('logger.conf')
logger_ac = getLogger('ac_control')
logger_mqtt = getLogger('MQTT')

# load params
print(__file__)
with open(f'/daikin_ac/params.yaml', 'r') as f:
    params = yaml.load(f, yaml.FullLoader)

# params
url_login = params['url_login']
url_ac = params['url_ac']
url_ac_status = params['url_ac_status']
headers = {x: str(y) for x, y in params['head'].items()}
data_login = params['data_login']
data_ac = params['data_ac']
TOKEN = 'X-MitsContextKey'


# communication with AC
def request_ac(url, headers, data):
    logger_ac.info(f'Request {url} with data {data}')
    with requests.request(method='post', url=url, headers=headers, json=data) as req:
        ret = req.json()
        logger_ac.info(f'Response: {ret}')
        return req.json()


@click.group()
def cli():
    pass


FLAGS = {
    'Power': 1
    , 'OperationMode': 2
    , 'SetTemperature': 4
    , 'SetFanSpeed': 8
}


def calc_flags(kwargs: dict):
    ret = 0
    for n, x in kwargs.items():
        if x is not None and n in FLAGS:
            ret = ret | FLAGS[n]
    return ret


@cli.command()
@click.option('--email')
@click.option('--pwd')
@click.option('--DeviceID', help='DeviceID')
@click.option('--OperationMode', default=None, help='OperationMode')
@click.option('--Power', default=None, help='Power')
@click.option('--SetFanSpeed', default=None, help='SetFanSpeed')
@click.option('--SetTemperature', default=None, help='SetTemperature')
def send_command(email, pwd, *args, **kwargs):
    # login to AC
    login = copy(data_login)
    login.update(
        Email='email'
        , Password='pwd'
    )
    token = request_ac(url_login, headers, login).get('LoginData', {}).get('ContextKey')
    if token:
        headers.update(**{TOKEN: token})
        # send msg
        data: dict = copy(data_ac)
        kwargs.update(EffectiveFlags=calc_flags(kwargs))
        data.update(**kwargs)
        print(request_ac(url_ac, headers, kwargs))
    else:
        raise RuntimeError('Did not get token')


@cli.command()
@click.option('--email')
@click.option('--pwd')
def get_status(email, pwd, **kwargs):
    # login to AC
    login = copy(data_login)
    login.update(
        Email='email'
        , Password='pwd'
    )
    token = request_ac(url_login, headers, login).get('LoginData', {}).get('ContextKey')
    if token:
        headers.update(**{TOKEN: token})
        print(request_ac(url_ac_status, headers, {}))
    else:
        raise RuntimeError('Did not get token')
