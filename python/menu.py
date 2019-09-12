import clr
import sys, os
import asyncio
debug_path = os.path.join(sys.path[0], "..", "Win10Bluetooth", "Win10Bluetooth", "bin", "Debug")
path = os.path.join(sys.path[0], "lib")
sys.path.append(debug_path)
clr.AddReference("Win10Bluetooth") #add .dll file
from Win10Bluetooth import BluetoothDiscoverer
from BMDCameraProtocol.bmdcamera import BMDCamera

class Menu:
    async def main_menu(self):
        playing = True
        
        while(playing):
            devices = []
            selected_devices = []
            selected_device = None
            print("\nMenu -----")
            print("1. Scan for 3 seconds")
            print("2. Connect to a device")
            print("3. Connect to all paired devices")
            print("0. Exit")
            try:
                selection = int(input("Selection : "))
            except:
                selection = -1

            if selection == 1:
                devices = self.scan_devices()
                self.show_device_found(devices)
            elif selection == 2:
                devices = self.scan_devices()
                if len(devices) == 0:
                    continue
                selected_devices = []
                selected_device = self.select_camera(devices)
                selected_devices.append(selected_device)
                paired = await self.connect_to_camera(selected_device)
                if not paired:
                    continue
                await self.camera_controller(selected_devices)
            elif selection == 3:
                devices = self.scan_devices()
                if len(devices) == 0:
                    continue
                selected_devices = self.select_all_paired_cameras(devices)
                if(len(selected_devices) == 0):
                    print("No device found")
                    continue
                task_list = []
                for camera in selected_devices:
                    task_list.append(asyncio.create_task(camera.connect(self.input_pin)))
                for task_element in task_list:
                    await task_element
                print("Connected to {} devices".format(len(selected_devices)))
                await self.camera_controller(selected_devices)
            elif selection == 0:
                playing = False
            else:
                continue

    async def camera_controller(self, selected_cameras):
        playing = True
        while(playing):
            print("\nCamera -----")
            print("1. Set pc timecode")
            print("2. Set focus")
            print("3. Start record")
            print("4. Stop record")
            print("5. Unpair")
            print("0. Disconnect")
            
            task_list = []
            try:
                choice = int(input("Selection : "))
            except:
                choice = -1
            if choice == 1:
                #timecode_string = input("HH:MM:SS:FF : ")

                for camera in selected_cameras:
                    task_list.append(asyncio.create_task(camera.set_timecode()))
                
            elif choice == 2:
                focus = int(input("Focus (min: 0, max: 8) : "))
                for camera in selected_cameras:
                    task_list.append(asyncio.create_task(camera.set_focus(focus)))
            elif choice == 3:
                for camera in selected_cameras:
                    task_list.append(asyncio.create_task(camera.start_record()))
            elif choice == 4:
                for camera in selected_cameras:
                    task_list.append(asyncio.create_task(camera.stop_record()))
            elif choice == 5:
                for camera in selected_cameras:
                    task_list.append(asyncio.create_task(camera.unpair()))
                for task_element in task_list:
                    await task_element
                task_list = []
                for camera in selected_cameras:
                    camera.dispose()
                    camera = None
                playing = False
            elif choice == 0:
                for camera in selected_cameras:
                    camera.dispose()
                    camera = None
                playing = False
            else:
                continue

            for task_element in task_list:
                await task_element

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
            if device.paired:
                paired_text = "- Paired"
            else:
                paired_text = ""
            print("{}. {} {}".format(index + 1, device.name, paired_text))

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

    def select_all_paired_cameras(self, cameras):
        paired_cameras = []
        for camera in cameras:
            if camera.paired:
                paired_cameras.append(camera)
        
        return paired_cameras
