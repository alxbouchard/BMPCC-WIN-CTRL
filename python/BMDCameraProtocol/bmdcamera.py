import clr
import sys, os
import time
import datetime
from .bmdcameracharacteristics import BMDCameraCharacteristics
debug_path = os.path.join(sys.path[0], "..", "Win10Bluetooth", "Win10Bluetooth", "bin", "Debug")
path = os.path.join(sys.path[0], "lib")
sys.path.append(debug_path)
clr.AddReference("Win10Bluetooth") #add .dll file
#import numpy

from Win10Bluetooth import BluetoothAdapter

class BMDCamera:
    def __init__(self, ble_device):
        self.bluetooth_adapter = BluetoothAdapter(ble_device)
        self.name = ble_device.Name

    @property
    def paired(self):
        return self.bluetooth_adapter.IsPaired().Result

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
        
    async def stop_record(self):
        message = [255, 8, 0, 0, 10, 1, 1, 0, 0, 1, 1, 1]
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.OUTGOING_CAMERA, message).Result
        return result

    async def set_timecode(self):
        SECOND = 24
        MINUTE = 60 * SECOND
        HOUR = 60 * MINUTE
        DAY = 24 * HOUR

        """
        timecode_split = timecode_string.split(":")

        HH = int(timecode_split[0])
        MM = int(timecode_split[1])
        SS = int(timecode_split[2])
        FF = int(timecode_split[3])

        total_frames = HH * HOUR + MM * MINUTE + SS * SECOND + FF"""
        
        date = datetime.datetime.now()

        yearH = BMDCamera.decimal_to_bcd(date.year // 100)
        yearL = BMDCamera.decimal_to_bcd(date.year % 100)
        month = BMDCamera.decimal_to_bcd(date.month)
        day = BMDCamera.decimal_to_bcd(date.day)

        seconds_utc = time.time()
        seconds_timezone = time.localtime().tm_gmtoff
        seconds_local = seconds_utc + seconds_timezone
        seconds_local = seconds_local % (DAY / SECOND)
        
        total_frames = int(round(seconds_local * 24))
        print(total_frames)
        offset_frames = 1 * HOUR + 4 * MINUTE

        diff_frames = BMDCamera.Mod(total_frames, DAY)


        HH = diff_frames // HOUR
        diff_frames -= HH * HOUR
        MM = diff_frames // MINUTE
        diff_frames -= MM * MINUTE
        SS = diff_frames // SECOND
        diff_frames -= SS * SECOND
        FF = diff_frames

        print("{}:{}:{}:{}".format(HH, MM, SS, FF))

        HH = BMDCamera.decimal_to_bcd(HH)
        MM = BMDCamera.decimal_to_bcd(MM)
        SS = BMDCamera.decimal_to_bcd(SS)
        FF = BMDCamera.decimal_to_bcd(FF)

        message = [ 255, 12, 0, 0, 7, 0, 3, 0, FF, SS, MM, HH, day, month, yearL, yearH ]
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.OUTGOING_CAMERA, message).Result
        return result

    async def set_time_offset(self, minutes):  
        
        ba = (minutes).to_bytes(4, byteorder="little", signed=True)
        message = [ 255, 8, 0, 0, 7, 2, 3, 0, ba[0], ba[1], ba[2], ba[3] ]
        result = self.bluetooth_adapter.WriteToCharacteristic(BMDCameraCharacteristics.OUTGOING_CAMERA, message).Result
        print("offset : {}".format(result))
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
        
    @staticmethod
    def decimal_to_bcd(decimal):
        hexadecimal = (decimal // 10) * 16 + decimal % 10
        return hexadecimal

    @staticmethod
    def Mod(x, m):
        r = x % m

        if r < 0:
            return r + m
        else:
            return r

    def dispose(self):
        self.bluetooth_adapter.Dispose()
        self.bluetooth_adapter = None

    async def unpair(self):
        return self.bluetooth_adapter.Unpair().Result