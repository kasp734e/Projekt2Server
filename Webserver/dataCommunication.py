import json
import serialDriver
import datetime
import elPris
import time

def saveArduinoDataToDisk(dataList):
    existingData = []
    try:
        with open("data.json", "r") as file:
            existingData = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existingData = []

    existingTimestamps = set()
    for i in existingData:
        if i.get('time'):
            existingTimestamps.add(i.get('time')) 

    for i in dataList:
        if i.get('time') not in existingTimestamps:
            existingData.append(i)
            existingTimestamps.add(i['time'])

    with open("data.json", "w") as file:
        json.dump(existingData, file, indent=4, ensure_ascii=False)

def getDataFromArduino():
    s = serialDriver.SerialDriver(baudrate=9600, timeout=2, port="/dev/tty.usbmodem1101")
    if s.connect():
        s.writeData("a")
        airValue = s.readWithTimeout(1.0)
        time.sleep(0.1)
        print(f"Raw Air Quality Value: {airValue}") 

        s.writeData("p")
        powerValue = s.readWithTimeout(1.0)
        time.sleep(0.1)
        print(f"Raw Power Value: {powerValue}")  

        s.writeData("t")
        airTempValue = s.readWithTimeout(1.0)
        time.sleep(0.1)
        print(f"Raw Air Temperature Value: {airTempValue}")  

        s.disconnect()

        return {
            'time': datetime.datetime.now().isoformat(timespec='seconds'),
            'powerPrice': elPris.fetchPrice(datetime.datetime.now().date()),
            'airQuality': airValue,
            'power': powerValue,
            'airTemp': airTempValue
        }
    else:
        return {
            'time': datetime.datetime.now().isoformat(timespec='seconds'),
            'powerPrice': elPris.fetchPrice(datetime.datetime.now().date()),
            'airQuality': 404,
            'power': 404,
            'airTemp': 404
        }
