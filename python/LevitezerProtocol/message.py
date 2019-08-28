import array

class Message:
    """Message class for sending a message to a bigbox or to decode a message received from a bigbox"""
    def __init__(self, deviceId=None, deviceType=None, fromBytes=None):
        """Two way to create a new message object:
        1. Add deviceId and deviceType
        2. Add a binary message received from bigbox in fromBytes parameters
        """
        if fromBytes != None:
            self._fromBytes(fromBytes)
        elif deviceId != None and deviceType != None:
            self.deviceId = deviceId
            self.deviceType = deviceType
            self.parameters = []
            self.counter = 0
        else:
            raise ValueError("Invalid arguments for Message")

    def _fromBytes(self, message):
        """Decode a binary message received from a bigbox"""
        self.deviceId = message[3]
        self.deviceType = message[4]
        self.counter = message[5]

        self.parameters = []
        if message[6] > 22:
            return
        for i in range(6, len(message) - 3, 3):
            id = message[i]
            value = message[i + 1] + (message[i + 2] << 8)
            self.parameters.append({'id': id, 'value': value})

    def _addHeader(self, message):
        """Add header to binary message for bigbox"""
        header = [0xff, 0xff, 0xff]

        message.append(header[0])
        message.append(header[1])
        message.append(header[2])
        message.append(self.deviceId)
        message.append(self.deviceType)
        message.append(self.counter)
    
    def _addParameters(self, message):
        """Add parameters to binary message for bigbox"""
        for parameter in self.parameters:
            value = parameter['value']
            if value < 0:
                value += 2**16

            message.append(parameter['id'])
            message.append(value & 0xff)
            message.append(value >> 8)
        
        message.append(0)

    def _addChecksum(self, message):
        """Calculate and add checksum to binary message for bigbox"""
        # calculate checksum starting in 3rd index
        checksum = 0
        for i in range(3, len(message)):
            checksum = (checksum + message[i]) & 0xffff # 16 bit overflow 
        
        # set the 16bit checksum at the end of the array
        message.append(checksum & 0xff)
        message.append(checksum >> 8)
    
    def tobytes(self):
        """Build and return message in an array of bytes"""
        message = []
        self._addHeader(message)
        self._addParameters(message)
        self._addChecksum(message)

        return array.array('B', message).tobytes()
