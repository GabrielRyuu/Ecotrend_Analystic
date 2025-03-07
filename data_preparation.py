import requests
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Lista das cidades que queremos processar
CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']

def get_coordinates(city_name):
    """Obtém coordenadas usando Nominatim apenas para nossas cidades alvo"""
    geolocator = Nominatim(user_agent="eco_project")
    
    try:
        # Busca específica para cidades brasileiras
        location = geolocator.geocode(f"{city_name}, Brasil", exactly_one=True)
        if location:
            return [location.longitude, location.latitude]
        return [0, 0]  # Fallback para cidades não encontradas
    except GeocoderTimedOut:
        time.sleep(1)
        return get_coordinates(city_name)  # Retry

def save_filtered_data(filename="municipios_filtrados.geojson"):
    """Processa apenas as cidades selecionadas"""
    features = []
    
    for cidade in CIDADES_ALVO:
        coords = get_coordinates(cidade)
        feature = {
            "type": "Feature",
            "properties": {"name": cidade},
            "geometry": {
                "type": "Point",
                "coordinates": coords
            }
        }
        features.append(feature)
        time.sleep(1)  # Respeita o limite da API
        print(f"Processado: {cidade}")

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": features
        }, f, ensure_ascii=False, indent=2)

def prepare_data():
    """Prepara apenas os dados necessários"""
    print("Iniciando geocodificação das 5 cidades...")
    save_filtered_data()
    print("Dados filtrados salvos com sucesso!")

if __name__ == "__main__":
    prepare_data()
