import socket
from .message import Message
import time
from threading import Thread

class Bigbox:
    """Represent a Levitezer Bigbox. It contains a socket to send and receive message from a bigbox"""
    def __init__(self, ip, port, protocol="TCP"):
        """Init a bigbox"""
        self.ip = ip
        self.port = port
        if protocol == "UDP":
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        elif protocol == "TCP":
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        else:
            raise ValueError("Invalid protocol name")
        self.socket.settimeout(1)
        
        self.counter = 0
        self.listeners = []

    def connect(self):
        """Connect to bigbox and start reading messages"""
        print("Connecting")
        self.socket.connect((self.ip, self.port))
        self.startReading()
         
    def sendMessage(self, message):
        """Send a message to bigbox"""
        message.counter = self.counter
        self.socket.send(message.tobytes())
        self.counter += 1

    def addListener(self, deviceId, callback):
        """Add a callback to each message received from bigbox with corresponding deviceId"""
        self.listeners.append({'id': deviceId, 'callback': callback})
    
    def startReading(self):
        """Start a thread to continuously read message from bigbox"""
        self.reading = True
        self.thread = ReadSocket(self)
        self.thread.start()
    
    def stopReading(self):
        """"Stop the thread reading messages from bigbox"""
        self.reading = False
    
class ReadSocket(Thread):
    """Thread class for reading message from bigbox"""
    def __init__(self, device):
        Thread.__init__(self)
        self.device = device
        

    def run(self):
        while self.device.reading:
            try:
                sMessage = self.device.socket.recv(2048)
            except socket.timeout:
                print("Can't read bigbox (Wrong ip or bigbox is off)")
                self.device.reading = False
                continue 
            except ConnectionResetError:
                print("Can't read bigbox (Wrong port)")
                self.device.reading = False
                continue

            if sMessage == b'Hello, client number: ' or len(sMessage) < 8:
                continue
            message = Message(fromBytes= sMessage)
            
            for listener in self.device.listeners:
                if message.deviceId == listener['id']:
                    listener['callback'](message)
