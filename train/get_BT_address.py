# from curio import sleep
from bricknil import attach, start
from bricknil.hub import PoweredUpHub
import logging

class Train(PoweredUpHub):

    async def run(self):
        None

async def system():
    train = Train('My train')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start(system)