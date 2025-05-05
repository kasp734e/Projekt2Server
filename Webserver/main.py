import dataObject
from flask import Flask, jsonify, render_template
import serialDriver
import time

power = dataObject.powerPrice()

arduinoData = {
    'powerPrice': [],
    'uv': 0,
    'airQuality': 0,
    'power': 0,
    'temperature': 0
}

def getDataFromArduino():
        s = serialDriver.SerialDriver(baudrate=9600, timeout= 1, port="/dev/ttyACM0")
        if s.connect():
            s.writeData("u")
            time.sleep(0.5)
            uvValue = s.readData() or 0

            s.writeData("a")
            time.sleep(0.5)
            airValue = s.readData() or 0

            s.writeData("p")
            time.sleep(0.5)
            powerValue = s.readData() or 0

            s.writeData("t")
            time.sleep(0.5)
            tempValue = s.readData() or 0

            power_data = power.getList()
            s.disconnect()  # Close connection when done

        


app = Flask(__name__)
@app.route("/")
def solcelleApp(): 
    # Denne funktion kører når siden bliver loaded. 
    # Hvad denne funktion returnerer er det der bliver sendt til klienten (browseren)
    power_data = power.getList()
    return render_template('index.html', power_data=power_data) # Pass variables here for the html/js to use

@app.route("/api/update")
def updateData():
    getDataFromArduino()
    return jsonify({"status": "updated"})

@app.route("/api/data")
def getData():
    return jsonify(arduinoData)

# Denne kode gør sådan at serveren kan tilgås på netværket med maskinenes ip efterfulgt af porten 8080
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)