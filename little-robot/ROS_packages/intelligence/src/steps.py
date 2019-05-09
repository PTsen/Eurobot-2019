#!/usr/bin/env python

import RPi.GPIO as GPIO
import rospy
from geometry_msgs.msg import Point
from std_msgs.msg import Bool, Empty



# Set the global variables
left = 0
start = 0
step = 1



# Set up the Raspberry pins
GPIO.setwarnings(False) # Ignore warning
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

# button0 - side - 38
# button1 - start - 37
pins = [38, 37] # The used pin(s)

for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pins to be an input pin and set initial value to be pulled low (off)



# Definition of the ROS publisher
bob_pub = rospy.Publisher('show_bob', Empty, queue_size=10)
nav_pub = rospy.Publisher('required_coords', Point, queue_size=10)
rotate_pub = rospy.Publisher('rotate_instructions', Point, queue_size=10)
take_pub = rospy.Publisher('take_puck', Empty, queue_size=10)
flush_pub = rospy.Publisher('flush_pucks', Empty, queue_size=10)



# Definition of the functions

# Toggle message send to the arduino (pump) to deploy the suction cup
def show_bob():
    global bob_pub
    bob_pub.publish(Empty())



# To read the button (GPIO) of the side
def is_left():
    global left
    global step
    if GPIO.input(pins[0]) == GPIO.LOW:
        left = 1
    else:
        left = 0
    finally:
        if step == 1:
            show_bob()



# To read the button (GPIO) of the sart
def is_started():
    global start
    if GPIO.input(pins[1]) == GPIO.LOW:
        start = 1
    else:
        start = 0



# To send the coordinates to the arduino (navigation)
def go_to(x, y):
    global nav_pub
    nav_pub.publish(Point(x, y, 0))



# To send the angle of rotation to the arduino (navigation)
def rotate(degrees):
    lobal rotate_pub
    rotate_pub.publish(Point(degrees, 0, 0)) # send with Point structure (easier)



# Toggle message send to the arduino (pump) to take a puck
def take_puck():
    global take_pub
    take_pub.publish(Empty())



# Toggle message send to the arduino (pump) to flush the pucks
def flush_pucks():
    global flush_pub
    flush_pub.publish(Empty())



# The "big" auomation function (callback)
def step_ok_callback(data):
    if data.data == True:
        global step
        global left
        if step == 1:
            if left == 1:
                go_to(0, -30) # x and y: the coordinates of the left dispenser (1)
            else:
                go_to(0, 30) # x and y: the coordinates of the right dispenser (1)

        if step == 2:
            if left == 1:
                rotate(90)
            else:
                rotate(-90)

        if step == 3:
            if left == 1:
                go_to(0, 15) # x and y: the coordinates of the first puck
            else:
                go_to(0, -15) # x and y: the coordinates of the first puck

        if step == 4:
            go_to(x, y) # x and y: the coordinates to adjust to take the puck

        if step == 5:
            take_puck()

        if step == 6:
            go_to(-x, -y) # x and y: the coordinates to go back after the take of the puck

        if step == 7:
            if left == 1:
                go_to(x, y) # x and y: the coordinates of the second puck
            else:
                go_to(x, Y) # x and y: the coordinates of the second puck

        if step == 8:
            go_to(x, y) # x and y: the coordinates to adjust to take the puck

        if step == 9:
            take_puck()

        if step == 10:
            go_to(-x, -y) # x and y: the coordinates to go back after the take of the puck

        if step == 11:
            if left == 1:
                go_to(x, y) # x and y: the coordinates of the third puck
             else:
                go_to(x, Y) # x and y: the coordinates of the third puck

        if step == 12:
            go_to(x, y) # x and y: the coordinates to adjust to take the puck

        if step == 13:
            take_puck()

        if step == 14:
            go_to(-x, -y) # x and y: the coordinates to go back after the take of the puck

        if step == 15:
            rotate(-90)

        if step == 16:
            go_to(x, y) # x and y: the coordinates of the balance
            if left == 1:
                go_to(x, y) # x and y: the coordinates to adjust ramp

        if step == 17:
            flush_pucks()

        if step == 18:
            rospy.loginfo("Finished !")

        if step > 18:
            rospy.loginfo("Anormally finished !")
        step += 1

    else:
        rospy.loginfo("Waiting ...") # security of test


if __name__ == '__main__':
    try:
        rospy.init_node("raspberry", anonymous=True)
        rospy.Subscriber('curry_arrived', Bool, step_ok_callback)
        rate=rospy.Rate(1)

        while not rospy.is_shutdown():
            is_started()
            if start == 1:
                is_left()
                rospy.loginfo(step)
                rate.sleep()

            else:
                print('Not started')

    except rospy.ROSInterruptException:
        pass