from server import update_control_data
import RPi.GPIO as GPIO

PWM_FREQUENCY = 2000

#LF9/10, LB11/5, RF6/13, RB19/26
MOTOR_PINS = {
    "RB2": {"forward_pin": 11, "backward_pin": 5},
    "RF2": {"forward_pin": 9, "backward_pin": 10},
    "LB2": {"forward_pin": 19, "backward_pin": 26},
    "LF2": {"forward_pin": 6, "backward_pin": 13},
}

class Motor:
    def __init__(self, forward_pin, backward_pin):
        self.forward_pin = forward_pin
        self.backward_pin = backward_pin

        GPIO.setup(self.forward_pin, GPIO.OUT)
        GPIO.setup(self.backward_pin, GPIO.OUT)

        self.pwm_forward = GPIO.PWM(self.forward_pin, PWM_FREQUENCY)
        self.pwm_backward = GPIO.PWM(self.backward_pin, PWM_FREQUENCY)

        self.pwm_forward.start(0)
        self.pwm_backward.start(0)

    def move_forward(self, speed):
        self.pwm_backward.ChangeDutyCycle(0)
        self.pwm_forward.ChangeDutyCycle(speed)

    def move_backward(self, speed):
        self.pwm_forward.ChangeDutyCycle(0)
        self.pwm_backward.ChangeDutyCycle(speed)

    def stop(self):
        self.pwm_forward.ChangeDutyCycle(0)
        self.pwm_backward.ChangeDutyCycle(0)

    def cleanup(self):
        self.pwm_forward.stop()
        self.pwm_backward.stop()


