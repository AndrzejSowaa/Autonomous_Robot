import time
from engine_control import Robot

def demonstrate_movements():
    robot = Robot() 

    try:
        print("I'm starting to demonstrate all the driving modes of the robot")

        movements = [
            (robot.move_forward, [50, 50, 50, 50]),
            (robot.move_backward, [50, 50, 50, 50]),
            (robot.move_right, [50, 50, 50, 50]),
            (robot.move_left, [50, 50, 50, 50]),
            (robot.move_right_forward, [50, 50]),
            (robot.move_left_forward, [50, 50]),
            (robot.move_right_backward, [50, 50]),
            (robot.move_left_backward, [50, 50]),
            (robot.move_turn_right, [50, 50, 50, 50]),
            (robot.move_turn_left, [50, 50, 50, 50]),
            (robot.move_around_left_front, [50, 50]),
            (robot.move_around_right_front, [50, 50]),
            (robot.move_around_right_back, [50, 50]),
            (robot.move_around_left_back, [50, 50]),
            (robot.move_around_back_left, [50, 50]),
            (robot.move_around_front_left, [50, 50]),
            (robot.move_around_back_right, [50, 50]),
            (robot.move_around_front_right, [50, 50]),
        ]

        for movement, args in movements:
            movement(*args)
            time.sleep(2)
            robot.stop()
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Demonstration interrupted")
    
    finally:
        robot.stop()
        robot.cleanup()

if __name__ == "__main__":
    demonstrate_movements()