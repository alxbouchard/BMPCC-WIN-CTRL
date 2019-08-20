import time
import asyncio

from winrt.windows.devices.bluetooth import BluetoothLEDevice
from winrt.windows.devices.enumeration import DevicePairingProtectionLevel, DevicePairingKinds, DevicePairingResultStatus

class BluetoothAdapter:
    def __init__(self, address):
        self.ble_device = None
        self.address = address
        self.name = None
        self.callbackPIN = None

    # public functions -----
    def connect_with_pin(self, callbackPIN=None):
        self.callbackPIN = callbackPIN
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._pair_with_pin())
        return result
    
    def get_services(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        #result = loop.run_until_complete(self._pair_with_pin())

    # connect_with_pin helper functions -----
    def _custom_pairing_requested(self, sender, args):
        if self.callbackPIN is not None:
            pin = self.callbackPIN()
        else:
            pin = ""
        args.accept(pin)

    async def _pair_with_pin(self):
        address = self.address
        BLEdevice = await BluetoothLEDevice.from_bluetooth_address_async(address)
        deviceInformation = BLEdevice.device_information

        if deviceInformation.pairing.can_pair:
            customPairing = deviceInformation.pairing.custom
            customPairing.add_pairing_requested(self._custom_pairing_requested)
            result = await customPairing.pair_async(DevicePairingKinds.PROVIDE_PIN)
            if(result.status == DevicePairingResultStatus.PAIRED) or (result.status == DevicePairingResultStatus.ALREADY_PAIRED):
                return True
            else :
                return False
            
        elif deviceInformation.pairing.is_paired:
            return True

        else:
            return False

    # get_services helper functions -----
    #async def _get_services(self):
        #ble_device = self.ble_device
        #result = await ble_device.get_gatt_services_async()
        #if (result.Status == GattCommunicationStatus.SUCCESS):
            #services = result.services