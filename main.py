import socket
import time
import sys, traceback
from BMDCameraProtocol.bluetoothdiscoverer import BluetoothDiscoverer

from LevitezerProtocol.message import Message
from LevitezerProtocol.bigbox import Bigbox
from LevitezerProtocol.gimbal import Gimbal

# Gimbal code test -----
def mainGimbal():
    try:
        bigbox = Bigbox("192.168.1.78", 50508, "TCP")
        bigbox.connect()
        gimbal = Gimbal(bigbox, 101)
        gimbal.setFrequency(100)
        time.sleep(1)
        gimbal.move(0, 0, 200)
        showGimbalStates(gimbal.states)
        time.sleep(1)
        showGimbalStates(gimbal.states)
        gimbal.setAngle(0, 0, 0, 500, 500, 500)
        showGimbalStates(gimbal.states)
        time.sleep(1)
        showGimbalStates(gimbal.states)
        bigbox.stopReading()

    except KeyboardInterrupt:
        bigbox.stopReading()
    sys.exit(0)

def showGimbalStates(states):
    print("imu_roll: {}".format(states.imu_roll))
    print("imu_pitch: {}".format(states.imu_pitch))
    print("imu_yaw: {}".format(states.imu_yaw))
    print("roll: {}".format(states.roll))
    print("pitch: {}".format(states.pitch))
    print("yaw: {}".format(states.yaw))
    print("timestamp: {}".format(states.timestamp))
    print("accel_roll: {}".format(states.accel_roll))
    print("accel_pitch: {}".format(states.accel_pitch))
    print("accel_yaw: {}".format(states.accel_yaw))
    print("angle_completed: {}".format(states.angle_completed))
    print("request_real_time_data: {}".format(states.request_real_time_data))
    print("board_version: {}".format(states.board_version))
    print("firmware_version: {}".format(states.firmware_version))

# BMDCamera code test -----
def mainCamera():
    print("Hello World!")
    bluetooth_discoverer = BluetoothDiscoverer()
    bluetooth_discoverer.scan_devices(2) # scan for 2 seconds

    if len(bluetooth_discoverer.ble_devices) == 0:
        print('No device found')
        return
    selected_device = select_camera(bluetooth_discoverer.ble_devices)
    print('Selected device : ', selected_device.name)
    paired = selected_device.connect(input_pin)

    print('Paired : ', paired)
    if paired:
        print('yay!')
        
def select_camera(devices):
    for index, device in enumerate(devices):
        print(index + 1, '. ', device.name)
    inputIndex = -1 + int(input('Enter number : '))
    selectedDevice = devices[inputIndex]
    return selectedDevice

def input_pin():
    pin = input('Enter PIN : ')
    return pin

# Launch test 
if __name__ == "__main__":
    mainCamera()
