import asyncio
from robot_control_16 import RobotControl
from engine_control import Robot
from server import read_sensors

async def main():
    robot = Robot()
    robot_control = RobotControl(robot=robot)

    try:
        while True:
            sensor_distances = read_sensors()

            sensor_groups = {
                "left": min(sensor_distances["LF"], sensor_distances["LB"]),
                "right": min(sensor_distances["RF"], sensor_distances["RB"]),
                "front": sensor_distances["F"],
                "back": sensor_distances["B"]
            }

            robot_control.control_robot(sensor_groups, speed=30)

            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("The program was interrupted")
    finally:
        robot.stop()
        robot_control.cleanup()

if __name__ == "__main__":
    asyncio.run(main())