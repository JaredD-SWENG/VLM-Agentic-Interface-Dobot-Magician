
import threading
import DobotDllType as dType
print("EXECUTING DOBOT.PY")
CON_STR = {
    dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
    dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
    dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

# Load Dll and get the CDLL object
api = dType.load()

# Connect Dobot
state = dType.ConnectDobot(api, "COM4", 115200)[0]
print("Connect status:", CON_STR[state])

if (state == dType.DobotConnect.DobotConnect_NoError):

    # Clean Command Queued
    dType.SetQueuedCmdClear(api)

    # Async Motion Params Setting
    dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued=1)
    dType.SetPTPJointParams(api, 200, 200, 200, 200,
                            200, 200, 200, 200, isQueued=1)
    dType.SetPTPCommonParams(api, 100, 100, isQueued=1)

    pos = dType.GetPose(api)
    print(pos)
    x = pos[0]
    y = pos[1]
    z = pos[2]
    rHead = pos[3]
    ptpMode = 0

    def draw_J(api, start_x, start_y, height):
        ptpMode_jump = 0
        ptpMode_linear = 2
        z = -63

        dType.SetPTPCmd(api, ptpMode_jump, start_x,
                        start_y, z, rHead, isQueued=1)

        dType.SetPTPCmd(api, ptpMode_linear, start_x - height,
                        start_y, z, rHead, isQueued=1)

        base_width = height / 3
        dType.SetPTPCmd(api, ptpMode_linear, start_x - height,
                        start_y + base_width, z, rHead, isQueued=1)

    def draw_D(api, start_x, start_y, height):
        ptpMode_jump = 0
        ptpMode_linear = 2
        z = -63

        dType.SetPTPCmd(api, ptpMode_jump, start_x,
                        start_y, z, rHead, isQueued=1)
        width = height / 2
        dType.SetPTPCmd(api, ptpMode_linear, start_x-width,
                        start_y - width, z, rHead, isQueued=1)
        dType.SetPTPCmd(api, ptpMode_linear, start_x-height,
                        start_y, z, rHead, isQueued=1)
        dType.SetPTPCmd(api, ptpMode_linear, start_x,
                        start_y, z, rHead, isQueued=1)

    letter_height = 50
    draw_J(api, x, y, letter_height)
    draw_D(api, x, y - 60, letter_height)

    lastIndex = dType.SetPTPCmd(api, ptpMode, x, y, z, rHead, 0)[0]

    # Start to Execute Command Queue
    dType.SetQueuedCmdStartExec(api)

    # Wait for Executing Last Command
    while lastIndex > dType.GetQueuedCmdCurrentIndex(api)[0]:
        dType.dSleep(100)

    # Stop to Execute Command Queued
    dType.SetQueuedCmdStopExec(api)

# Disconnect Dobot
dType.DisconnectDobot(api)