import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def k3FuzzyAvoidDef():

    MinProximitySignal = 2
    MaxProximitySignal = 200

    left_front = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'left_front')
    right_front = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'right_front')
    front = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'front')
    back = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'back')
    left_back = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'left_back')
    right_back = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'right_back')

    motion = ctrl.Consequent(np.arange(0, 18, 1), 'motion')

    for sensor in [left_front, right_front, front, back, left_back, right_back]:
        sensor['near'] = fuzz.trimf(sensor.universe, [MinProximitySignal, MinProximitySignal, 20])
        sensor['far'] = fuzz.trimf(sensor.universe, [18, MaxProximitySignal, MaxProximitySignal])


    motion['move_forward'] = fuzz.trimf(motion.universe, [0, 0, 1])
    motion['move_turn_left'] = fuzz.trimf(motion.universe, [1, 2, 3])
    motion['move_turn_right'] = fuzz.trimf(motion.universe, [3, 4, 5])
    motion['move_right'] = fuzz.trimf(motion.universe, [5, 6, 7])
    motion['move_left'] = fuzz.trimf(motion.universe, [7, 8, 9])
    motion['move_right_forward'] = fuzz.trimf(motion.universe, [9, 10, 11])
    motion['move_left_forward'] = fuzz.trimf(motion.universe, [11, 12, 13])
    motion['move_right_backward'] = fuzz.trimf(motion.universe, [13, 14, 15])
    motion['move_left_backward'] = fuzz.trimf(motion.universe, [15, 16, 17])

    rules = [
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_right']),

        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_left']),

        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_right_forward']),

        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_forward']),

        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_right_backward']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_left_backward']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_right_backward']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_right_forward']),

        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_left']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_left']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_right']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_turn_left']),

        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_right_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['near'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_right_forward']),

        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['near']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['near'] & left_back['near'] & right_back['far']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['near']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['near'] & left_back['far'] & right_back['far']), consequent=motion['move_left_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['far'] & left_back['near'] & right_back['far']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left_front['far'] & right_front['far'] & left_back['far'] & right_back['far']), consequent=motion['move_forward'])
    ]

    avoid_ctrl = ctrl.ControlSystem(rules)
    avoid_sim = ctrl.ControlSystemSimulation(avoid_ctrl)

    return avoid_sim