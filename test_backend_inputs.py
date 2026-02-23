import requests
import json

url = "http://localhost:8000/simulate"

payload = {
    "region": "Bretagne",
    "filiere": "Bovins Lait",
    "sau": 100.0,
    "umo": 2.5,
    "ugb": 120.0,
    "nb_vl": 90,
    "surface_sfp": 80.0,
    "surface_herbe_pp": 40.0,
    "surface_herbe_pt": 20.0,
    "surface_culture": 20.0,
    "part_herbe": 75.0,
    "part_mais": 25.0,
    "conso_fioul": 15000.0,
    "conso_elec": 8000.0
}

try:
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Success! Backend accepted the new input format.")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Connection failed: {e}")
