import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

def k3FuzzyAvoidDef():
    MinProximitySignal = 2 
    MaxProximitySignal = 200

    left = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'left')
    right = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'right')
    front = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'front')
    back = ctrl.Antecedent(np.arange(MinProximitySignal, MaxProximitySignal + 1, 1), 'back')

    motion = ctrl.Consequent(np.arange(0, 6, 1), 'motion')

    for sensor in [left, right, front, back]:
        sensor['near'] = fuzz.trimf(sensor.universe, [MinProximitySignal, MinProximitySignal, 20]) 
        sensor['far'] = fuzz.trimf(sensor.universe, [18, MaxProximitySignal, MaxProximitySignal])  

    motion['move_forward'] = fuzz.trimf(motion.universe, [0, 0, 1])
    motion['move_turn_left'] = fuzz.trimf(motion.universe, [1, 2, 3])
    motion['move_turn_right'] = fuzz.trimf(motion.universe, [3, 4, 5])

    rules = [
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left['far'] & right['far']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left['far'] & right['far']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left['near'] & right['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left['far'] & right['near']), consequent=motion['move_turn_left']),
     
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left['far'] & right['far']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left['near'] & right['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left['near'] & right['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left['far'] & right['near']), consequent=motion['move_turn_left']),
        
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left['near'] & right['near']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left['near'] & right['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left['near'] & right['far']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(front['far'] & back['far'] & left['far'] & right['far']), consequent=motion['move_forward']),
        
        ctrl.Rule(antecedent=(front['far'] & back['near'] & left['near'] & right['near']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(front['near'] & back['far'] & left['far'] & right['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left['far'] & right['near']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(front['near'] & back['near'] & left['near'] & right['near']), consequent=motion['move_turn_left'])
    ]

    avoid_ctrl = ctrl.ControlSystem(rules)
    avoid_sim = ctrl.ControlSystemSimulation(avoid_ctrl)

    return avoid_sim