import asyncio
from robot_control_line import RobotControl
from engine_control import Robot
from server import get_color_sensors2

async def main():
    robot = Robot()
    robot_control = RobotControl(robot=robot)

    try:
        while True:
            sensor_line = get_color_sensors2()

            sensor_groups = {
                "outer_left": sensor_line['ol'],
                "middle_left": sensor_line['ml'],
                "middle_right": sensor_line['mr'],
                "outer_right": sensor_line['or']
            }

            robot_control.control_robot(sensor_groups, speed=17)

            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("The program has been interrupted")
    finally:
        robot.stop()
        robot_control.cleanup()

if __name__ == "__main__":
    asyncio.run(main())