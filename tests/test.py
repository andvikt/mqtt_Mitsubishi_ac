from logging import basicConfig, DEBUG
basicConfig(level=DEBUG)
from mitsubishi_ac.api import load_token, save_token, MitsubishiAC
from mitsubishi_ac.app import make_app
from pytest import fixture
import  pytest
import asyncio
import yaml


@fixture()
async def ac():
    ret = MitsubishiAC.from_yaml('params.yaml')
    await ret.get_token()
    assert len(ret.token) == 30
    yield ret
    await ret.close()


@pytest.mark.asyncio
async def test_new_mac_class(ac):
    stat = await ac.get_status()
    assert 'RoomTemperature' in stat


@fixture()
async def app(ac):
    ret = await make_app(
        ac, 'in', 'out', 'localhost', 1883, 60
    )
    yield ret
    await ret.stop()


@pytest.mark.asyncio
async def test_app(app):
    await asyncio.sleep(70)