from engine_control import Robot
import socket

robot = Robot()
HOST = '0.0.0.0'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    try:
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Connected by {addr}")
                command = conn.recv(1024).decode('utf-8')
                print(f"Command received: {command}")

                data = command.split(':')
                action = data[0]
                speed = int(data[1]) if len(data) > 1 else 50


                if action == 'move-left-forward':
                    robot.move_left_forward(rf_speed=speed, lb_speed=speed)
                elif action == 'move-forward':
                    robot.move_forward(rb_speed=speed, rf_speed=speed, lb_speed=speed, lf_speed=speed)
                elif action == 'move-right-forward':
                    robot.move_right_forward(rb_speed=speed, lf_speed=speed)
                elif action == 'move-left':
                    robot.move_left(rb_speed=speed, rf_speed=speed, lb_speed=speed, lf_speed=speed)
                elif action == 'stop':
                    robot.stop()
                elif action == 'move-right':
                    robot.move_right(rb_speed=speed, rf_speed=speed, lb_speed=speed, lf_speed=speed)
                elif action == 'move-left-backward':
                    robot.move_left_backward(rb_speed=speed, lf_speed=speed)
                elif action == 'move-backward':
                    robot.move_backward(rb_speed=speed, rf_speed=speed, lb_speed=speed, lf_speed=speed)
                elif action == 'move-right-backward':
                    robot.move_right_backward(rf_speed=speed, lb_speed=speed)
                elif action == 'move-turn-left':
                    robot.move_turn_left(rb_speed=speed, rf_speed=speed, lb_speed=speed, lf_speed=speed)
                elif action == 'move-turn-right':
                    robot.move_turn_right(rb_speed=speed, rf_speed=speed, lb_speed=speed, lf_speed=speed)
                else:
                    print(f"Unknown action: {action}")
                    
    except KeyboardInterrupt:
        print("Manual stopped.")
    finally:
        robot.stop()
        robot.cleanup()
