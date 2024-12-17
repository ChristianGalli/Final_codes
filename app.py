from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Questo abilita CORS per tutte le rotte

# URL dell'API del middleware
API_URL = "http://localhost:8000/api/"

# Funzione per ottenere i dati del supermercato
def get_supermarkets():
    try:
        response = requests.get(API_URL + "supermarkets")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Funzione per ottenere le location di un supermercato
def get_locations(supermarket_id):
    try:
        response = requests.get(API_URL + f"supermarkets/locations/{supermarket_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Funzione per ottenere i fridges di una location
def get_fridges(supermarket_id, location_id):
    try:
        response = requests.get(API_URL + f"supermarkets/locations/{supermarket_id}/fridges/{location_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Funzione per ottenere i dati di un frigorifero
def get_fridge_data(supermarket_id, location_id, fridge_id):
    try:
        response = requests.get(API_URL + f"supermarkets/locations/{supermarket_id}/fridges/{location_id}/{fridge_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Prima schermata: Selezione del supermercato
@app.route('/')
def index():
    supermarkets = get_supermarkets()
    if "error" in supermarkets:
        return render_template('error.html', error=supermarkets["error"])
    return render_template('index.html', supermarkets=supermarkets)

# Seconda schermata: Selezione della location nel supermercato
@app.route('/supermarket/<supermarket_id>')
def supermarket(supermarket_id):
    locations = get_locations(supermarket_id)
    if "error" in locations:
        return render_template('error.html', error=locations["error"])
    return render_template('locations.html', supermarket_id=supermarket_id, locations=locations)

# Terza schermata: Selezione del frigorifero nella location
@app.route('/supermarket/<supermarket_id>/location/<location_id>')
def location(supermarket_id, location_id):
    fridges = get_fridges(supermarket_id, location_id)
    if "error" in fridges:
        return render_template('error.html', error=fridges["error"])
    return render_template('fridges.html', supermarket_id=supermarket_id, location_id=location_id, fridges=fridges)

# Quarta schermata: Dati del frigorifero selezionato
@app.route('/supermarket/<supermarket_id>/location/<location_id>/fridge/<fridge_id>')
def fridge(supermarket_id, location_id, fridge_id):
    fridge_data = get_fridge_data(supermarket_id, location_id, fridge_id)
    if "error" in fridge_data:
        return render_template('error.html', error=fridge_data["error"])
    return render_template('fridge_data.html', supermarket_id=supermarket_id, location_id=location_id, fridge_id=fridge_id, fridge_data=fridge_data)

@app.route('/api/<supermarket_id>/<location_id>/<fridge_id>')
def fetch_fridge_data(supermarket_id, location_id, fridge_id):
    fridge_data = get_fridge_data(supermarket_id, location_id, fridge_id)
    return fridge_data

if __name__ == '__main__':
    app.run(debug=True)
