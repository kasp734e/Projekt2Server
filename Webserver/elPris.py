import json
import urllib.request

def fetchPrice(date):
    """Benytter sig af elprisenligenu.dk til at skaffen dagens elpris, retunerer et stort JSON objekt"""
    monthStr = f"{date.month:02d}" # Det er nødvendigt at runde dag og måned af fordi ellers bliver apien sur.
    dayStr = f"{date.day:02d}"
    formatted_date = f"{date.year}/{monthStr}-{dayStr}" # Formaterer en string til formatet APIen kræver
    url = f"https://www.elprisenligenu.dk/api/v1/prices/{formatted_date}_DK2.json" # Definerer url til APIen
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    )
    response = urllib.request.urlopen(req) # Sender en request til url og skaffer JSON
    data = json.loads(response.read().decode()) # Loader JSON fra APIen til en python variabel så vi kan arbejde med det
    return data