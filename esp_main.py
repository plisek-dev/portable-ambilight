import sys
import uselect
from machine import Pin
import machine
import neopixel
import time
import random
import json
import uasyncio as asyncio
import uselect
import os

# Configure the Neopixel
NUM_PIXELS = 72
# Total number of LEDs
PIN = 5  # GPIO for neopixel data

np = neopixel.NeoPixel(Pin(PIN), NUM_PIXELS)
serialPoll = uselect.poll()
serialPoll.register(sys.stdin, uselect.POLLIN)
LED = Pin(4, Pin.OUT)

def convert_to_list(color_string):
    """Converts received string of colors to list"""
    return json.loads(color_string)

def handle_command(command):

    if command == None: # filter out empty messages
        return 0
    sys.stdout.buffer.write(command)

def led_strip():

    try:
        while True:
            color_wipe((255, 0, 0))  # Red wipe
            time.sleep(1)

            color_wipe((0, 255, 0))  # Green wipe
            time.sleep(1)

            color_wipe((0, 0, 255))  # Blue wipe
            time.sleep(1)

            rainbow_cycle()  # Rainbow cycle
            time.sleep(1)

    except KeyboardInterrupt:
        # Turn off LEDs on exit
        np.fill((0, 0, 0))
        np.write()


def color_wipe(color, wait_ms=50):
    for i in range(NUM_PIXELS):
        np[i] = color
        np.write()
        time.sleep_ms(wait_ms)

def rainbow_cycle(wait_ms=20, iterations=5):
    num_colors = 256
    for j in range(iterations):
        for i in range(num_colors):
            r, g, b = wheel((i * 256 // num_colors) % 256)
            for pixel in range(NUM_PIXELS):
                np[pixel] = (r, g, b)
            np.write()
            time.sleep_ms(wait_ms)

def wheel(pos):
    # Generate rainbow colors across 0-255 positions
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


def rand_color():

    rand_LED = random.randint(0, 71)
    col1 = random.randint(0, 255)
    col2 = random.randint(0, 255)
    col3 = random.randint(0, 255)
    ambience(rand_LED, (col1, col2, col3))

def ambience(led_number, color):
    np[led_number] = color
    np.write()

def create_ambience(message):

    for color in message:
        np[color[0]] = color[1]
    np.write()


def readSerial():

    if serialPoll.poll(0):
        message = ""
        while not message.strip():
            message = sys.stdin.readline()
        return message
    else:
        return None

def custom_eval(input_str):
    stack = []
    current_list = None

    for char in input_str:
        if char == "[":
            new_list = []
            if current_list is not None:
                stack.append(current_list)
            current_list = new_list
        elif char == "]":
            if stack:
                previous_list = stack.pop()
                previous_list.append(current_list)
                current_list = previous_list
        elif char.isdigit():
            num_str = char
            while input_str[input_str.index(char) + 1].isdigit():
                char = input_str[input_str.index(char) + 1]
                num_str += char
            current_list.append(int(num_str))

    return current_list

def readSerial_continously():
    # ESP32_baudrate = 115400
    # ESP32_baudrate = 230400
    # ESP32_baudrate = 460800
    ESP32_baudrate = 921600

    machine.UART(0, baudrate=ESP32_baudrate)

    while True:
        # continuously read commands over serial and handle them
        try:
            message = readSerial()
            # message2 = readSerial()
            if message is not None:
                print(message)
                message = message.strip('\n')
                color = convert_to_list(message)
                create_ambience(color)
            # if message2 is not None:
            #     message2 = message2.strip('\n')
            #     color2 = convert_to_list(message2)
            #     create_ambience(color2)
        except Exception as err:
            print(err)
            pass


async def read_input(input_queue):
    while True:
        await asyncio.sleep_ms(100)  # Non-blocking sleep
        if sys.stdin in uselect.select([sys.stdin], [], [], 0)[0]:
            input_data = sys.stdin.readline()
            input_queue.put_nowait(input_data)


async def process_input(input_queue):
    while True:
        try:
            input_data = await input_queue.get()
            # Process the input data
            print("Processing:", input_data.strip())
        except IndexError:
            pass  # No data in the queue, continue processing or do other tasks


async def main():
    # ESP32_baudrate = 115400
    # ESP32_baudrate = 230400
    # ESP32_baudrate = 460800
    ESP32_baudrate = 921600

    machine.UART(0, baudrate=ESP32_baudrate)

    
    input_queue = asyncio.Queue()

    # Start reading input in the background
    asyncio.create_task(read_input(input_queue))

    # Start processing input in the foreground
    await process_input(input_queue)


# def main():
#     readSerial_continously()
