from engine_control import Robot
from fuzzy_avoid_64 import k3FuzzyAvoidDef

class RobotControl:
    def __init__(self, robot=None):
        self.robot = robot if robot else Robot()
        self.avoid_sim = k3FuzzyAvoidDef()

    def control_robot(self, sensor_groups, speed=30):
        self.avoid_sim.input['left_front'] = sensor_groups['left_front']
        self.avoid_sim.input['right_front'] = sensor_groups['right_front']
        self.avoid_sim.input['left_back'] = sensor_groups['left_back']
        self.avoid_sim.input['right_back'] = sensor_groups['right_back']
        self.avoid_sim.input['front'] = sensor_groups['front']
        self.avoid_sim.input['back'] = sensor_groups['back']

        self.avoid_sim.compute()
        motion = None
        try:
            motion = self.avoid_sim.output['motion']
        except:
            print("Motion was not captured")
            motion = 2

        print(f"Sensor readings: Left_front= {sensor_groups['left_front']:.1f} cm, "
              f"Right_front= {sensor_groups['right_front']:.1f} cm, "
              f"Left_back= {sensor_groups['left_back']:.1f} cm, "
              f"Right_back= {sensor_groups['right_back']:.1f} cm, "
              f"Front= {sensor_groups['front']:.1f} cm, "
              f"Back= {sensor_groups['back']:.1f} cm")

        if motion is not None:
            if 0 <= motion < 1:
                print("Mode: move_forward")
                self.robot.move_forward(speed, speed, speed, speed)
            elif 1 <= motion < 3:
                print("Mode: move_turn_left")
                self.robot.move_turn_left(speed, speed, speed, speed)
            elif 3 <= motion < 5:
                print("Mode: move_turn_right")
                self.robot.move_turn_right(speed, speed, speed, speed)
            elif 5 <= motion < 7:
                print("Mode: move_right")
                self.robot.move_right(speed, speed, speed, speed)
            elif 7 <= motion < 9:
                print("Mode: move_left")
                self.robot.move_left(speed, speed, speed, speed)  
            elif 9 <= motion < 11:
                print("Mode: move_right_forward")
                self.robot.move_right_forward(speed, speed)
            elif 11 <= motion < 13:
                print("Mode: move_left_forward")
                self.robot.move_left_forward(speed, speed)  
            elif 13 <= motion < 15:
                print("Mode: move_right_backward")
                self.robot.move_right_backward(speed, speed) 
            elif 15 <= motion < 17:
                print("Mode: move_left_backward")
                self.robot.move_left_backward(speed, speed)
            print(f"Motion values: {motion}\n")
        else:
            print("Motion is undefined. Robot remains stationary.")

    def cleanup(self):
        self.robot.cleanup()