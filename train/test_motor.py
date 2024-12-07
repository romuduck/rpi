import logging

from curio import tcp_server, run, sleep, UniversalQueue, spawn
from bricknil import attach, start
from bricknil.hub import PoweredUpHub
from bricknil.sensor import TrainMotor


q = UniversalQueue()


# @attach(LED, name='train_led')
@attach(TrainMotor, name='motor')
class Train(PoweredUpHub):
    currentSpeed = 0

    # async def run(self):
    #     for i in range(2):  # Repeat this control two times
    #         await self.motor.ramp_speed(80,5000) # Ramp speed to 80 over 5 seconds
    #         await sleep(6)
    #         await self.motor.ramp_speed(0,1000)  # Brake to 0 over 1 second
    #         await sleep(2)

    async def run(self):
        self.message_info("Now up and Running")
        # await self.train_led.set_color(Color.blue)
        while True:
            item = await q.get()
            self.message_info(f"have queue item `{item}`")
            if item is not None:
                # if item == "start":
                #     await self.start_train()
                # if item == "stop":
                #     await self.stop_train()
                # if item == "faster":
                #     await self.faster_train()
                # if item == "slower":
                #     await self.slower_train()
                # if item == "quit":
                #     await self.quit_all()
                await self.motor.ramp_speed(80,5000) # Ramp speed to 80 over 5 seconds
                await sleep(6)
                await self.motor.ramp_speed(0,1000)  # Brake to 0 over 1 second
                await sleep(2)

async def system():
    train = Train('My train')


async def echo_client(client, addr):
    print('Connection from', addr)
    while True:
        data = await client.recv(1000)
        q.put(str(data.decode()))
        if not data:
            break
        await client.sendall(data)
    print('Connection closed')

if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)

    run(tcp_server, '', 25000, echo_client)
    start(system)