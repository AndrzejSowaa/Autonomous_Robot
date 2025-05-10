from engine_control import Robot
from fuzzy_avoid_16 import k3FuzzyAvoidDef

class RobotControl:

    def __init__(self, robot=None):
        self.robot = robot if robot else Robot()
        self.avoid_sim = k3FuzzyAvoidDef()

    def control_robot(self, sensor_groups, speed=30):

        self.avoid_sim.input['left'] = sensor_groups['left']
        self.avoid_sim.input['right'] = sensor_groups['right']
        self.avoid_sim.input['front'] = sensor_groups['front']
        self.avoid_sim.input['back'] = sensor_groups['back']

        self.avoid_sim.compute()
        motion = None
        try:
            motion = self.avoid_sim.output['motion']
        except:
            print("Motion was not captured")
            motion = 2

        print(f"Sensor readings: Left= {sensor_groups['left']:.1f} cm, "
              f"Right= {sensor_groups['right']:.1f} cm, "
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
            print(f"Motion values: {motion}\n")
        else:
            print("Motion is undefined. Robot remains stationary.")

    def cleanup(self):
        self.robot.cleanup()