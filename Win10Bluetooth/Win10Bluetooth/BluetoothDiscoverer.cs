using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Windows.Devices.Bluetooth;
using Windows.Devices.Bluetooth.Advertisement;

namespace Win10Bluetooth
{
    public class BluetoothDiscoverer
    {
        List<ulong> addresses;
        List<BluetoothLEDevice> bleDevices;
        public BluetoothDiscoverer()
        {
            addresses = new List<ulong>();
            bleDevices = new List<BluetoothLEDevice>();
        }

        public async Task<List<BluetoothLEDevice>> ScanDevices(int ms)
        {
            bleDevices.Clear();
            BluetoothLEAdvertisementWatcher watcher = new BluetoothLEAdvertisementWatcher();
            watcher.ScanningMode = BluetoothLEScanningMode.Active;
            watcher.Received += OnAdvertisementReceived;
            watcher.Start();
            await Task.Delay(ms);
            watcher.Stop();
            return bleDevices;
        }

        public bool isNewAddress(ulong newAddress)
        {
            bool isNew = true;
            foreach (ulong address in addresses)
            {
                if (address == newAddress)
                {
                    isNew = false;
                    break;
                }
            }
            return isNew;
        }

        private async void OnAdvertisementReceived(BluetoothLEAdvertisementWatcher watcher, BluetoothLEAdvertisementReceivedEventArgs eventArgs)
        {
            ulong address = eventArgs.BluetoothAddress;

            BluetoothLEDevice bleDevice = await BluetoothLEDevice.FromBluetoothAddressAsync(address);
            if (bleDevice == null)
                return;

            if (!isNewAddress(address))
                return;
            addresses.Add(address);
            bleDevices.Add(bleDevice);

        }
    }
}
