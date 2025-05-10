import RPi.GPIO as GPIO
import asyncio
import json

color_sensor = [
    {"line": 15, "name": "ol"},
    {"line": 14, "name": "ml"},
    {"line": 23, "name": "mr"},
    {"line": 18, "name": "or"}
]

sensor_line = {sensor['name']: 0 for sensor in color_sensor}


def setup():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for sensor in color_sensor:
        GPIO.setup(sensor["line"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


async def read_sensors():
    for sensor in color_sensor:
        sensor_line[sensor['name']] = GPIO.input(sensor["line"])
    with open("sensor_color.json", "w") as file:
        json.dump(sensor_line, file, indent=2)
    await asyncio.sleep(0.1)