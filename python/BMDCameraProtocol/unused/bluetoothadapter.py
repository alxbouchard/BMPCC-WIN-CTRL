import time
import asyncio

from winrt.windows.devices.bluetooth import BluetoothLEDevice
from winrt.windows.devices.enumeration import DevicePairingProtectionLevel, DevicePairingKinds, DevicePairingResultStatus
from winrt.windows.devices.bluetooth.genericattributeprofile import GattCommunicationStatus, GattCharacteristicProperties
from winrt.windows.devices.enumeration import DeviceInformation


class BluetoothAdapter:
    def __init__(self, ble_device):
        self.ble_device = ble_device
        self.address = ble_device.BluetoothAddress
        self.name = ble_device.Name
        self.callbackPIN = None

    # public functions -----
    async def connect_with_pin(self, callbackPIN=None):
        self.callbackPIN = callbackPIN
        result = await self._pair_with_pin()
        return result

    def read_characteristic(self, uuid):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._read_characteristic(uuid))

        
        """result = await selectedCharacteristic.ReadValueAsync()
        if result.Status == GattCommunicationStatus.SUCCESS:
        
            var reader = DataReader.FromBuffer(result.Value);
            byte[] input = new byte[reader.UnconsumedBufferLength];
            reader.ReadBytes(input);
            // Utilize the data as needed"""
        
    async def _read_characteristic(self, uuid):
        #print(dir(self.ble_device))
        result = await self.ble_device.get_gatt_services_for_uuid_async(uuid, 1)#.get_characteristics_async()
        #print(result)

    def get_services(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._get_services())
        return result

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
        self.ble_device = BLEdevice
        deviceInformation = BLEdevice.device_information

        if deviceInformation.pairing.can_pair:
            customPairing = deviceInformation.pairing.custom
            customPairing.add_pairing_requested(self._custom_pairing_requested)
            result = await customPairing.pair_async(DevicePairingKinds.PROVIDE_PIN)
            if(result.status == DevicePairingResultStatus.PAIRED) or (result.status == DevicePairingResultStatus.ALREADY_PAIRED):
                print("hi")
                await self.startReceivingData()
                return True
            else :
                return False
            
        elif deviceInformation.pairing.is_paired:
            print("hi")
            await self.startReceivingData()
            return True

        else:
            return False

    # get_services helper functions -----
    async def _get_services(self):
        ble_device = self.ble_device
        result = await ble_device.get_gatt_services_async()

        if result.status == GattCommunicationStatus.SUCCESS:
            services = result.services
            print(services.size)
            for service in services:
                print(service.get_characteristics('7FE8691D-95DC-4FC5-8ABD-CA74339B51B9'))
                result = await service.get_characteristics_async()
                if result.status == GattCommunicationStatus.SUCCESS:
                    characteristics = result.characteristics
                    print(characteristics.size)
                    for characteristic in characteristics:
                        properties = characteristic.characteristic_properties
                        property_text = ""
                        if properties == GattCharacteristicProperties.READ:
                            property_text = "read"
                        if properties == GattCharacteristicProperties.WRITE:
                            property_text = "write"
                        if properties == GattCharacteristicProperties.NOTIFY:
                            property_text = "notify"
                        #print(characteristic.uuid)


            return services

    async def startReceivingData(self):
        print("Hello")
        leDevice = await BluetoothLEDevice.from_id_async(self.ble_device.device_id)
        self.ble_device = leDevice

        
        selector = "(System.DeviceInterface.Bluetooth.DeviceAddress:=\"{:X}\")".format(leDevice.bluetooth_address)
        print(selector)

        watcher = DeviceInformation.create_watcher(selector)
        watcher.on_added += Watcher_Added
        watcher.on_removed += Watcher_Removed
        watcher.start()
        
        def Watcher_Removed(sender, args):
            print("")

        async def Watcher_Added(sender, args):
        
            service = await GattDeviceService.from_id_async(args.id)
            if (service is not None):
            
                cResult = await service.get_characteristics_async()
                if (cResult.status == GattCommunicationStatus.SUCCESS):
                
                    characteristics = cResult.characteristics;

                    for characteristic in characteristics:
                    
                        print(characteristic)
                        #deviceCharacteristics.SetCharacteristic(characteristic);
                    
                
            
        