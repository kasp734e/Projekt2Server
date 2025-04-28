import datetime
import elPris

#class dataObject:
#    def __init__(self, data = 0, time = dateTimeObject):
        
class powerPrice:
    """Bruger elPris til at skaffe dagens elpriser hvilket klassen kører igennem noget logik der gør sådan at man kan få en list af priserne i DKK afrudnet til 0,01 med getList()"""
    def __init__(self):
        now = datetime.datetime.now()
        self.priceJsonPy = elPris.fetchPrice(now.date())

        # Removes irrelevant data from the json
        # Dette er nok ikke nødvendigt for at getList() duer men det gør printjson() mere læsbart
        keysToDelete = ["EXR", "EUR_per_kWh"]
        for key in keysToDelete:
            for d in self.priceJsonPy:
                if key in d:
                    del d[key]
            for d in self.priceJsonPy:
                if key in d:
                    del d[key]

        # Turns the data into a workable array
        self.dkkPerKWhVals = [d["DKK_per_kWh"] for d in self.priceJsonPy if "DKK_per_kWh" in d]
        self.dkkPerKWhVals = [round(value, 2) for value in self.dkkPerKWhVals]

    def printjson(self):
        """Prints the JSON from the API to the python terminal. Cleaned up a little"""
        print(self.priceJsonPy)
    
    def printPythonArray(self):
        """Prints the list of power prices in DKK for the current day to the python terminal"""
        print(self.dkkPerKWhVals)
    
    def getList(self):
        """Returns a list of the power price for the current day in DKK"""
        return self.dkkPerKWhVals
