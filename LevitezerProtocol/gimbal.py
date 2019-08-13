from .message import Message
from .bigbox import Bigbox

class Gimbal:
    _deviceType = 1

    def __init__(self, bigbox, deviceId):
        self.deviceId = deviceId
        self.states = GimbalStates()
        self.bigbox = bigbox
        self.bigbox.addListener(self.deviceId, self.states.updateStates)

    def setAngle(self, roll, pitch, yaw, rollSpeed, pitchSpeed, yawSpeed):
        mode = 2
        
        # convert angle to raw value
        rawRoll = int(roll / 0.02197265625)
        rawPitch = int(pitch / 0.02197265625)
        rawYaw = int(yaw / 0.02197265625)

        message = Message(self.deviceId, Gimbal._deviceType)

        message.parameters.append({'id': 4, 'value': rawRoll})
        message.parameters.append({'id': 5, 'value': rawPitch})
        message.parameters.append({'id': 6, 'value': rawYaw})

        message.parameters.append({'id': 10, 'value': rollSpeed})
        message.parameters.append({'id': 11, 'value': pitchSpeed})
        message.parameters.append({'id': 12, 'value': yawSpeed})

        message.parameters.append({'id': 16, 'value': mode})

        self.bigbox.sendMessage(message)
    
    def move(self, rollSpeed, pitchSpeed, yawSpeed):
        mode = 1
    
        message = Message(self.deviceId, Gimbal._deviceType)

        message.parameters.append({'id': 10, 'value': rollSpeed})
        message.parameters.append({'id': 11, 'value': pitchSpeed})
        message.parameters.append({'id': 12, 'value': yawSpeed})

        message.parameters.append({'id': 16, 'value': mode})

        self.bigbox.sendMessage(message)
    
    def reset(self):
        self.setAngle(0, 0, 0, 500, 500, 1000)
    
    def setFrequency(self, ms):
        message = Message(self.deviceId, Gimbal._deviceType)
        message.parameters.append({'id': 19, 'value': ms})
        self.bigbox.sendMessage(message)

class GimbalStates:
    def __init__(self):
        self.imu_roll = None        
        self.imu_pitch = None      
        self.imu_yaw = None        
        self.roll = None        
        self.pitch = None        
        self.yaw = None        
        self.timestamp = None       
        self.accel_roll = None        
        self.accel_pitch = None    
        self.accel_yaw = None
        self.angle_completed = None
        self.request_real_time_data = None
        self.board_version = None
        self.firmware_version = None

    def updateStates(self, message):
        for parameter in message.parameters:
            id = parameter['id']
            value = parameter['value']
            if id == 1:
                self.imu_roll = int(value * 0.02197265625)
            if id == 2:
                self.imu_pitch = int(value * 0.02197265625)
            if id == 3:
                self.imu_yaw = int(value * 0.02197265625)
            if id == 4:
                self.roll = int(value * 0.02197265625)
            if id == 5:
                self.pitch = int(value * 0.02197265625)
            if id == 6:
                self.yaw = int(value * 0.02197265625)
            if id == 7:
                self.timestamp = value
            if id == 13:
                self.accel_roll = value
            if id == 14:
                self.accel_pitch = value
            if id == 15:
                self.accel_yaw = value
            if id == 18:
                self.angle_completed = value
            if id == 19:
                self.request_real_time_data = value
            if id == 21:
                self.board_version = value
            if id == 22:
                self.firmware_version = value
