from mitsubishi_ac.const import logger_ac, FLAGS, DATA_LOGIN, url_login, HEADERS, TOKEN, data_ac, url_ac, url_ac_status, TOKEN_PATH, TOKEN_EXPIRES_H
import pickle
from datetime import datetime, timedelta
from copy import copy
import attr
import aiohttp
import json
import asyncio
import yaml


@attr.s
class MitsubishiAC:

    devid: str = attr.ib()
    buildingid: str = attr.ib()
    token: str = attr.ib(default=None)
    token_expire_in: datetime = attr.ib(factory=lambda : datetime.now() + timedelta(days=TOKEN_EXPIRES_H))
    email: str = attr.ib(default=None)
    pwd: str = attr.ib(default=None)
    token_path: str = attr.ib(default=TOKEN_PATH)
    ready: asyncio.Event = attr.ib(factory=asyncio.Event, init=False)


    def __attrs_post_init__(self):

        head = copy(HEADERS)
        if self.token:
            head.update(**{TOKEN: self.token})
        self._sess = aiohttp.ClientSession(headers=head, json_serialize=json.dumps)

    async def get_token(self):
        try:
            if self.token:
                return
            token, expire = load_token(self.token_path)
            if token is None:
                login = copy(DATA_LOGIN)
                if self.email is None:
                    raise Exception('Email is not provided')
                login.update(
                    Email=self.email
                    , Password=self.pwd
                )
                data = await self.request_ac(url_login, login)
                if data:
                    data = data.get('LoginData', {})
                else:
                    return
                token = data.get('ContextKey')

            self.token = token
            self.token_expire_in = expire or self.token_expire_in
            self._sess._default_headers.update(**{TOKEN: self.token})

        finally:
            if self.token is None:
                raise RuntimeError(f'Could not load token')
            save_token(self.token_path, self.token, self.token_expire_in)
            self.ready.set()

    async def request_ac(self, url, data, method='post'):
        logger_ac.info(f'Request {url} with data {data} and session: {self._sess}')
        async with self._sess.request(method=method, url=url, json=data) as req:
            txt = await req.text()
            try:
                ret = await req.json()
                logger_ac.info(f'Response: {ret}')
                return ret
            except Exception as ex:
                logger_ac.error(f'{ex}\n{txt}')

    async def get_status(self):
        return await self.request_ac(url_ac_status.format(devid=self.devid, buildingID=self.buildingid), {}, method='get')

    async def close(self):
        await self._sess.close()

    async def send_command(self, **kwargs):
        data: dict = copy(data_ac)
        kwargs.update(EffectiveFlags=calc_flags(kwargs))
        data.update(**kwargs)
        return await self.request_ac(url_ac, data)

    @classmethod
    def from_yaml(cls, path):
        with open(path, 'r') as f:
            return cls(**yaml.load(f, yaml.FullLoader))


def calc_flags(kwargs: dict):
    ret = 0
    for n, x in kwargs.items():
        if x is not None and n in FLAGS:
            ret = ret | FLAGS[n]
    return ret


def save_token(path, token, expires):

    with open(path, 'bw') as f:
        pickle.dump((token, expires), f)


def load_token(path):
    try:
        with open(path, 'br') as f:
            token, date = pickle.load(f)
            date: datetime = date
            if ((datetime.now() - date).total_seconds() / 60 / 60) >= TOKEN_EXPIRES_H:
                return
            else:
                return token, date
    except FileNotFoundError:
        return None, None
    except EOFError:
        return None, None






