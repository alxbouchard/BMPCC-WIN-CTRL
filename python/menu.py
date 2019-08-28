import clr
import sys, os
debug_path = os.path.join(sys.path[0], "..", "Win10Bluetooth", "Win10Bluetooth", "bin", "Debug")
path = os.path.join(sys.path[0], "lib")
sys.path.append(debug_path)
clr.AddReference("Win10Bluetooth") #add .dll file
from Win10Bluetooth import BluetoothDiscoverer
from BMDCameraProtocol.bmdcamera import BMDCamera

class Menu:
    async def main_menu(self):
        playing = True
        devices = []
        while(playing):
            print("\nMenu -----")
            print("1. Scan for 3 seconds")
            print("2. Connect to a device")
            print("0. Exit")
            selection = int(input("Selection : "))

            if selection == 1:
                devices = self.scan_devices()
                self.show_device_found(devices)
            elif selection == 2:
                devices = self.scan_devices()
                if len(devices) == 0:
                    return
                selected_device = self.select_camera(devices)
                paired = await self.connect_to_camera(selected_device)
                if not paired:
                    continue
                await self.camera_controller(selected_device)
            elif selection == 0:
                playing = False
            else:
                continue

    async def camera_controller(self, selected_camera):
        playing = True
        while(playing):
            print("\nCamera -----")
            print("1. Set timecode")
            print("2. Set focus")
            print("3. Start record")
            print("4. Disconnect")
            print("5. Unpair")
            print("0. Back to main menu")

            choice = int(input("Selection : "))
            if choice == 1:
                timecode_string = input("HH,MM,SS,FF : ")
                timecode = timecode_string.split(",")
                time_array = [int(x) for x in timecode]
                await selected_camera.set_timecode(time_array[0], time_array[1], time_array[2], time_array[3])
            elif choice == 2:
                focus = int(input("Focus (min: 0, max: 8) : "))
                await selected_camera.set_focus(focus)
            elif choice == 3:
                await selected_camera.start_record()
            elif choice == 4:
                selected_camera.dispose()
                playing = False
            elif choice == 5:
                await selected_camera.unpair()
                selected_camera.dispose()
                playing = False
            elif choice == 0:
                playing = False
            else:
                continue

    async def connect_to_camera(self, selected_device):
        print('Selected device : ', selected_device.name)
        paired = await selected_device.connect(self.input_pin)

        print('Paired : ', paired)
        if paired:
            print('Connected!')
        return paired

    def show_device_found(self, devices):
        for index, device in enumerate(devices):
            print("\nDevices : ")
            print("{}. {}".format(index + 1, device.name))

    def select_camera(self, devices):
        self.show_device_found(devices)
        inputIndex = -1 + int(input('Enter number : '))
        selectedDevice = devices[inputIndex]
        return selectedDevice

    @staticmethod
    def input_pin():
        pin = input('Enter PIN : ')
        return pin

    def create_device(self, ble_device):  
        if "Pocket Cinema Camera 4K" in ble_device.Name:
            return BMDCamera(ble_device)
        else:
            return None

    def scan_devices(self):
        bluetooth_discoverer = BluetoothDiscoverer()
        ble_devices = bluetooth_discoverer.ScanDevices(2000).Result # scan for ms
        devices = []
        for ble_device in ble_devices:
            camera = self.create_device(ble_device)
            if camera is None:
                continue
            devices.append(camera)
        if len(devices) == 0:
            print('No device found')
        return devices