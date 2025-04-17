import csv
import json
import time
import os
import logging
from typing import Dict, List, Optional, Tuple

import ee
import numpy as np

from data_processing import calculate_sustainability_index, extract_features
from earth_engine_utils import get_city_geometry, get_satellite_images
from visualization import plot_sustainability_index, create_interactive_map
from data_preparation import prepare_data
from sustainability_nn_model import train_sustainability_model

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do projeto
CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']
GEOJSON_FILE = "municipios_filtrados.geojson"
START_DATE = '2023-01-01'
END_DATE = '2025-03-08'

DADOS_ADICIONAIS = {
    'São Paulo': {'IDH': 0.805, 'Área Verde (m²/hab)': 15, 'Temperatura Média (°C)': 22.5},
    'Rio de Janeiro': {'IDH': 0.799, 'Área Verde (m²/hab)': 12, 'Temperatura Média (°C)': 24.2},
    'Belo Horizonte': {'IDH': 0.810, 'Área Verde (m²/hab)': 18, 'Temperatura Média (°C)': 21.8},
    'Brasília': {'IDH': 0.824, 'Área Verde (m²/hab)': 25, 'Temperatura Média (°C)': 23.4},
    'Salvador': {'IDH': 0.759, 'Área Verde (m²/hab)': 10, 'Temperatura Média (°C)': 26.3}
}

def validate_city_data(city: str, coordenadas: Dict) -> bool:
    required = ['IDH', 'Área Verde (m²/hab)', 'Temperatura Média (°C)']
    return (city in coordenadas and 
            None not in coordenadas[city] and
            all(key in DADOS_ADICIONAIS[city] for key in required))

def input_coordinates() -> Dict[str, Tuple[float, float]]:
    defaults = {
        "São Paulo": (-23.55052, -46.633308),
        "Rio de Janeiro": (-22.9068, -43.1729),
        "Belo Horizonte": (-19.8157, -43.9542),
        "Salvador": (-12.9714, -38.5014)
    }
    coords = {}
    print("Pressione Enter para manter o valor padrão.\n")
    for city, (lat0, lon0) in defaults.items():
        try:
            lat = input(f"{city} latitude [{lat0}]: ").strip() or lat0
            lon = input(f"{city} longitude [{lon0}]: ").strip() or lon0
            coords[city] = (float(lat), float(lon))
        except ValueError:
            logger.warning(f"Valor inválido para {city}, mantendo padrão.")
            coords[city] = (lat0, lon0)
    return coords

def export_results_to_csv(resultados, coordenadas, filename="dados_cidades_ajustado.csv"):
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Cidade", "Índice de Sustentabilidade", "Latitude", "Longitude", "IDH", "Área Verde (m²/hab)", "Temperatura Média (°C)"])
            for city in resultados:
                idx = resultados[city]
                lat, lon = coordenadas.get(city, (None, None))
                add = DADOS_ADICIONAIS.get(city, {"IDH": "N/A", "Área Verde (m²/hab)": "N/A", "Temperatura Média (°C)": "N/A"})
                writer.writerow([
                    city, f"{idx:.2f}" if idx else "N/A",
                    lat if lat else "N/A", lon if lon else "N/A",
                    add['IDH'], add['Área Verde (m²/hab)'], add['Temperatura Média (°C)']
                ])
        logger.info(f"CSV salvo: {filename}")
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {e}")

def export_results_to_json(resultados, coordenadas, stats, filename="dados_cidades_ajustado.json"):
    try:
        payload = {
            "resultados": resultados,
            "coordenadas": coordenadas,
            "estatisticas": stats,
            "dados_adicionais": DADOS_ADICIONAIS,
            "metadata": {"data_processamento": time.strftime("%Y-%m-%d %H:%M:%S"), "versao": "1.0"}
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"JSON salvo: {filename}")
    except Exception as e:
        logger.error(f"Erro ao exportar JSON: {e}")

def calculate_statistics(resultados):
    vals = [v for v in resultados.values() if v is not None]
    if not vals:
        logger.warning("Nenhum dado válido.")
        return {}
    stats = {
        "Média": float(np.mean(vals)),
        "Mediana": float(np.median(vals)),
        "Desvio Padrão": float(np.std(vals)),
        "Máximo": float(max(vals)),
        "Mínimo": float(min(vals)),
        "Número de Cidades": len(vals)
    }
    logger.info("Estatísticas: " + ", ".join(f"{k}: {v:.2f}" for k, v in stats.items()))
    return stats

def process_city(city, coordenadas):
    try:
        logger.info(f"Processando {city}...")
        if not validate_city_data(city, coordenadas):
            logger.warning(f"Dados incompletos para {city}, pulando.")
            return None
        geom = get_city_geometry(city)
        img = get_satellite_images(geom, START_DATE, END_DATE)
        feats = extract_features(img, geom)
        if feats is None or any(v is None for v in feats.values()):
            logger.warning(f"Features incompletas para {city}.")
            return None
        indice = calculate_sustainability_index(feats, geom)
        return indice
    except Exception as e:
        logger.error(f"Erro ao processar {city}: {e}")
        return None

def process_cities(cidades, coordenadas):
    return {city: process_city(city, coordenadas) for city in cidades}

def calculate_adjusted_indices(resultados_brutos, model, scaler):
    peso_idh = 0.1
    resultados_ajustados = {}
    for city in CIDADES_ALVO:
        if resultados_brutos[city] is None:
            resultados_ajustados[city] = None
            continue
        try:
            x = np.array([[DADOS_ADICIONAIS[city]['IDH'], DADOS_ADICIONAIS[city]['Área Verde (m²/hab)'], DADOS_ADICIONAIS[city]['Temperatura Média (°C)']]])
            x_scaled = scaler.transform(x)
            pred = float(model.predict(x_scaled, verbose=0)[0])
            resultados_ajustados[city] = pred * (1 + peso_idh * (DADOS_ADICIONAIS[city]['IDH'] - 0.5))
        except Exception as e:
            logger.error(f"Erro no ajuste para {city}: {e}")
            resultados_ajustados[city] = None
    return resultados_ajustados

def main():
    logger.info("Iniciando análise de sustentabilidade urbana.")
    
    if not os.path.exists(GEOJSON_FILE):
        logger.info("Preparando dados geoespaciais...")
        prepare_data()

    ee.Authenticate()
    ee.Initialize(project='ee-shiryucode')

    coordenadas = input_coordinates()
    resultados_brutos = process_cities(CIDADES_ALVO, coordenadas)

    stats = calculate_statistics(resultados_brutos)
    export_results_to_csv(resultados_brutos, coordenadas)
    export_results_to_json(resultados_brutos, coordenadas, stats)

    model, scaler = train_sustainability_model()
    resultados_ajustados = calculate_adjusted_indices(resultados_brutos, model, scaler)

    stats_aj = calculate_statistics(resultados_ajustados)
    plot_sustainability_index(resultados_ajustados)

    resultados_validos = {k: v for k, v in resultados_ajustados.items() if v is not None}
    if resultados_validos:
        mapa = create_interactive_map(coordenadas, resultados_validos)
        mapa.save("mapa_sustentabilidade.html")
        logger.info("Mapa salvo: mapa_sustentabilidade.html")
    else:
        logger.warning("Nenhum resultado válido para gerar o mapa.")

    export_results_to_csv(resultados_ajustados, coordenadas, filename="dados_cidades_ajustado_final.csv")
    export_results_to_json(resultados_ajustados, coordenadas, stats_aj, filename="dados_cidades_ajustado_final.json")

    logger.info("Processo concluído com sucesso!")

if __name__ == "__main__":
    main()
