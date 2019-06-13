from .api import MitsubishiAC
from .const import logger_mqtt
from hbmqtt.session import ApplicationMessage
from hbmqtt.client import MQTTClient
import json
import asyncio
import attr


@attr.s
class App:

    ac: MitsubishiAC= attr.ib()
    handle_loop: asyncio.Future = attr.ib()
    poll_loop: asyncio.Future = attr.ib()
    clnt: MQTTClient = attr.ib()

    async def stop(self):
        self.handle_loop.cancel()
        self.poll_loop.cancel()
        await self.clnt.disconnect()
        await self.ac.close()


async def make_app(ac: MitsubishiAC
             , topic_in: str
             , topic_out: str
             , host: str
             , port: int
             , poll_interval: int
             ):

    clnt = MQTTClient()

    async def handle_in():
        try:
            while True:
                msg: ApplicationMessage = await clnt.deliver_message()
                logger_mqtt.debug(f'Recieved msg {msg.topic} {msg.data}')
                try:
                    data = json.loads(msg.data.decode())
                except Exception as err:
                    logger_mqtt.error(f'{msg.data} is not json: {err}')
                    continue
                await ac.send_command(**data)
        except asyncio.CancelledError:
            pass

    async def poll():
        try:
            while True:
                try:
                    data = await ac.get_status()
                    await clnt.publish(topic_out, json.dumps(data).encode())
                except Exception as exc:
                    logger_mqtt.error(f'{exc}')
                    continue
                finally:
                    await asyncio.sleep(poll_interval)
        except asyncio.CancelledError:
            pass

    await clnt.connect(f'mqtt://{host}:{port}')
    await clnt.subscribe([(topic_in, 0)])

    return App(
        ac, handle_loop=asyncio.ensure_future(handle_in()), poll_loop=asyncio.ensure_future(poll()), clnt=clnt
    )
