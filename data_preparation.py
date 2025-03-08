import requests
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
import time
from unidecode import unidecode
import csv

# Lista das cidades alvo para análise
CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']

def normalize_city_name(city_name):
    """
    Normaliza o nome da cidade removendo acentos e caracteres especiais.
    
    Parâmetros:
        city_name (str): Nome da cidade.
    
    Retorna:
        str: Nome normalizado.
    """
    return unidecode(city_name.strip().lower())

def get_coordinates(city_name, retries=3, wait_time=2):
    """
    Obtém as coordenadas (longitude, latitude) de uma cidade usando a API do Nominatim.
    
    Parâmetros:
        city_name (str): Nome da cidade.
        retries (int): Número máximo de tentativas em caso de falha (padrão: 3).
        wait_time (int): Tempo de espera entre as tentativas em segundos (padrão: 2).
    
    Retorna:
        list: Coordenadas [longitude, latitude] ou [0, 0] se não encontradas.
    """
    geolocator = Nominatim(user_agent="eco_project")
    
    for attempt in range(retries):
        try:
            location = geolocator.geocode(f"{city_name}, Brasil", exactly_one=True)
            if location:
                return [location.longitude, location.latitude]
            print(f"Coordenadas não encontradas para {city_name}. Tentativa {attempt + 1}/{retries}.")
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Erro ao buscar coordenadas para {city_name}: {e}. Tentativa {attempt + 1}/{retries}.")
            time.sleep(wait_time)  # Aguarda antes de tentar novamente
    
    print(f"Falha ao obter coordenadas para {city_name} após {retries} tentativas.")
    return [0, 0]

def save_filtered_data(cidades=CIDADES_ALVO, filename_geojson="municipios_filtrados.geojson", filename_csv="municipios_filtrados.csv"):
    """
    Gera arquivos GeoJSON e CSV contendo as coordenadas das cidades alvo.
    
    Parâmetros:
        cidades (list): Lista das cidades a serem processadas.
        filename_geojson (str): Nome do arquivo GeoJSON gerado.
        filename_csv (str): Nome do arquivo CSV gerado.
    """
    features = []
    csv_data = []

    # Remove duplicatas na lista de cidades
    cidades_unicas = list(set(cidades))
    
    for cidade in cidades_unicas:
        coords = get_coordinates(cidade)
        
        # Ignora cidades com coordenadas zeradas
        if coords == [0, 0]:
            print(f"Coordenadas inválidas ignoradas para {cidade}.")
            continue
        
        feature = {
            "type": "Feature",
            "properties": {"name": cidade},
            "geometry": {
                "type": "Point",
                "coordinates": coords
            }
        }
        features.append(feature)
        
        # Adiciona os dados ao CSV
        csv_data.append({"Cidade": cidade, "Longitude": coords[0], "Latitude": coords[1]})
        
        time.sleep(1)  # Evita sobrecarregar a API
        print(f"Processado: {cidade} | Coordenadas: {coords}")

    # Salva o arquivo GeoJSON
    with open(filename_geojson, 'w', encoding='utf-8') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": features
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Arquivo GeoJSON salvo como {filename_geojson}.")

    # Salva o arquivo CSV
    with open(filename_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Cidade", "Longitude", "Latitude"])
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"Arquivo CSV salvo como {filename_csv}.")

def prepare_data(cidades=CIDADES_ALVO, filename_geojson="municipios_filtrados.geojson", filename_csv="municipios_filtrados.csv"):
    """
    Prepara os dados das cidades alvo e salva em arquivos GeoJSON e CSV.
    
    Parâmetros:
        cidades (list): Lista das cidades a serem processadas.
        filename_geojson (str): Nome do arquivo GeoJSON gerado.
        filename_csv (str): Nome do arquivo CSV gerado.
    """
    print("Iniciando geocodificação das cidades...")
    save_filtered_data(cidades=cidades, filename_geojson=filename_geojson, filename_csv=filename_csv)
    print("Dados filtrados salvos com sucesso!")

if __name__ == "__main__":
    prepare_data()
