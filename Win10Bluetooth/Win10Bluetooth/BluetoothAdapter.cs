using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Windows.Devices.Bluetooth;
using Windows.Devices.Bluetooth.GenericAttributeProfile;
using Windows.Devices.Enumeration;
using Windows.Storage.Streams;

namespace Win10Bluetooth
{
    public class BluetoothAdapter
    {
        public delegate string ProvidePinDelegate();
        BluetoothLEDevice bluetoothLEDevice;


        public ulong Address { get { return bluetoothLEDevice.BluetoothAddress; } }
        public string Name { get { return bluetoothLEDevice.Name; } }
        private ProvidePinDelegate callbackPin;
        private Dictionary<string, GattCharacteristic> characteristics;
        private DevicePairingRequestedEventArgs devicePairingCodePin = null;
        private string pin;

        public BluetoothAdapter(BluetoothLEDevice bleDevice)
        {
            bluetoothLEDevice = bleDevice;
            characteristics = new Dictionary<string, GattCharacteristic>();
            pin = null;
        }

        public async Task<bool> ConnectWithPin()
        {
            ulong address = this.Address;

            DeviceInformation deviceInformation = bluetoothLEDevice.DeviceInformation;

            if (deviceInformation.Pairing.CanPair)
            {
                DeviceInformationCustomPairing customPairing = deviceInformation.Pairing.Custom;
                customPairing.PairingRequested += OnCustomPairingRequested;
                DevicePairingResult result = await customPairing.PairAsync(DevicePairingKinds.ProvidePin);
                customPairing.PairingRequested -= OnCustomPairingRequested;
                if ((result.Status == DevicePairingResultStatus.Paired) || (result.Status == DevicePairingResultStatus.AlreadyPaired))
                {
                    return true;
                }
                else
                    return false;
            }
            else
                return false;
        }

        public async Task<bool> IsPaired()
        {
            ulong address = this.Address;
            DeviceInformation deviceInformation = bluetoothLEDevice.DeviceInformation;

            if (deviceInformation.Pairing.IsPaired)
            {
                return true;
            }
            else
                return false;
        }

        public async void WatchCharacteristics()
        {
            StartReceivingData();
        }

        public async Task<bool> Unpair()
        {
            DeviceUnpairingResult duResult = await bluetoothLEDevice.DeviceInformation.Pairing.UnpairAsync();
            Console.WriteLine("Unpair result: " + duResult.Status);
            if (duResult.Status == DeviceUnpairingResultStatus.Unpaired)
                return true;
            else
                return false;
        }

        public async Task<string> ReadCharacteristic(string uuid)
        {
            GattCharacteristic characteristic = GetCharacteristic(uuid);
            if (characteristic == null)
                return null;

            GattReadResult result = await characteristic.ReadValueAsync();
            if (result.Status != GattCommunicationStatus.Success)
                return null;

            var reader = DataReader.FromBuffer(result.Value);
            byte[] input = new byte[reader.UnconsumedBufferLength];
            reader.ReadBytes(input);
            return BytesToString(input);
        }

        public async Task<bool> WriteToCharacteristic(string uuid, byte[] message)
        {
            GattCharacteristic characteristic = GetCharacteristic(uuid);
            if (characteristic == null)
                return false;


            DataWriter writer = new DataWriter();
            // WriteByte used for simplicity. Other common functions - WriteInt16 and WriteSingle
            writer.WriteBytes(message);

            GattCommunicationStatus result = await characteristic.WriteValueAsync(writer.DetachBuffer());
            if (result == GattCommunicationStatus.Success)
            {
                return true;
            }
            else
                return false;
        }

        private void OnCustomPairingRequested(DeviceInformationCustomPairing sender, DevicePairingRequestedEventArgs args)
        {
            while (pin == null)
            {
                Thread.Sleep(500);
            }
            args.Accept(pin);
            pin = null;
        }

        public void SendPin(string pin)
        {
            this.pin = pin;
        }

        private string BytesToString(byte[] bytes)
        {
            string text = "";
            foreach (byte b in bytes)
            {
                text += b + "";
            }
            return text;
        }

        public void Dispose()
        {
            bluetoothLEDevice.Dispose();
        }

        public GattCharacteristic GetCharacteristic(string uuid)
        {
            return characteristics[uuid.ToLower()];
        }

        private void AddCharacteristic(GattCharacteristic characteristic)
        {
            characteristics[characteristic.Uuid.ToString()] = characteristic;
        }

        public async void StartReceivingData()
        {
            BluetoothLEDevice leDevice = await BluetoothLEDevice.FromIdAsync(bluetoothLEDevice.DeviceId);
            bluetoothLEDevice = leDevice;

            string selector = "(System.DeviceInterface.Bluetooth.DeviceAddress:=\"" +
                leDevice.BluetoothAddress.ToString("X") + "\")";


            DeviceWatcher watcher = DeviceInformation.CreateWatcher(selector);
            watcher.Added += Watcher_Added;
            watcher.Removed += Watcher_Removed;
            watcher.Start();
        }
        private void Watcher_Removed(DeviceWatcher sender,
            DeviceInformationUpdate args)
        { }
        private async void Watcher_Added(DeviceWatcher sender, DeviceInformation args)
        {
            GattDeviceService service = await GattDeviceService.FromIdAsync(args.Id);
            if (service != null)
            {
                GattCharacteristicsResult cResult = await service.GetCharacteristicsAsync();
                if (cResult.Status == GattCommunicationStatus.Success)
                {
                    IReadOnlyList<GattCharacteristic> characteristics = cResult.Characteristics;

                    foreach (GattCharacteristic characteristic in characteristics)
                    {
                        AddCharacteristic(characteristic);
                    }
                }
            }
        }
    }
}
