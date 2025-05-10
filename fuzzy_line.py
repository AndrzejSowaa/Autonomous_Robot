import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
 
def FuzzyLineFollowDef():
    
    minLineSignal = 0
    maxLineSignal = 1

    outer_left = ctrl.Antecedent(np.arange(minLineSignal, maxLineSignal + 1, 1), 'outer_left')
    middle_left = ctrl.Antecedent(np.arange(minLineSignal, maxLineSignal + 1, 1), 'middle_left')
    middle_right = ctrl.Antecedent(np.arange(minLineSignal, maxLineSignal + 1, 1), 'middle_right')
    outer_right = ctrl.Antecedent(np.arange(minLineSignal, maxLineSignal + 1, 1), 'outer_right')
 
    motion = ctrl.Consequent(np.arange(0, 8, 1), 'motion')

    for sensor in [outer_left, middle_left, middle_right, outer_right]:
        sensor['on-line'] = fuzz.trimf(sensor.universe, [1, 1, 1]) 
        sensor['off-line'] = fuzz.trimf(sensor.universe, [0, 0, 0])
 
 
    motion['move_forward'] = fuzz.trimf(motion.universe, [0, 0, 1])
    motion['move_turn_left'] = fuzz.trimf(motion.universe, [1, 2, 3])
    motion['move_turn_right'] = fuzz.trimf(motion.universe, [3, 4, 5])
    motion['stop'] = fuzz.trimf(motion.universe, [5, 6, 7])
 

    rules = [
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['on-line'] & middle_right['on-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['on-line'] & middle_right['on-line'] & outer_right['off-line']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['on-line'] & middle_right['off-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['on-line'] & middle_right['off-line'] & outer_right['off-line']), consequent=motion['move_turn_left']),
     
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['off-line'] & middle_right['on-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['off-line'] & middle_right['on-line'] & outer_right['off-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['off-line'] & middle_right['off-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['on-line'] & middle_left['off-line'] & middle_right['off-line'] & outer_right['off-line']), consequent=motion['move_turn_left']),
        
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['on-line'] & middle_right['on-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['on-line'] & middle_right['on-line'] & outer_right['off-line']), consequent=motion['move_forward']),
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['on-line'] & middle_right['off-line'] & outer_right['on-line']), consequent=motion['move_turn_left']),
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['on-line'] & middle_right['off-line'] & outer_right['off-line']), consequent=motion['move_turn_left']),
        
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['off-line'] & middle_right['on-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['off-line'] & middle_right['on-line'] & outer_right['off-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['off-line'] & middle_right['off-line'] & outer_right['on-line']), consequent=motion['move_turn_right']),
        ctrl.Rule(antecedent=(outer_left['off-line'] & middle_left['off-line'] & middle_right['off-line'] & outer_right['off-line']), consequent=motion['stop']),
    ]
 
    avoid_ctrl = ctrl.ControlSystem(rules)
    avoid_sim = ctrl.ControlSystemSimulation(avoid_ctrl)
 
    return avoid_sim