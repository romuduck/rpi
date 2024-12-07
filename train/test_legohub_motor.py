import logging

from curio import sleep, UniversalQueue, spawn, run, tcp_server, TaskGroup
from bricknil import attach, start
from bricknil.hub import PoweredUpHub
from bricknil.sensor import TrainMotor

logger = logging.getLogger(__name__)

MAX_SPEED = 100


q = UniversalQueue()
# q.put(str(msg.payload.decode()))

async def publish(msg):
    await q.put(msg)

async def echo_client(client, addr):
    logger.info(f"Connection from {addr}")
    while True:
        data = await client.recv(1000)
        data_decoded = data.decode("utf-8")[:-1]
        logger.info(f"Received data: {data_decoded}")
        if not data:
            break
        await publish(data_decoded)
        await client.sendall(bytes(f"Server received: {data_decoded}\n", "utf-8"))
    logger.info('Connection closed')



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


    async def set_speed(self, speed):
        self.message_info('Set speed')
        if abs(speed) >= 0 and abs(speed) <= MAX_SPEED
            self.currentSpeed = speed
            await self.motor.ramp_speed(self.currentSpeed, 1000)

    async def start_train(self):
        self.message_info('Starting')
        self.currentSpeed = 20
        # await self.train_led.set_color(Color.green)
        await self.motor.ramp_speed(self.currentSpeed, 1000)

    async def stop_train(self):
        self.message_info('Coming to a stop')
        await self.motor.ramp_speed(0, 2000)
        # await self.train_led.set_color(Color.blue)
        self.currentSpeed = 0
        await sleep(1)

    async def faster_train(self):
        self.message_info('Increasing speed')
        if self.currentSpeed < MAX_SPEED:
            self.currentSpeed += 10
        await self.motor.ramp_speed(self.currentSpeed, 1000)

    async def slower_train(self):
        self.message_info('Decreasing speed')
        if self.currentSpeed > -MAX_SPEED:
            self.currentSpeed -= 10
        await self.motor.ramp_speed(self.currentSpeed, 1000)

    async def run(self):
        self.message_info("Now up and Running")
        # await self.train_led.set_color(Color.blue)

        # start a tcp server with a client that will publish message in a queue
        await spawn(tcp_server, '', 25001, echo_client)

        while True:
            # wait for a new message in quueue
            item = await q.get()
            self.message_info(f"have queue item `{item}`")
            if item is not None:
                if item == "start":
                    await self.start_train()
                if item == "stop":
                    await self.stop_train()
                if item == "faster":
                    await self.faster_train()
                if item == "slower":
                    await self.slower_train()



async def system():
    train = Train('My train')


if __name__ == '__main__':
    formatter = "[%(asctime)s] %(name)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)

    start(system)


