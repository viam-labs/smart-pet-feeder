import asyncio
import os
import time

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.camera import Camera
from viam.components.motor import Motor
from viam.services.vision import VisionClient

# these must be set, you can get them from your robot's 'CODE SAMPLE' tab
robot_secret = os.getenv('ROBOT_SECRET') or ''
robot_address = os.getenv('ROBOT_ADDRESS') or ''

# change this if you named your camera differently in your robot configuration
camera_name = os.getenv('ROBOT_CAMERA') or 'petcam'

async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload=robot_secret)
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address(robot_address, opts)

async def main():
    robot = await connect()

    # robot components + services below, update these based on how you named them in configuration
    # pi
    pi = Board.from_robot(robot, "pi")
    
    # petcam
    petcam = Camera.from_robot(robot, "petcam")
    
    # stepper
    stepper = Motor.from_robot(robot, "stepper")
    
    # classifier_cam
    classifier_cam = Camera.from_robot(robot, "classifier_cam")
    
    # puppyclassifier
    puppyclassifier = VisionClient.from_robot(robot, "puppyclassifier")

    while True:
        # look if the camera is seeing the dog
        found = False
        classifications = await puppyclassifier.get_classifications_from_camera(camera_name)
        for d in classifications:
            # check if the model is confident in the classification
            if d.confidence > 0.7:
                print(d)
                if d.class_name.lower() == "toastml":
                    print("This is Toast")
                    found = True
             
        if (found):
            # turn on the stepper motor
            print("giving snack")
            state = "on"
            await stepper.go_for(rpm=80,revolutions=2)
            # stops the treat from constantly being dispensed 
            time.sleep(300)

        else:
            # turn off the stepper motor 
            print("it's not the dog, no snacks")
            state = "off"
            await stepper.stop()

        await asyncio.sleep(5)

        # don't forget to close the robot when you're done!
        await robot.close()
    

if __name__ == '__main__':
    asyncio.run(main())
