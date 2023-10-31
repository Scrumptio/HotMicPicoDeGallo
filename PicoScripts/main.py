import asyncio
# from enum import Enum
from machine import Pin
from sys import stdin, stdout
import time

__version__ = "0.9"
EOL_MARKER = "\n"

#Makeshift Enum for controlling spelling errors
LED_COLORS  = {"GREEN", "ONBOARD"}
GREEN   = "GREEN"
ONBOARD = "ONBOARD"
LED_COMMANDS= {"HOT","MUTE","BLINK","HELLO","GOODBYE"}
HOT     = "HOT"
MUTE    = "MUTE"
BLINK   = "BLINK"
HELLO   = "HELLO"
GOODBYE = "GOODBYE"

__version__ = "0.9"

#Boolean to determine what state the device is in
active = False


# To consume count for use with COMMAND dict() for faster processing
def mode_hot(led, count = None):
    led.value(1)


# To consume count for use with COMMAND dict() for faster processing
def mode_mute(led, count = None):
    led.value(0)


# LED blinks on and off for 'count'
async def blink(led, count):
    i = 0
    while i < int(count):
        led.toggle()
        await asyncio.sleep(0.4)
        led.toggle()
        await asyncio.sleep(0.8)
        i+= 1
    return 1

ONBOARD_LED = Pin(25, Pin.OUT)
GREEN_LED   = Pin(15, Pin.OUT)
LEDS = dict({
    ONBOARD  : ONBOARD_LED,
    GREEN: GREEN_LED
    })

    
# Blinks LEDs twice and changes device state to On
async def start(consumed_led_color = None, consumed_count = None):
    task = asyncio.create_task(group_blink(LEDS, 2))
    await task
    global active
    active = True
    return 1

    
# Blinks LEDs twice and changes device state to Off
async def stop(consumed_led_color = None, consumed_count = None):
    for led in LEDS:
        mode_mute(led)
    global active
    active = False
    globals()['active']  = False
    await asyncio.run(group_blink(LEDS, 2))
    return 1


# Used to blink() multiple LEDs at the some time
async def group_blink(leds: dict, count):
    tasks = list()
    for pin in leds.values():
        tasks.append(
            asyncio.create_task(
                blink(pin, int(count))
                )
            )
    await asyncio.gather(*tasks)
    
    return 1


# Used to blink() a single led
def single_blink(led, count):
    asyncio.run(blink(led, int(count)))
    return 1
    
        
def get_flash_command(led_color, count: int) -> str:
    return "_".join([led_color, BLINK, str(count)]) + EOL_MARKER

def get_hot_command(led_color) -> str:
     return "_".join([led_color, HOT]) + EOL_MARKER

def get_mute_command(led_color) -> str:
    return "_".join([led_color, MUTE]) + EOL_MARKER

def get_start_command():
    return HELLO + EOL_MARKER

def get_end_command():
    return GOODBYE + EOL_MARKER


COMMANDS = {
    HOT:   mode_hot,    
    MUTE:  mode_mute,
    BLINK: single_blink,
    HELLO: start,
    GOODBYE: stop
    }


async def main():
    global active
    active = True
    try:
        while True:
            print(active)
            """
            while not active:
                await blink(ONBOARD_LED,1)
                incoming = stdin.readline().rstrip()
                if incoming == HELLO:
                    try:
                        await start()
                        stdout.write((__version__+EOL_MARKER).encode())
                        break
                    except Exception as e:
                        print("ERROR")
                        raise RuntimeError("Error on Startup")
                    time.sleep(2)
            """

            while active:
                incoming = stdin.readline().strip()
                # 0.9 Format COLOR_MODE_COUNT(optional)\n
                inputs = incoming.split("_")
                if len(inputs) == 3:
                    COMMANDS.get(inputs[1])(LEDS.get(inputs[0]), inputs[2])
                elif len(inputs) == 2:
                    COMMANDS.get(inputs[1])(LEDS.get(inputs[0]))
                time.sleep(0.2)
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())
    

        
