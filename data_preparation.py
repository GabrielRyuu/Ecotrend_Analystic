import requests
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from unidecode import unidecode
import csv
import ee



CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Salvador']




def normalize_city_name(city_name):
    """Normaliza nomes de cidades para comparação."""
    return unidecode(city_name.strip().lower())

def get_coordinates(city_name, retries=3, wait_time=2):
    """Obtém coordenadas usando Nominatim com tratamento de erros."""
    geolocator = Nominatim(user_agent="eco_project")
    
    for attempt in range(retries):
        try:
            location = geolocator.geocode(f"{city_name}, Brasil", exactly_one=True)
            if location:
                return [location.latitude, location.longitude]  # Padronizado como [lat, lon]
            print(f"Coordenadas não encontradas para {city_name}. Tentativa {attempt + 1}/{retries}.")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Erro ao buscar coordenadas para {city_name}: {e}. Tentativa {attempt + 1}/{retries}.")
            time.sleep(wait_time)
    return None

def save_adjusted_data(cidades=CIDADES_ALVO):
    """Salva dados no formato GeoJSON e CSV."""
    features = []
    csv_data = []
    
    for cidade in cidades:
        coords = get_coordinates(cidade)
        if not coords:
            print(f"Falha ao obter coordenadas para {cidade}")
            continue
            
        features.append({
            "type": "Feature",
            "properties": {"name": cidade},
            "geometry": {
                "type": "Point",
                "coordinates": [coords[1], coords[0]]  # GeoJSON usa [lon, lat]
            }
        })
        
        csv_data.append({
            "Cidade": cidade,
            "Latitude": coords[0],
            "Longitude": coords[1]
        })
        
        time.sleep(1)  # Respeitar limites da API
    
    # Salva GeoJSON
    with open("municipios_filtrados.geojson", "w", encoding='utf-8') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": features
        }, f, ensure_ascii=False, indent=2)
    
    # Salva CSV
    with open("dados_cidades_ajustado.csv", "w", encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Cidade", "Latitude", "Longitude"])
        writer.writeheader()
        writer.writerows(csv_data)

def prepare_data():
    """Prepara os dados iniciais para análise."""
    print("Preparando dados...")
    save_adjusted_data()
    print("Dados preparados com sucesso!")

if __name__ == "__main__":
    prepare_data()
