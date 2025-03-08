from earth_engine_utils import initialize_ee, get_city_geometry, get_satellite_images, extract_features
from data_processing import calculate_sustainability_index
from visualization import plot_sustainability_index, create_interactive_map
import os
import csv
import json

# Configurações do projeto
CIDADES_ALVO = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador']
GEOJSON_FILE = "municipios_filtrados.geojson"
START_DATE = '2024-01-01'  # Atualizado para refletir o ano atual
END_DATE = '2025-03-08'    # Data atual


# Dados adicionais (exemplo)
DADOS_ADICIONAIS = {
    'São Paulo': {'IDH': 0.805, 'Área Verde (m²/hab)': 15, 'Temperatura Média (°C)': 22.5},
    'Rio de Janeiro': {'IDH': 0.799, 'Área Verde (m²/hab)': 12, 'Temperatura Média (°C)': 24.2},
    'Belo Horizonte': {'IDH': 0.810, 'Área Verde (m²/hab)': 18, 'Temperatura Média (°C)': 21.8},
    'Brasília': {'IDH': 0.824, 'Área Verde (m²/hab)': 25, 'Temperatura Média (°C)': 23.4},
    'Salvador': {'IDH': 0.759, 'Área Verde (m²/hab)': 10, 'Temperatura Média (°C)': 26.3}
}

def export_results_to_csv(resultados, coordenadas, filename="resultados_sustentabilidade.csv"):
    """
    Exporta os resultados para um arquivo CSV.
    
    Parâmetros:
        resultados (dict): Dicionário com os índices de sustentabilidade por cidade.
        coordenadas (dict): Dicionário com as coordenadas das cidades.
        filename (str): Nome do arquivo CSV gerado.
    """
    try:
        with open(filename, mode='w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Cidade", "Índice de Sustentabilidade", "Latitude", "Longitude", 
                             "IDH", "Área Verde (m²/hab)", "Temperatura Média (°C)"])
            for cidade, indice in resultados.items():
                latitude, longitude = coordenadas.get(cidade, (None, None))
                idh = DADOS_ADICIONAIS[cidade]['IDH']
                area_verde = DADOS_ADICIONAIS[cidade]['Área Verde (m²/hab)']
                temperatura = DADOS_ADICIONAIS[cidade]['Temperatura Média (°C)']
                writer.writerow([cidade, f"{indice:.2f}" if indice else "N/A", latitude, longitude,
                                 idh, area_verde, temperatura])
        print(f"\nResultados exportados para {filename}")
    except Exception as e:
        print(f"Erro ao exportar resultados para CSV: {str(e)}")


def export_results_to_json(resultados, coordenadas, stats, filename="resultados_sustentabilidade.json"):
    """
    Exporta os resultados e estatísticas para um arquivo JSON.
    
    Parâmetros:
        resultados (dict): Dicionário com os índices de sustentabilidade por cidade.
        coordenadas (dict): Dicionário com as coordenadas das cidades.
        stats (dict): Estatísticas calculadas dos índices.
        filename (str): Nome do arquivo JSON gerado.
    """
    try:
        data = {
            "resultados": resultados,
            "coordenadas": coordenadas,
            "estatisticas": stats,
            "dados_adicionais": DADOS_ADICIONAIS
        }
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
        print(f"\nResultados exportados para {filename}")
    except Exception as e:
        print(f"Erro ao exportar resultados para JSON: {str(e)}")

def calculate_statistics(resultados):
    """
    Calcula estatísticas detalhadas dos índices de sustentabilidade.
    
    Parâmetros:
        resultados (dict): Dicionário com os índices de sustentabilidade por cidade.
    
    Retorna:
        dict: Estatísticas calculadas (média, mediana, desvio padrão, máximo e mínimo).
    """
    try:
        valores = [indice for indice in resultados.values() if indice is not None]
        
        if not valores:
            return {}
        
        stats = {
            "Média": sum(valores) / len(valores),
            "Mediana": sorted(valores)[len(valores) // 2],
            "Desvio Padrão": (sum((x - sum(valores) / len(valores))**2 for x in valores) / len(valores))**0.5,
            "Máximo": max(valores),
            "Mínimo": min(valores)
        }
        
        print("\nEstatísticas Calculadas:")
        for chave, valor in stats.items():
            print(f"{chave}: {valor:.2f}")
        
        return stats
    
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {str(e)}")
        return {}

def main():
    """
    Função principal que executa o processamento das cidades alvo.
    """
    # Verifica se o arquivo GeoJSON existe
    if not os.path.exists(GEOJSON_FILE):
        from data_preparation import prepare_data
        prepare_data()

    # Inicializa o Google Earth Engine
    initialize_ee(project_id='ee-shiryucode')

    resultados = {}
    coordenadas = {}

    for cidade in CIDADES_ALVO:
        try:
            print(f"\nProcessando: {cidade}")
            
            # Obtém a geometria da cidade
            geometry = get_city_geometry(cidade)
            
            # Obtém imagens de satélite filtradas por data e cobertura de nuvens
            imagem = get_satellite_images(
                geometry=geometry,
                start_date=START_DATE,
                end_date=END_DATE
            )
            
            # Extrai NDVI e NDBI das imagens
            features = extract_features(imagem)
            
            # Calcula o índice de sustentabilidade
            indice = calculate_sustainability_index(features, geometry)
            resultados[cidade] = indice
            
            # Obtém as coordenadas da cidade
            coords = geometry.coordinates().getInfo()
            coordenadas[cidade] = (coords[1], coords[0])  # Latitude e Longitude

        except Exception as e:
            print(f"Erro em {cidade}: {str(e)}")
            resultados[cidade] = None

    if resultados:
        print("\nResultados finais:")
        for cidade, indice in resultados.items():
            print(f"{cidade}: {indice:.2f}" if indice else f"{cidade}: N/A")

        # Calcula estatísticas detalhadas dos índices
        stats = calculate_statistics(resultados)

        # Gera gráfico de sustentabilidade
        plot_sustainability_index(resultados)
        
        # Cria mapa interativo com os resultados
        mapa = create_interactive_map(coordenadas, resultados)
        mapa.save("mapa_sustentabilidade.html")
        print("\nMapa interativo gerado com sucesso!")

        # Exporta os resultados para CSV e JSON
        export_results_to_csv(resultados, coordenadas)
        export_results_to_json(resultados, coordenadas, stats)

if __name__ == "__main__":
    main()
