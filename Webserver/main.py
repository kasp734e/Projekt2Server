import dataObject
from flask import Flask, render_template

power = dataObject.powerPrice()

app = Flask(__name__)
@app.route("/")
def solcelleApp(): 
    # Denne funktion kører når siden bliver loaded. 
    # Hvad denne funktion returnerer er det der bliver sendt til klienten (browseren)
    power_data = power.getList()
    return render_template('index.html', power_data=power_data) # Pass variables here for the html/js to use

@app.before_request
def beforeEveryRequest():
    # Denne kode kører hver gang siden bliver loaded
    print("Page is being reloaded")

# Denne kode gør sådan at serveren kan tilgås på netværket med maskinenes ip efterfulgt af porten 8080
app.run(host='0.0.0.0', port=8080, debug=True)