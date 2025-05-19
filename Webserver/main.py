from flask import Flask, jsonify, render_template, request
import json
from dataCommunication import getDataFromArduino, saveArduinoDataToDisk
import time
import threading


arduinoData = {
    'time': None,
    'powerPrice': [],
    'uv': 0,
    'airQuality': 0,
    'power': 0,
    'airTemp': 0,
    'touchTemp': 0
}
dataList = []

updateMins = 10
updateEvent = threading.Event()


app = Flask(__name__)
@app.route("/")
def solcelleApp(): 
    # Denne funktion kører når siden bliver loaded. 
    # Hvad denne funktion returnerer er det der bliver sendt til klienten (browseren)
    return render_template('index.html')

@app.route("/api/update")
def updateData():
    global dataList
    dataList.append(getDataFromArduino())
    saveArduinoDataToDisk(dataList)
    return jsonify({"status": "updated"})

@app.route("/api/getJSON")
def getJSON():
    """Fetches and returns the contents of data.json as JSON."""
    with open("data.json", "r") as file:
        data = json.load(file)
        return jsonify(data)

""" @app.route("/api/changeUpdateTime", methods=['POST'])
def changeUpdateTime():
    global updateMins
    newData = request.json

    if newData and "value" in newData:
        try:
            newTime = float(newData["value"])
            if newTime <= 0:
                return jsonify({"error": "Update time must be greater than 0"}), 400

            updateMins = newTime
            print(f'New update time is: {updateMins} minutes')
            return jsonify({"status": "success", "newUpdateTime": updateMins})
        except ValueError:
            return jsonify({"error": "Invalid value for 'value'. Must be a number."}), 400
    else:
        return jsonify({"error": "Invalid input"}), 400
 """

@app.route("/api/data")
def getData():
    try:
        with open("data.json", "r") as file:
            existingData = json.load(file)
            # Get the last 24 objects, filling with zeros if there aren't enough
            result = existingData[-24:]
            while len(result) < 24:
                result.insert(0, {
                    'time': None,
                    'powerPrice': [],
                    'uv': 0,
                    'airQuality': 0,
                    'power': 0,
                    'airTemp': 0,
                    'touchTemp': 0
                })
            return jsonify(result)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return 24 objects filled with zeros if there is an error
        return jsonify([{
            'time': None,
            'powerPrice': [],
            'uv': 0,
            'airQuality': 0,
            'power': 0,
            'airTemp': 0,
            'touchTemp': 0
        } for _ in range(24)])

def backgroundUpdateData():
    global updateMins
    while True:
        try:
            with app.app_context():
                updateData()
        except Exception as error:
            print(f"Error in backgroundUpdateData: {error}")
        
        time.sleep(updateMins * 60)

# Denne kode gør sådan at serveren kan tilgås på netværket med maskinenes ip efterfulgt af porten 8080
if __name__ == "__main__":
    updateMins = 10
    threading.Thread(target=backgroundUpdateData, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False)