class Robot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'motors'):
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self.motors = {
                "RB2": Motor(**MOTOR_PINS["RB2"]),
                "RF2": Motor(**MOTOR_PINS["RF2"]),
                "LB2": Motor(**MOTOR_PINS["LB2"]),
                "LF2": Motor(**MOTOR_PINS["LF2"]),
            }

    
    def controls(self, action, speed=50):
        try:
            update_control_data(action=action, speed=speed)
        except Exception as e:
            print(f"Error while updating control: {e}")

    def move_forward(self, rb_speed, rf_speed, lb_speed, lf_speed):
        self.motors["RB2"].move_forward(rb_speed)
        self.motors["RF2"].move_forward(rf_speed)
        self.motors["LB2"].move_forward(lb_speed)
        self.motors["LF2"].move_forward(lf_speed)
        self.controls("move-forward", speed=rb_speed)

    def move_backward(self, rb_speed, rf_speed, lb_speed, lf_speed):
        self.motors["RB2"].move_backward(rb_speed)
        self.motors["RF2"].move_backward(rf_speed)
        self.motors["LB2"].move_backward(lb_speed)
        self.motors["LF2"].move_backward(lf_speed)
        self.controls("move-backward", speed=rb_speed)

    def move_right(self, rb_speed, rf_speed, lb_speed, lf_speed):
        self.motors["RB2"].move_forward(rb_speed)
        self.motors["RF2"].move_backward(rf_speed)
        self.motors["LB2"].move_backward(lb_speed)
        self.motors["LF2"].move_forward(lf_speed)
        self.controls("move-right", speed=rb_speed)

    def move_left(self, rb_speed, rf_speed, lb_speed, lf_speed):
        self.motors["RB2"].move_backward(rb_speed)
        self.motors["RF2"].move_forward(rf_speed)
        self.motors["LB2"].move_forward(lb_speed)
        self.motors["LF2"].move_backward(lf_speed)
        self.controls("move-left", speed=rb_speed)

    def move_right_forward(self, rb_speed, lf_speed):
        self.motors["RB2"].move_forward(rb_speed)
        self.motors["RF2"].stop()
        self.motors["LB2"].stop()
        self.motors["LF2"].move_forward(lf_speed)
        self.controls("move-right-forward", speed=rb_speed)

    def move_left_forward(self, rf_speed, lb_speed):
        self.motors["RB2"].stop()
        self.motors["RF2"].move_forward(rf_speed)
        self.motors["LB2"].move_forward(lb_speed)
        self.motors["LF2"].stop()
        self.controls("move-left-forward", speed=rf_speed)

    def move_right_backward(self, rf_speed, lb_speed):
        self.motors["RB2"].stop()
        self.motors["RF2"].move_backward(rf_speed)
        self.motors["LB2"].move_backward(lb_speed)
        self.motors["LF2"].stop()
        self.controls("move-right-backward", speed=rf_speed)

    def move_left_backward(self, rb_speed, lf_speed):
        self.motors["RB2"].move_backward(rb_speed)
        self.motors["RF2"].stop()
        self.motors["LB2"].stop()
        self.motors["LF2"].move_backward(lf_speed)
        self.controls("move-left-backward", speed=rb_speed)

    def move_turn_right(self, rb_speed, rf_speed, lb_speed, lf_speed):
        self.motors["RB2"].move_backward(rb_speed)
        self.motors["RF2"].move_backward(rf_speed)
        self.motors["LB2"].move_forward(lb_speed)
        self.motors["LF2"].move_forward(lf_speed)
        self.controls("move-turn-right", speed=rb_speed)

    def move_turn_left(self, rb_speed, rf_speed, lb_speed, lf_speed):
        self.motors["RB2"].move_forward(rb_speed)
        self.motors["RF2"].move_forward(rf_speed)
        self.motors["LB2"].move_backward(lb_speed)
        self.motors["LF2"].move_backward(lf_speed)
        self.controls("move-turn-left", speed=rb_speed)

    def move_around_left_front(self, lb_speed, lf_speed):
        self.motors["RB2"].stop()
        self.motors["RF2"].stop()
        self.motors["LB2"].move_forward(lb_speed)
        self.motors["LF2"].move_forward(lf_speed)
        self.controls("move-around-left-front", speed=lb_speed)
    
    def move_around_left_back(self, lb_speed, lf_speed):
        self.motors["RB2"].stop()
        self.motors["RF2"].stop()
        self.motors["LB2"].move_backward(lb_speed)
        self.motors["LF2"].move_backward(lf_speed)
        self.controls("move-around-left-back", speed=lb_speed)
    
    def move_around_right_front(self, rb_speed, rf_speed):
        self.motors["RB2"].move_forward(rb_speed)
        self.motors["RF2"].move_forward(rf_speed)
        self.motors["LB2"].stop()
        self.motors["LF2"].stop()
        self.controls("move-around-right-front", speed=rb_speed)
        
    def move_around_right_back(self, rb_speed, rf_speed):
        self.motors["RB2"].move_backward(rb_speed)
        self.motors["RF2"].move_backward(rf_speed)
        self.motors["LB2"].stop()
        self.motors["LF2"].stop()
        self.controls("move-around-right-back", speed=rb_speed)
        
    def move_around_front_right(self, rf_speed, lf_speed):
        self.motors["RB2"].stop()
        self.motors["RF2"].move_backward(rf_speed)
        self.motors["LB2"].stop()
        self.motors["LF2"].move_forward(lf_speed)
        self.controls("move-around-front-right", speed=rf_speed)
        
    def move_around_front_left(self, rf_speed, lf_speed):
        self.motors["RB2"].stop()
        self.motors["RF2"].move_forward(rf_speed)
        self.motors["LB2"].stop()
        self.motors["LF2"].move_backward(lf_speed)
        self.controls("move-around-front-left", speed=rf_speed)
        
    def move_around_back_right(self, rb_speed, lb_speed):
        self.motors["RB2"].move_backward(rb_speed)
        self.motors["RF2"].stop()
        self.motors["LB2"].move_forward(lb_speed)
        self.motors["LF2"].stop()
        self.controls("move-around-back-right", speed=rb_speed)
        
    def move_around_back_left(self, rb_speed, lb_speed):
        self.motors["RB2"].move_forward(rb_speed)
        self.motors["RF2"].stop()
        self.motors["LB2"].move_backward(lb_speed)
        self.motors["LF2"].stop()
        self.controls("move-around-back-left", speed=rb_speed)

    def stop(self):
        for motor in self.motors.values():
            motor.stop()
        self.controls("stop", speed=0)

    def cleanup(self):
        for motor in self.motors.values():
            motor.cleanup()
        GPIO.cleanup()