#%%
from logging import config as logconfig
import click

# logger config

logconfig.fileConfig('logger.yml')

# load params


# params


# communication with AC


@click.group()
def cli():
    pass


# @cli.command()
# @click.option('--email')
# @click.option('--pwd')
# @click.option('--DeviceID', help='DeviceID')
# @click.option('--OperationMode', default=None, help='OperationMode')
# @click.option('--Power', default=None, help='Power')
# @click.option('--SetFanSpeed', default=None, help='SetFanSpeed')
# @click.option('--SetTemperature', default=None, help='SetTemperature')


# @cli.command()
# @click.option('--email')
# @click.option('--pwd')


if __name__ == '__main__':
    cli()