from engine_control import Robot
from fuzzy_line import FuzzyLineFollowDef

class RobotControl:

    def __init__(self, robot=None):
        self.robot = robot if robot else Robot()
        self.avoid_sim = FuzzyLineFollowDef()

    def control_robot(self, sensor_groups, speed=17):

        self.avoid_sim.input['outer_left'] = sensor_groups['outer_left']
        self.avoid_sim.input['middle_left'] = sensor_groups['middle_left']
        self.avoid_sim.input['middle_right'] = sensor_groups['middle_right']
        self.avoid_sim.input['outer_right'] = sensor_groups['outer_right']

        self.avoid_sim.compute()
        motion = None
        try:
            motion = self.avoid_sim.output['motion']
        except:
            print("Motion was not captured")
            motion = 2

        print(f"Sensor readings: Outer left= {sensor_groups['outer_left']:.1f} cm, "
              f"Middle left= {sensor_groups['middle_left']:.1f} cm, "
              f"Middle right= {sensor_groups['middle_right']:.1f} cm, "
              f"Outer right= {sensor_groups['outer_right']:.1f} cm")

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
                print("Mode: stop")
                self.robot.stop()
            print(f"Motion values: {motion}\n")
        else:
            print("Motion is undefined. Robot remains stationary.")
              
    def cleanup(self):
        self.robot.cleanup()
