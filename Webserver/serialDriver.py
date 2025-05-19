import serial
import time

class SerialDriver:
    """A serial port driver for communicating with devices"""
    
    def __init__(self, baudrate=9600, timeout=1, port="/dev/ttyACM0"):
        """Initialize the serial driver with the specified parameters"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.isConnected = False
    
    def connect(self):
        """Connect to the serial port"""
        if self.isConnected:
            return True
            
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.isConnected = True
            return True
        except serial.SerialException as e:
            print(f"Error connecting to port {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close the serial connection"""
        if self.isConnected and self.ser:
            self.ser.close()
            self.isConnected = False
    
    def readData(self):
        """Read available data from the serial port"""
        if not self.isConnected or not self.ser:
            return None
            
        if self.ser.in_waiting > 0:
            data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
            return data
        return None
    
    def writeData(self, data):
        """Write data to the serial port"""
        if not self.isConnected or not self.ser:
            return False
            
        try:
            self.ser.write(data.encode('ascii'))
            return True
        except Exception as e:
            print(f"Error writing to serial port: {e}")
            return False
    
    def readWithTimeout(self, duration=1.0):
        """Read data from serial port for a specified duration 
        duration (float): Time in seconds to wait for data"""
        if not self.isConnected or not self.ser:
            return 0
            
        startTime = time.time()
        data = ""
        
        while (time.time() - startTime) < duration:
            newData = self.readData()
            if newData:
                data = newData  # Keep the latest response
            time.sleep(0.1)  # Short pause between reads
        try:
            value = float(data.strip())
            return value
        except:
            return 0