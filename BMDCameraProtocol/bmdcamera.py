from .bluetoothadapter import BluetoothAdapter

class BMDCamera:
    def __init__(self, address, name):
        self.bluetooth_adapter = BluetoothAdapter(address)
        self.name = name

    def connect(self, callback_input_pin):
        result = self.bluetooth_adapter.connect_with_pin(callback_input_pin)
        return result

