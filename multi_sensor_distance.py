import json
import RPi.GPIO as GPIO
import asyncio
import os
import time

sensors = [
    {"trigger": 7, "echo": 22, "name": "F"},
    {"trigger": 8, "echo": 27, "name": "RF"}, 
    {"trigger": 12, "echo": 17, "name": "RB"},
    {"trigger": 16, "echo": 4, "name": "B"},  
    {"trigger": 21, "echo": 3, "name": "LB"}, 
    {"trigger": 20, "echo": 2, "name": "LF"}  
]

OBSTACLE_THRESHOLD = 20
DEFAULT_DISTANCE = 200

MIN_DISTANCE = 2
MAX_DISTANCE = 200

sensor_distances = {sensor['name']: DEFAULT_DISTANCE for sensor in sensors}

def setup_sensors():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for sensor in sensors:
        GPIO.setup(sensor["trigger"], GPIO.OUT)
        GPIO.setup(sensor["echo"], GPIO.IN)
        GPIO.output(sensor["trigger"], False)

def run_sensor_monitor():
    setup_sensors()
    asyncio.run(monitor_sensors())

def get_sensor_data():
    return dict(sensor_distances)

async def measure_distance(sensor, timeout=0.3):
    trigger = sensor["trigger"]
    echo = sensor["echo"]

    GPIO.output(trigger, True)
    await asyncio.sleep(0.0001)
    GPIO.output(trigger, False)

    start_time = time.time()
    stop_time = start_time

    start_wait = time.time()
    while GPIO.input(echo) == 0:
        start_time = time.time()
        if start_time - start_wait > timeout:
            print(f"Timeout on sensor {sensor['name']} while waiting for signal to start")
            return None

    stop_wait = time.time()
    while GPIO.input(echo) == 1:
        stop_time = time.time()
        if stop_time - stop_wait > timeout:
            print(f"Timeout on sensor {sensor['name']} while waiting for signal to end")
            return None

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2

    return round(distance, 1)

async def monitor_sensor(sensor):
    while True:
        distance = await measure_distance(sensor)
        if distance is not None and distance < MAX_DISTANCE and distance >= MIN_DISTANCE:
            sensor_distances[sensor['name']] = round(distance, 1)
        elif distance is not None and distance < MIN_DISTANCE:
            sensor_distances[sensor['name']] = MIN_DISTANCE
        else:
            sensor_distances[sensor['name']] = MAX_DISTANCE 
        try:
            with open('sensors.json.tmp', 'w') as f:
                json.dump(sensor_distances, f)
            os.replace('sensors.json.tmp', 'sensors.json')
        except Exception as e:
            print(f"Error while writing to sensors.json: {e}")
        await asyncio.sleep(0.1)

async def monitor_sensors():
    tasks = [asyncio.create_task(monitor_sensor(sensor)) for sensor in sensors]
    await asyncio.gather(*tasks)