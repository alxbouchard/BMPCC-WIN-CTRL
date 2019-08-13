import socket
from .message import Message
import time
from threading import Thread

class Bigbox:
    def __init__(self, ip, port, protocol="TCP"):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.socket.settimeout(1)
        
        self.counter = 0
        self.listeners = []

    def connect(self):
        print("Connecting")
        self.socket.connect((self.ip, self.port))

        print("After")
        self.startReading()
         
    def sendMessage(self, message):
        message.counter = self.counter
        self.socket.send(message.tobytes())
        self.counter += 1

    def addListener(self, deviceId, callback):
        self.listeners.append({'id': deviceId, 'callback': callback})
    
    def startReading(self):
        self.reading = True
        self.thread = ReadSocket(self)
        self.thread.start()
    
    def stopReading(self):
        self.reading = False
        self.thread.join()
    
class ReadSocket(Thread):
    def __init__(self, device):
        Thread.__init__(self)
        self.device = device
        

    def run(self):
        while self.device.reading:
            try:
                sMessage = self.device.socket.recv(2048)
            except socket.timeout:
                print("Can't read bigbox")
                self.device.reading = False
                continue  
            message = Message(fromBytes= sMessage)
            
            for listener in self.device.listeners:
                if message.deviceId == listener['id']:
                    listener['callback'](message)
