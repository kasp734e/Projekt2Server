import json
import urllib.request
import datetime

def fetchPrice(date):
    """Returns a list of the power price for the current day in DKK"""
    monthStr = f"{date.month:02d}"  # Format month and day to ensure API compatibility
    dayStr = f"{date.day:02d}"
    formattedDate = f"{date.year}/{monthStr}-{dayStr}"  # Format the date string for the API
    url = f"https://www.elprisenligenu.dk/api/v1/prices/{formattedDate}_DK2.json"  # Define the API URL
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req) as response:
        priceJsonPy = json.load(response)  # Load JSON from the API into a Python variable

    # Get and round the power prices
    return [round(d["DKK_per_kWh"], 2) for d in priceJsonPy if "DKK_per_kWh" in d]