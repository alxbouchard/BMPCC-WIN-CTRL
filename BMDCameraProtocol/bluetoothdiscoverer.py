import time
import asyncio

from winrt.windows.devices.bluetooth.advertisement import BluetoothLEAdvertisementWatcher, BluetoothLEAdvertisementReceivedEventArgs, BluetoothLEScanningMode
from winrt.windows.devices.bluetooth import BluetoothLEDevice

from .bmdcamera import BMDCamera


DEVICE_NAMES = {'bmdcamera': 'Pocket Cinema Camera 4K'}

class BluetoothDiscoverer:
    
    def __init__(self, callbackPIN=None):
        self.deviceAddresses = []
        self.ble_devices = []
        self.callbackPIN = callbackPIN

    def scan_devices(self, seconds):
        self.ble_devices = []

        watcher = BluetoothLEAdvertisementWatcher()
        watcher.scanning_mode = BluetoothLEScanningMode.ACTIVE
        watcher.add_received(self._on_advertisement_received)

        watcher.start()
        time.sleep(seconds)
        watcher.stop()

    def _on_advertisement_received(self, btAdvWatcher, btAdvEvent):
        address = btAdvEvent.bluetooth_address

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ble_device = loop.run_until_complete(self._ask_device_information(address))
        
        name = ble_device.name
        
        if not self._isNewAddress(address):
            return

        self.deviceAddresses.append(address)

        device = self._create_device(address, name)
        if device is not None:
            self.ble_devices.append(device)

    async def _ask_device_information(self, address):
        device = await BluetoothLEDevice.from_bluetooth_address_async(address)
        return device

    def _create_device(self, address, name):
        device = None

        if DEVICE_NAMES['bmdcamera'] in name:
            device = BMDCamera(address, name)

        return device

    def _isNewAddress(self, address):
        isNew = True
        for dev_address in self.deviceAddresses:
            if address == dev_address:
                isNew = False
                break
        return isNew
