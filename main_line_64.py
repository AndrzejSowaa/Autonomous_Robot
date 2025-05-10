import asyncio
from robot_control_line import RobotControl as LineControl
from robot_control_64 import RobotControl as ObstacleControl
from engine_control import Robot
from server import read_sensors, get_color_sensors2

async def main():
    robot = Robot()

    line_control = LineControl(robot=robot)
    obstacle_control = ObstacleControl(robot=robot)

    try:
        current_mode = "line_following"
        
        while True:
            sensor_distances = read_sensors()
            line_sensors = get_color_sensors2()

            off_line = (
                line_sensors["ol"] == 0 and
                line_sensors["ml"] == 0 and
                line_sensors["mr"] == 0 and
                line_sensors["or"] == 0
            )

            front_obstacle = min(sensor_distances["F"], sensor_distances["LF"], sensor_distances["RF"])


            if current_mode == "line_following":
                if off_line:
                    current_mode = "obstacle_avoidance"
                elif front_obstacle < 15:
                    current_mode = "obstacle_avoidance"
                else:
                    sensor_line = {
                        "outer_left": line_sensors["ol"],
                        "middle_left": line_sensors["ml"],
                        "middle_right": line_sensors["mr"],
                        "outer_right": line_sensors["or"]
                    }
                    line_control.control_robot(sensor_line, speed=17)

            elif current_mode == "obstacle_avoidance":
                if not off_line and front_obstacle >= 15:
                    current_mode = "line_following"
                else:
                    obstacle_sensors = {
                        "left_back": sensor_distances["LB"],
                        "right_back": sensor_distances["RB"],
                        "left_front": sensor_distances["LF"],
                        "right_front": sensor_distances["RF"],
                        "front": sensor_distances["F"],
                        "back": sensor_distances["B"]
                    }
                    obstacle_control.control_robot(obstacle_sensors, speed=30)

            await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("The program was interrupted")
    finally:
        robot.stop()
        robot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())