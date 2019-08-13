import array

class Message:
    def __init__(self, deviceId=None, deviceType=None, fromBytes=None):
        if fromBytes != None:
            self.fromBytes(fromBytes)
        else:
            self.deviceId = deviceId
            self.deviceType = deviceType
            self.parameters = []
            self.counter = 0

    def fromBytes(self, message):
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
        header = [0xff, 0xff, 0xff]

        message.append(header[0])
        message.append(header[1])
        message.append(header[2])
        message.append(self.deviceId)
        message.append(self.deviceType)
        message.append(self.counter)
    
    def _addParameters(self, message):
    
        for parameter in self.parameters:
            value = parameter['value']
            if value < 0:
                value += 2**16

            message.append(parameter['id'])
            message.append(value & 0xff)
            message.append(value >> 8)
        
        message.append(0)

    def _addChecksum(self, message):
        # calculate checksum starting in 3rd index
        checksum = 0
        for i in range(3, len(message)):
            checksum = (checksum + message[i]) & 0xffff # 16 bit overflow 
        
        # set the 16bit checksum at the end of the array
        message.append(checksum & 0xff)
        message.append(checksum >> 8)
    
    def tobytes(self):
        message = []
        self._addHeader(message)
        self._addParameters(message)
        self._addChecksum(message)

        return array.array('B', message).tobytes()
