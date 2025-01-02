import DobotDllType as dType
import time

# Connect to Dobot
api = dType.load()
state = dType.ConnectDobot(api, "", 115200)[0]
if state != 0:
    print("Error connecting to Dobot")
    exit()

# Set parameters (adjust as needed)
dType.SetHOMEParams(api, 200, 200, 200, 200)
dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200)
dType.SetPTPCommonParams(api, 100, 100)
dType.SetPTPCoordinateParams(api, 200, 200, 200, 200) #Added for smoother movement

ptpMode = 2 # Linear mode

# Block coordinates (replace with actual values from your system)
yellow_x = -12.991453
yellow_y = 387.2255488632734
yellow_z = 40.854700854700894

blue_x = 114.444444
blue_y = 398.4032
blue_z = 40.854700854700894

# Target position (add safety margin)
target_x = blue_x + 20
target_y = yellow_y
target_z = yellow_z


#Safety height above blocks
safety_height = 50


#Step 1: Pick up yellow block

#Approach above yellow block
approach_x = yellow_x
approach_y = yellow_y
approach_z = yellow_z + 10

dType.SetPTPCmd(api, ptpMode, approach_x, approach_y, approach_z, 0, 0)
time.sleep(2)


#Descend and grip (Simulate gripping – replace with actual gripper control)
dType.SetPTPCmd(api, ptpMode, approach_x, approach_y, yellow_z, 0, 0)
time.sleep(2)
print("Gripper closed (simulated)")


#Lift yellow block
dType.SetPTPCmd(api, ptpMode, approach_x, approach_y, safety_height, 0, 0)
time.sleep(2)



#Step 2: Move yellow block

#Move to target position
dType.SetPTPCmd(api, ptpMode, target_x, target_y, safety_height, 0, 0)
time.sleep(2)

#Descend to surface
dType.SetPTPCmd(api, ptpMode, target_x, target_y, target_z, 0, 0)
time.sleep(2)

#Release yellow block (Simulate releasing – replace with actual gripper control)
print("Gripper opened (simulated)")


#Step 3: Retract
retract_x = 0 # Define safe retract position
retract_y = 0
retract_z = safety_height

dType.SetPTPCmd(api, ptpMode, retract_x, retract_y, retract_z, 0, 0)
time.sleep(2)

# Disconnect from Dobot
dType.DisconnectDobot(api)