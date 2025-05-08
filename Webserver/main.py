import datetime
import dataObject
from flask import Flask, jsonify, render_template
import serialDriver
import time
import json


power = dataObject.powerPrice()

arduinoData = {
    'powerPrice': [],
    'uv': 0,
    'airQuality': 0,
    'power': 0,
    'temperature': 0
}

def saveArduinoDataToDisk():
    dataToSave = arduinoData.copy()
    dataToSave["time"] = datetime.datetime.now().isoformat()
    
    with open("data.json", "a") as file:
        file.write("\n \n")
        file.write(json.dumps(dataToSave, indent=4))

def getDataFromArduino():
    s = serialDriver.SerialDriver(baudrate=9600, timeout=1, port="/dev/ttyACM0")
    if s.connect():
        s.writeData("u")
        uvValue = s.readWithTimeout(1.0)

        s.writeData("a")
        airValue = s.readWithTimeout(1.0)

        s.writeData("p")
        powerValue = s.readWithTimeout(1.0)

        s.writeData("t")
        tempValue = s.readWithTimeout(1.0)

        s.disconnect()

        return {
            'powerPrice': power.getList(),
            'uv': uvValue,
            'airQuality': airValue,
            'power': powerValue,
            'temperature': tempValue
        }
    else:
        return {
            'powerPrice': power.getList(),
            'uv': 0,
            'airQuality': 0,
            'power': 0,
            'temperature': 0
        }

app = Flask(__name__)
@app.route("/")
def solcelleApp(): 
    # Denne funktion kører når siden bliver loaded. 
    # Hvad denne funktion returnerer er det der bliver sendt til klienten (browseren)
    return render_template('index.html')

@app.route("/api/update")
def updateData():
    global arduinoData
    arduinoData = getDataFromArduino()
    saveArduinoDataToDisk()
    return jsonify({"status": "updated"})

@app.route("/api/data")
def getData():
    if arduinoData is None:
        return jsonify({
            'powerPrice': power.getList(),
            'uv': 0,
            'airQuality': 0,
            'power': 0,
            'temperature': 0
        })
    return jsonify(arduinoData)

# Denne kode gør sådan at serveren kan tilgås på netværket med maskinenes ip efterfulgt af porten 8080
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)