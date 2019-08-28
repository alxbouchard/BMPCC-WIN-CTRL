import clr
import sys, os
from .bmdcameracharacteristics import BMDCameraCharacteristics
debug_path = os.path.join(sys.path[0], "..", "Win10Bluetooth", "Win10Bluetooth", "bin", "Debug")
path = os.path.join(sys.path[0], "lib")
sys.path.append(debug_path)
clr.AddReference("Win10Bluetooth") #add .dll file
import numpy

from Win10Bluetooth import BluetoothAdapter

class BMDCamera:
    def __init__(self, ble_device):
        self.bluetooth_adapter = BluetoothAdapter(ble_device)
        self.name = ble_device.Name

    async def connect(self, callback_input_pin):
        if not self.bluetooth_adapter.IsPaired().Result:
            task = self.bluetooth_adapter.ConnectWithPin()
            pin = callback_input_pin()
            self.bluetooth_adapter.SendPin(pin)
            paired = task.Result
        else:
            paired = True
        if paired:
            self.bluetooth_adapter.WatchCharacteristics()
        return paired

    async def read_camera_status(self):
        result = self.bluetooth_adapter.ReadCharacteristic(BMDCameraCharacteristics.CAMERA_STATUS).Result
        return result
        
    async def read_protocol_version(self):
        result = self.bluetooth_adapter.ReadCharacteristic(BMDCameraCharacteristics.PROTOCOL_VERSION).Result
        return result
        
    async def power_off_camera(self):
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.CAMERA_STATUS, [0]).Result
        return result

    async def power_on_camera(self):
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.CAMERA_STATUS, [1]).Result
        return result
        
    async def change_name(self, name):
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.DEVICE_NAME, name.encode()).Result
        return result
         
    async def start_record(self):
        message = [255, 8, 0, 0, 10, 1, 1, 0, 2, 1, 1, 1]
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.OUTGOING_CAMERA, message).Result
        return result
        
    async def set_timecode(self, HH,  MM, SS, FF):
        HH -= 1
        MM -= 4
        nbHour = MM / 60
        HH += nbHour
        HH = self.Mod(HH, 24)
        MM = self.Mod(MM, 60)

        message = [ 255, 12, 0, 0, 7, 0, 3, 0, FF, SS, MM, HH, 0, 0, 0, 0 ]
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.OUTGOING_CAMERA, message).Result
        return result
    
    async def set_focus(self, focus):
        #value = numpy.float16(focus)
        #ba = bytearray(struct.pack("f", value))  
        #ba = value.tobytes()
        #print(len(ba))
        #print("{} {}". format(ba[0], ba[1]))
        message = [255, 6, 0, 0, 0, 0, 128, 0, 0, focus]
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.OUTGOING_CAMERA, message)
        return result
         
    def Mod(self, x, m):
        r = x % m

        if r < 0:
            return r + m
        else:
            return r

    def dispose(self):
        self.bluetooth_adapter.Dispose()

    async def unpair(self):
        return self.bluetooth_adapter.Unpair().Result