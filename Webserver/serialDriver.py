import serial
import time

class SerialDriver:
    """A serial port driver for communicating with devices on /dev/tty.usbmodem1101"""
    
    def __init__(self, baudrate=9600, timeout=1, port="/dev/ttyACM0"):
        """Initialize the serial driver with the specified parameters"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.is_connected = False
    
    def connect(self):
        """Connect to the serial port"""
        if self.is_connected:
            return True
            
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.is_connected = True
            return True
        except serial.SerialException as e:
            print(f"Error connecting to port {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close the serial connection"""
        if self.is_connected and self.ser:
            self.ser.close()
            self.is_connected = False
    
    def readData(self):
        """Read available data from the serial port"""
        if not self.is_connected or not self.ser:
            return None
            
        if self.ser.in_waiting > 0:
            data = self.ser.read(self.ser.in_waiting).decode('ascii', errors='ignore')
            return data
        return None
    
    def writeData(self, data):
        """Write data to the serial port"""
        if not self.is_connected or not self.ser:
            return False
            
        try:
            self.ser.write(data.encode('ascii'))
            return True
        except Exception as e:
            print(f"Error writing to serial port: {e}")
            return False
    
    def monitor(self, callback=None, interval=0.1):
        """
        Continuously monitor the serial port
        
        Args:
            callback: Function that processes received data
            interval: Time between checks in seconds
        """
        if not self.connect():
            return
            
        try:
            while True:
                data = self.readData()
                if data:
                    if callback:
                        callback(data)
                    else:
                        print(f"Received: {data}")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping serial monitor.")
        finally:
            self.disconnect()
    
    def readWithTimeout(self, duration=1.0):
        """Read data from serial port for a specified duration and return as integer.
        
        Args:
            duration (float): Time in seconds to wait for data
            
        Returns:
            int: The parsed integer value from serial, or 0 if invalid/empty
        """
        if not self.is_connected or not self.ser:
            return 0
            
        start_time = time.time()
        data = ""
        
        while (time.time() - start_time) < duration:
            new_data = self.readData()
            if new_data:
                data = new_data  # Keep the latest response
            time.sleep(0.1)  # Short pause between reads
        
        # Convert to float instead of integer
        try:
            value = float(data.strip())
            # Optionally keep as int if it's a whole number
            if value.is_integer():
                return int(value)
            return value
        except:
            return 0